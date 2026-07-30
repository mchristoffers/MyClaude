---
name: appflowy-collab
description: Read or update AppFlowy document and collaboration objects through native collab HTTP endpoints. Use for documents, blocks, page content, folder collabs, database collabs, or raw Yjs state.
---

# AppFlowy Collab

Read `../../references/collab.md` before acting. AppFlowy collabs are Yjs
documents, not plain JSON.

## Safe workflow

1. Resolve the workspace, view/object ID, and exact collab type.
2. Fetch the current collab and save the raw state.
3. Decode or modify it only with a schema-compatible AppFlowy/Yjs client.
4. Encode a Yjs update, inspect the request, and send it through
   `../../scripts/appflowy_http.py` with `--execute-write`.
5. Fetch and validate the collab again.

Do not construct block maps by guesswork or replace `doc_state` with text. The
helper deliberately provides transport and raw state handling, not a high-level
block editor: silently corrupting a collab is worse than declining an
unsupported edit.

Publishing a page is a separate REST operation; consult
`../../references/endpoints.md`.
