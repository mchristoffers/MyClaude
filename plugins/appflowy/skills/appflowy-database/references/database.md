# Database API

Core routes:

- `GET /api/workspace/{workspace}/database`
- `/api/workspace/{workspace}/database/{database}/fields`
- `GET|POST|PUT /api/workspace/{workspace}/database/{database}/row`
- Row detail accepts `ids` and `with_doc=true`.
- Create/update bodies contain `cells` and optionally `document`; updates may
  require the server-provided `pre_hash`.
- CSV import:
  `/api/workspace/{workspace}/database/import/csv`.

Web 0.16.1 field type numbers:

| Value | Type | Value | Type |
|---:|---|---:|---|
| 0 | RichText | 9 | CreatedTime |
| 1 | Number | 10 | Relation |
| 2 | DateTime | 11 | Summary |
| 3 | SingleSelect | 12 | Translate |
| 4 | MultiSelect | 13 | Time |
| 5 | Checkbox | 14 | Media |
| 6 | URL | 15 | Person |
| 7 | Checklist | 16 | Rollup |
| 8 | LastEditedTime | | |

Cells can carry their stored field type independently of the field's current
display type. Preserve `field_type`, legacy metadata, timestamps, unknown
properties, relation IDs and selection IDs unless the requested operation
explicitly changes them. Summary and Translate depend on the disabled AI
service.
