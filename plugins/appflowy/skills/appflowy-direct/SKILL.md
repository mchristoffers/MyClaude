---
name: appflowy-direct
description: Operate a self-hosted AppFlowy instance through its native GoTrue and HTTP APIs without MCP. Use for users, workspaces, views, members, search, quick notes, files, imports, exports, publishing, comments, reactions, sharing, or arbitrary supported API calls.
---

# AppFlowy Direct

Call AppFlowy directly with `../../scripts/appflowy_http.py`. Never introduce an
MCP server, proxy, daemon, or container.

## Workflow

1. Read `../../references/compatibility.md` and the relevant section of
   `../../references/endpoints.md`.
2. Confirm `APPFLOWY_BASE_URL`, `APPFLOWY_EMAIL`, and `APPFLOWY_PASSWORD` exist
   in the environment. Never print them or pass credentials as arguments.
3. Read before writing. Use `--dry-run` to inspect a mutation.
4. Add `--execute-write` for mutations and also `--execute-destructive` for
   deletes, leave/trash/cancel/abort/unpublish.
5. Fetch the affected object again and verify the result.

```sh
python3 ../../scripts/appflowy_http.py GET /api/workspace \
  --query include_role=true --show-body
python3 ../../scripts/appflowy_http.py PATCH /api/workspace/WORKSPACE_ID \
  --json-file /tmp/appflowy-change.json --execute-write --dry-run
```

Output is private by default: without `--show-body` the helper prints only a
status/type/size summary. Use `--output` for binary downloads and `--upload` for
raw uploads. Prefer `--json-file` over inline JSON.

AI/chat and AI search-summary routes are unavailable on this installation.
Do not call them. Run the helper with `--help` for all request options.
