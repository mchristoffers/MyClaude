# Collab wire format

Fetch:

`GET /api/workspace/v1/{workspace}/collab/{object}?collab_type=N`

Submit a Yjs update:

`POST /api/workspace/v1/{workspace}/collab/{object}/web-update`

```json
{"doc_state": [1, 2, 3], "collab_type": 0}
```

Send `client-version: web` and a stable, non-secret `device-id`. Collab types:

| Value | Type |
|---:|---|
| 0 | Document |
| 1 | Database |
| 2 | WorkspaceDatabase |
| 3 | Folder |
| 4 | DatabaseRow |
| 5 | UserAwareness |
| 6 | Empty |

`doc_state` is binary Yjs state represented as JSON byte values. It is not UTF-8
document text. An update must be produced by a compatible Yjs/AppFlowy schema
implementation. This plugin intentionally has no speculative high-level block
writer. Raw transport remains available for state produced by an official
client or a separately verified schema implementation.
