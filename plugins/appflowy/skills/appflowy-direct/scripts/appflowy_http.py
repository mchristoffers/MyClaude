#!/usr/bin/env python3
"""Direct, safety-gated HTTP client for a self-hosted AppFlowy instance."""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
DESTRUCTIVE_PARTS = re.compile(r"(?:^|/)(?:delete|leave|trash|cancel|abort|unpublish)(?:/|$)")
SECRET_KEYS = re.compile(r"(?:token|password|secret|authorization|cookie)", re.I)
ALLOWED_ROOTS = ("/api", "/gotrue")


class AppFlowyError(RuntimeError):
    pass


@dataclass
class Response:
    status: int
    headers: Any
    body: bytes


def default_cache_path() -> Path:
    configured = os.environ.get("APPFLOWY_TOKEN_CACHE")
    if configured:
        return Path(configured).expanduser()
    root = os.environ.get("XDG_RUNTIME_DIR") or os.environ.get("XDG_CACHE_HOME")
    if root:
        return Path(root) / "appflowy-direct" / "token.json"
    return Path.home() / ".cache" / "appflowy-direct" / "token.json"


def validate_base_url(value: str) -> str:
    parsed = urllib.parse.urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise AppFlowyError("APPFLOWY_BASE_URL must be an http(s) origin")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise AppFlowyError("base URL must not contain credentials, query, or fragment")
    if parsed.path not in {"", "/"}:
        raise AppFlowyError("base URL must not contain a path")
    if parsed.scheme != "https" and parsed.hostname not in {"localhost", "127.0.0.1", "::1"}:
        raise AppFlowyError("plain HTTP is allowed only for a local host")
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, "", "", "")).rstrip("/")


def validate_path(path: str) -> str:
    parsed = urllib.parse.urlsplit(path)
    if parsed.scheme or parsed.netloc or parsed.query or parsed.fragment:
        raise AppFlowyError("use a relative API path and --query; absolute URLs are rejected")
    decoded = urllib.parse.unquote(parsed.path)
    if not any(decoded == root or decoded.startswith(f"{root}/") for root in ALLOWED_ROOTS) or decoded.startswith("//"):
        raise AppFlowyError("path must start with /api or /gotrue")
    if any(part in {".", ".."} for part in decoded.split("/")) or "\\" in decoded:
        raise AppFlowyError("path traversal is rejected")
    return parsed.path


def is_destructive(method: str, path: str) -> bool:
    return method.upper() == "DELETE" or bool(DESTRUCTIVE_PARTS.search(urllib.parse.unquote(path)))


def redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: ("<redacted>" if SECRET_KEYS.search(str(key)) else redact(item)) for key, item in value.items()}
    if isinstance(value, list):
        return [redact(item) for item in value]
    if isinstance(value, tuple) and len(value) == 2:
        return (value[0], "<redacted>" if SECRET_KEYS.search(str(value[0])) else redact(value[1]))
    return value


def parse_retry_after(headers: Any) -> float:
    raw = headers.get("Retry-After") if headers else None
    try:
        return min(30.0, max(0.0, float(raw)))
    except (TypeError, ValueError):
        return 1.0


class TokenStore:
    def __init__(self, path: Path):
        self.path = path.expanduser().resolve()
        plugin_root = Path(__file__).resolve().parents[3]
        if self.path == plugin_root or plugin_root in self.path.parents:
            raise AppFlowyError("token cache must be outside the plugin repository")

    def load(self) -> dict[str, Any]:
        try:
            mode = stat.S_IMODE(self.path.stat().st_mode)
            if mode & 0o077:
                raise AppFlowyError(f"token cache permissions are unsafe: {oct(mode)}")
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError as exc:
            raise AppFlowyError("token cache is invalid JSON") from exc

    def save(self, data: dict[str, Any]) -> None:
        parent_existed = self.path.parent.exists()
        self.path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        if not parent_existed:
            os.chmod(self.path.parent, 0o700)
        fd, temporary = tempfile.mkstemp(prefix=".token-", dir=self.path.parent)
        try:
            os.fchmod(fd, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(data, handle, separators=(",", ":"))
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, self.path)
            os.chmod(self.path, 0o600)
        finally:
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass


