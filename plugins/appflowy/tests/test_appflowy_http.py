import importlib.util
import io
import json
import os
import stat
import sys
import tempfile
import unittest
from unittest import mock
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "scripts" / "appflowy_http.py"
SPEC = importlib.util.spec_from_file_location("appflowy_http", MODULE_PATH)
api = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
sys.modules[SPEC.name] = api
SPEC.loader.exec_module(api)


class FakeResponse:
    def __init__(self, status, body=b"", headers=None):
        self.status = status
        self.body = body
        self.headers = headers or {"Content-Type": "application/json"}

    def read(self):
        return self.body

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


class AppFlowyHttpTests(unittest.TestCase):
    def test_base_and_path_safety(self):
        self.assertEqual(api.validate_base_url("https://flow.example"), "https://flow.example")
        for bad in [
            "https://user:pass@flow.example", "https://flow.example/api",
            "file:///tmp/x", "http://flow.example",
        ]:
            with self.assertRaises(api.AppFlowyError):
                api.validate_base_url(bad)
        for bad in [
            "https://evil.example/api", "/api/../secret", "/other",
            "//evil/api", "/apiary", "/gotrueevil",
        ]:
            with self.assertRaises(api.AppFlowyError):
                api.validate_path(bad)

    def test_redaction_is_recursive(self):
        value = {"password": "x", "nested": [{"access_token": "y", "safe": 3}]}
        self.assertEqual(api.redact(value)["password"], "<redacted>")
        self.assertEqual(api.redact(value)["nested"][0]["access_token"], "<redacted>")
        self.assertEqual(api.redact(value)["nested"][0]["safe"], 3)
        self.assertEqual(api.redact([("refresh_token", "z")])[0][1], "<redacted>")

    def test_write_and_destructive_gates(self):
        env = {"APPFLOWY_BASE_URL": "https://flow.example"}
        with mock.patch.dict(os.environ, env, clear=True):
            err = io.StringIO()
            with redirect_stderr(err):
                self.assertEqual(api.main(["POST", "/api/workspace", "--dry-run"]), 2)
            self.assertIn("--execute-write", err.getvalue())
            err = io.StringIO()
            with redirect_stderr(err):
                self.assertEqual(api.main([
                    "DELETE", "/api/workspace/id", "--execute-write", "--dry-run"
                ]), 2)
            self.assertIn("--execute-destructive", err.getvalue())

    def test_dry_run_never_authenticates_and_redacts_body(self):
        env = {"APPFLOWY_BASE_URL": "https://flow.example"}
        output = io.StringIO()
        with mock.patch.dict(os.environ, env, clear=True), redirect_stdout(output):
            result = api.main([
                "POST", "/api/workspace", "--json",
                '{"name":"demo","password":"private"}',
                "--execute-write", "--dry-run",
            ])
        self.assertEqual(result, 0)
        self.assertNotIn("private", output.getvalue())
        self.assertIn("<redacted>", output.getvalue())

    def test_token_cache_is_atomic_and_private(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nested" / "token.json"
            store = api.TokenStore(path)
            store.save({"access_token": "test"})
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
            self.assertEqual(store.load()["access_token"], "test")
            path.chmod(0o644)
            with self.assertRaises(api.AppFlowyError):
                store.load()

    def test_401_refreshes_and_retries_once(self):
        with tempfile.TemporaryDirectory() as directory:
            store = api.TokenStore(Path(directory) / "token.json")
            store.save({"access_token": "old", "refresh_token": "refresh", "expires_at": 9999})
            calls = []
            responses = [
                FakeResponse(401, b'{"message":"expired"}'),
                FakeResponse(200, b'{"access_token":"new","refresh_token":"next","expires_in":3600}'),
                FakeResponse(200, b'{"code":0,"data":{"ok":true}}'),
            ]

            def opener(request, timeout):
                calls.append((request.full_url, request.headers.get("Authorization")))
                return responses.pop(0)

            client = api.AppFlowyClient(
                "https://flow.example", token_store=store, opener=opener,
                clock=lambda: 100, sleeper=lambda _: None,
            )
            response = client.request("GET", "/api/user/profile")
            self.assertEqual(response.status, 200)
            self.assertEqual(len(calls), 3)
            self.assertEqual(calls[-1][1], "Bearer new")

    def test_envelope_and_binary_handling(self):
        good = api.Response(200, {"Content-Type": "application/json"}, b'{"code":0,"data":1}')
        self.assertEqual(api.check_envelope(good)["data"], 1)
        binary = api.Response(200, {"Content-Type": "application/octet-stream"}, b"\x00\x01")
        self.assertIsNone(api.check_envelope(binary))
        bad = api.Response(200, {"Content-Type": "application/json"}, b'{"code":42,"message":"no"}')
        with self.assertRaises(api.AppFlowyError):
            api.check_envelope(bad)

    def test_retry_after_is_bounded(self):
        self.assertEqual(api.parse_retry_after({"Retry-After": "999"}), 30)
        self.assertEqual(api.parse_retry_after({}), 1)

    def test_rate_retry_does_not_force_token_refresh(self):
        with tempfile.TemporaryDirectory() as directory:
            store = api.TokenStore(Path(directory) / "token.json")
            store.save({"access_token": "same", "refresh_token": "unused", "expires_at": 9999})
            responses = [
                FakeResponse(429, b"{}", {"Content-Type": "application/json", "Retry-After": "0"}),
                FakeResponse(200, b'{"code":0}'),
            ]
            seen = []

            def opener(request, timeout):
                seen.append(request.headers.get("Authorization"))
                return responses.pop(0)

            client = api.AppFlowyClient(
                "https://flow.example", token_store=store, opener=opener,
                clock=lambda: 100, sleeper=lambda _: None,
            )
            self.assertEqual(client.request("GET", "/api/user").status, 200)
            self.assertEqual(seen, ["Bearer same", "Bearer same"])


if __name__ == "__main__":
    unittest.main()
