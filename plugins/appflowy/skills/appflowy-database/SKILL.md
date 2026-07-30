---
name: appflowy-database
description: Read and manage AppFlowy databases through native HTTP endpoints. Use for database discovery, fields, typed cells, rows, row documents, CSV import, quick notes, relations, or database collabs.
---

# AppFlowy Database

Read `references/database.md` before constructing a field or cell payload.
Use `$appflowy-direct` for transport.

## Workflow

1. Fetch the database, fields, and target rows first.
2. Preserve field IDs, field type encodings, unknown properties, and `pre_hash`
   values returned by the server.
3. Build the smallest possible change in a JSON file.
4. Inspect with `--dry-run`, then use `--execute-write`.
5. Fetch the row plus details (`with_doc=true`) and verify it.

Rows and row documents may combine REST payloads with Yjs state. Use
`$appflowy-collab` when editing the document attached to a row. Never convert a
field type merely from its display name.

Summary and Translate fields depend on the disabled AI service; do not execute
AI population endpoints.