class AppFlowyClient:
    def __init__(
        self,
        base_url: str,
        email: str | None = None,
        password: str | None = None,
        token_store: TokenStore | None = None,
        opener: Callable[..., Any] = urllib.request.urlopen,
        sleeper: Callable[[float], None] = time.sleep,
        clock: Callable[[], float] = time.time,
        timeout: float = 30.0,
    ):
        self.base_url = validate_base_url(base_url)
        self.email = email
        self.password = password
        self.tokens = token_store or TokenStore(default_cache_path())
        self.opener = opener
        self.sleeper = sleeper
        self.clock = clock
        self.timeout = timeout

    def _wire(self, request: urllib.request.Request) -> Response:
        try:
            with self.opener(request, timeout=self.timeout) as result:
                return Response(result.status, result.headers, result.read())
        except urllib.error.HTTPError as exc:
            return Response(exc.code, exc.headers, exc.read())
        except urllib.error.URLError as exc:
            raise AppFlowyError(f"network error: {exc.reason}") from exc

    def _auth_call(self, grant: str, payload: dict[str, str]) -> dict[str, Any]:
        body = json.dumps(payload).encode()
        request = urllib.request.Request(
            f"{self.base_url}/gotrue/token?grant_type={grant}",
            data=body,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "appflowy-direct/0.1",
            },
        )
        response = self._wire(request)
        if response.status >= 400:
            raise AppFlowyError(f"authentication failed with HTTP {response.status}")
        try:
            result = json.loads(response.body)
            if not result.get("access_token"):
                raise ValueError
            return result
        except (json.JSONDecodeError, ValueError) as exc:
            raise AppFlowyError("authentication returned an invalid response") from exc

    def access_token(self, force_refresh: bool = False) -> str:
        cached = self.tokens.load()
        if not force_refresh and cached.get("access_token") and float(cached.get("expires_at", 0)) > self.clock() + 10:
            return str(cached["access_token"])
        if cached.get("refresh_token"):
            try:
                result = self._auth_call("refresh_token", {"refresh_token": str(cached["refresh_token"])})
                return self._save_auth(result)
            except AppFlowyError:
                pass
        if not self.email or not self.password:
            raise AppFlowyError("set APPFLOWY_EMAIL and APPFLOWY_PASSWORD")
        result = self._auth_call("password", {"email": self.email, "password": self.password})
        return self._save_auth(result)

    def _save_auth(self, result: dict[str, Any]) -> str:
        expires = max(30, int(result.get("expires_in", 3600)))
        stored = {
            "access_token": result["access_token"],
            "refresh_token": result.get("refresh_token"),
            "expires_at": self.clock() + expires - 20,
        }
        self.tokens.save(stored)
        return str(stored["access_token"])

    def request(
        self,
        method: str,
        path: str,
        *,
        query: list[tuple[str, str]] | None = None,
        body: bytes | None = None,
        content_type: str | None = None,
        public: bool = False,
        device_id: str | None = None,
    ) -> Response:
        method = method.upper()
        path = validate_path(path)
        encoded_query = urllib.parse.urlencode(query or [], doseq=True)
        url = f"{self.base_url}{path}" + (f"?{encoded_query}" if encoded_query else "")
        refresh_token = False
        auth_retried = False
        rate_retried = False
        for _ in range(3):
            headers = {"Accept": "application/json", "User-Agent": "appflowy-direct/0.1"}
            if content_type:
                headers["Content-Type"] = content_type
            if device_id:
                headers.update({"client-version": "web", "device-id": device_id})
            if not public:
                headers["Authorization"] = f"Bearer {self.access_token(force_refresh=refresh_token)}"
                refresh_token = False
            request = urllib.request.Request(url, data=body, method=method, headers=headers)
            response = self._wire(request)
            if response.status == 401 and not public and not auth_retried:
                auth_retried = True
                refresh_token = True
                continue
            if response.status in {429, 503} and not rate_retried:
                rate_retried = True
                self.sleeper(parse_retry_after(response.headers))
                continue
            return response
        raise AppFlowyError("request failed after bounded retries")


