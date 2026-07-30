# Endpoint catalog

Paths are relative to `APPFLOWY_BASE_URL`. Read the current object before any
mutation; route payloads can change between Cloud releases.

## Server, user, workspace

- `GET /api/health`, `GET /gotrue/health`
- `GET /api/server-info`, `/api/server-info/auth-providers`
- `/api/user`, `/api/user/profile`, `/api/user/verify/{access_token}`
- `GET|POST|PATCH /api/workspace`
- `/api/user/workspace`
- `/api/workspace/{workspace}/settings`
- `/api/workspace/{workspace}/member`, invitations, open, leave, delete
- sharing and access-request routes under `/api/workspace/{workspace}`

## Pages and navigation

- Spaces, page views, folder/tree, favorites, recent, trash and move live under
  `/api/workspace/{workspace}`.
- Fetch the workspace tree with
  `/api/workspace/{workspace}/view/{workspace}?depth=N`.
- Page publication:
  `POST /api/workspace/{workspace}/page-view/{view}/publish` and `/unpublish`.
- Publish metadata: `/api/workspace/v1/published-info/{view}`.
- Namespace/default/outline, comments, reactions, configuration and
  `published-duplicate` are under `/api/workspace`.
- Do not use obsolete `/api/workspace/{workspace}/published-info`.

## Search and quick notes

- `GET /api/search/{workspace}` and `/api/search/{workspace}/page`
- `/api/workspace/{workspace}/quick-note`
- AI summary search is unavailable locally.

## Files

- Usage: `GET /api/file_storage/{workspace}/usage`
- Blob: `/api/file_storage/{workspace}/v1/blob/{view}/{file}`
- Upload: `PUT /api/file_storage/{workspace}/v1/blob/{view}`
- Large files use create/upload-part/list-parts/complete/abort multipart routes
  in the same file-storage family. Use raw/binary mode and preserve returned
  upload IDs and ETags.

## Import and export

- `/api/import/create`, `/api/import/{workspace}/notion`, task cancellation and
  multipart completion
- `/api/workspace/{workspace}/database/import/csv`
- `POST /api/export/workspace/{workspace}` with `include_file_attachments`; the
  workspace export is asynchronous.
- `POST /api/export/view/{workspace}/{view}/pdf`

## CLI patterns

```sh
python3 ../../scripts/appflowy_http.py GET /api/user/profile --show-body
python3 ../../scripts/appflowy_http.py GET /api/search/WORKSPACE_ID \
  --query query=term --query limit=20 --show-body
python3 ../../scripts/appflowy_http.py PUT \
  /api/file_storage/WORKSPACE_ID/v1/blob/VIEW_ID \
  --upload /tmp/file.bin --content-type application/octet-stream --execute-write
```

Use a JSON file for payloads. The helper is a generic native-API transport, so
new or less common routes do not require a plugin release.
