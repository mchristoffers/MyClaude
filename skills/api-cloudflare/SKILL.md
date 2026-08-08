---
name: api-cloudflare
description: Use the Cloudflare API directly instead of asking Moritz to use the dashboard. Use when configuring DNS, Access, tunnels, Workers, or any other Cloudflare resource.
---

> Source: `~/git/mchristoffers/MyClaude/skills/api-cloudflare/SKILL.md`. Learned
> something here? Edit it there and reinstall (that repo's AGENTS.md) —
> never edit the installed copy, it is overwritten without warning.

# Cloudflare API

`CLOUDFLARE_API_TOKEN` is set in the environment — an API token with access to
Moritz's zones/account. Use it directly, don't ask him to open the dashboard.

```sh
curl -s -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  "https://api.cloudflare.com/client/v4/<endpoint>"
```

Base URL for every call: `https://api.cloudflare.com/client/v4`.

## Finding the right endpoint

`references/openapi.json` is the unmodified official spec, from
https://github.com/cloudflare/api-schemas. It's 23 MB, so don't `cat`/`Read`
the whole file — `jq` or `grep` for what you need, e.g.:

```sh
jq '.paths | keys[]' references/openapi.json | grep -i dns_records
jq '.paths["/zones/{zone_id}/dns_records"]' references/openapi.json
```