def check_envelope(response: Response) -> Any:
    if response.status >= 400:
        raise AppFlowyError(f"AppFlowy returned HTTP {response.status}")
    content_type = response.headers.get("Content-Type", "") if response.headers else ""
    if "json" not in content_type and not response.body.lstrip().startswith((b"{", b"[")):
        return None
    try:
        payload = json.loads(response.body)
    except json.JSONDecodeError as exc:
        raise AppFlowyError("response claims JSON but is invalid") from exc
    if isinstance(payload, dict) and "code" in payload and payload["code"] != 0:
        raise AppFlowyError(f"AppFlowy error {payload['code']}: {payload.get('message', 'unknown error')}")
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("method", choices=["GET", "HEAD", "POST", "PUT", "PATCH", "DELETE"])
    parser.add_argument("path", help="relative /api or /gotrue path")
    parser.add_argument("--query", action="append", default=[], metavar="KEY=VALUE")
    body = parser.add_mutually_exclusive_group()
    body.add_argument("--json", help="JSON body; prefer --json-file")
    body.add_argument("--json-file", type=Path)
    body.add_argument("--upload", type=Path, help="raw/binary request body")
    parser.add_argument("--content-type")
    parser.add_argument("--output", type=Path, help="write response body to a file")
    parser.add_argument("--show-body", action="store_true", help="print private response JSON")
    parser.add_argument("--public", action="store_true", help="send no Bearer token")
    parser.add_argument("--device-id", help="stable non-secret device ID for collab updates")
    parser.add_argument("--execute-write", action="store_true")
    parser.add_argument("--execute-destructive", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--timeout", type=float, default=30)
    return parser


def parse_query(values: list[str]) -> list[tuple[str, str]]:
    result = []
    for value in values:
        if "=" not in value:
            raise AppFlowyError("--query must be KEY=VALUE")
        result.append(tuple(value.split("=", 1)))
    return result


def load_body(args: argparse.Namespace) -> tuple[bytes | None, str | None, Any]:
    if args.json is not None:
        value = json.loads(args.json)
        return json.dumps(value).encode(), args.content_type or "application/json", value
    if args.json_file is not None:
        value = json.loads(args.json_file.read_text(encoding="utf-8"))
        return json.dumps(value).encode(), args.content_type or "application/json", value
    if args.upload is not None:
        return args.upload.read_bytes(), args.content_type or "application/octet-stream", "<binary>"
    return None, args.content_type, None


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        method = args.method.upper()
        path = validate_path(args.path)
        if method in WRITE_METHODS and not args.execute_write:
            raise AppFlowyError("mutation blocked: add --execute-write")
        if is_destructive(method, path) and not args.execute_destructive:
            raise AppFlowyError("destructive request blocked: also add --execute-destructive")
        query = parse_query(args.query)
        body, content_type, preview = load_body(args)
        base_url = validate_base_url(os.environ.get("APPFLOWY_BASE_URL", ""))
        if args.dry_run:
            print(json.dumps(redact({
                "method": method, "url": f"{base_url}{path}", "query": query,
                "content_type": content_type, "body": preview, "authenticated": not args.public,
            }), indent=2))
            return 0
        client = AppFlowyClient(
            base_url,
            os.environ.get("APPFLOWY_EMAIL"),
            os.environ.get("APPFLOWY_PASSWORD"),
            timeout=args.timeout,
        )
        response = client.request(
            method, path, query=query, body=body, content_type=content_type,
            public=args.public, device_id=args.device_id or os.environ.get("APPFLOWY_DEVICE_ID"),
        )
        payload = check_envelope(response)
        if args.output:
            if args.output.exists():
                raise AppFlowyError("output file already exists; choose a new path")
            args.output.write_bytes(response.body)
            print(f"HTTP {response.status}; wrote {len(response.body)} bytes")
        elif args.show_body:
            if payload is None:
                raise AppFlowyError("binary response requires --output")
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            kind = "json" if payload is not None else "binary"
            print(f"HTTP {response.status}; {kind}; {len(response.body)} bytes (body hidden)")
        return 0
    except (AppFlowyError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
