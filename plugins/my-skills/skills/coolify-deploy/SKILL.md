---
name: coolify-deploy
description: Use when deploying or updating a self-hosted app, setting up a new app on the Users infrastructure, or anything involving Coolify, Traefik/Let's Encrypt domains, or DNS for mchristoffers.dev. Covers the SSH-tunneled Coolify API, the two deployment shapes (service vs dockerimage), and the service-FQDN gotcha.
---

# Deploying apps via Coolify

## Infrastructure

- All self-hosted apps run on **Coolify 4.1.1** on a Hetzner VPS **`master-1`** (IP `178.105.233.193`, SSH alias `master-1`). Coolify ships **Traefik** as reverse proxy with automatic **Let's Encrypt** TLS.
- Currently hosts: BeautyByJulia (`julialeocardia.de`), Mealie (`mealie.mchristoffers.dev`).
- Server UUID in Coolify: `vujyc7sfezma2okcnnhi4huw` (name `localhost`).

## Coolify API — SSH-only (gotcha)

The dashboard `coolify.mchristoffers.dev` is behind **Cloudflare Access**, so the API is **only reachable from the box via localhost**. Tunnel every API call over SSH. Token lives at `~/.bbj_coolify_token`.

```bash
TOKEN=$(cat ~/.bbj_coolify_token)
ssh master-1 "curl -s -H 'Authorization: Bearer $TOKEN' http://localhost:8000/api/v1/<endpoint>"
```

Useful endpoints:

| Endpoint | Purpose |
|---|---|
| `GET /api/v1/projects`, `POST /api/v1/projects` | list / create projects |
| `GET /api/v1/servers` | server UUIDs |
| `GET /api/v1/applications`, `GET /api/v1/services` | list resources |
| `POST /api/v1/services` | create service from raw compose |
| `POST /api/v1/applications/dockerimage` | create image-based app |
| `GET /api/v1/deploy?uuid=<uuid>&force=true` | (re)deploy a resource |

## Two deployment shapes

### 1. Off-the-shelf app (upstream public image, e.g. Mealie)

Deploy as a Coolify **service** from a raw compose. `POST /api/v1/services` with body:

- `name`, `project_uuid`, `environment_name` (e.g. `production`), `server_uuid`
- `docker_compose_raw` — the compose file, **base64-encoded**
- `instant_deploy: false`

Coolify also has built-in one-click templates (`{"type":"mealie",...}`), but those may pin an older version / SQLite — **prefer your own `docker_compose_raw`** for full control (image version, Postgres).

Coolify "magic" variables inside the compose:

- `SERVICE_FQDN_<SERVICENAME>_<PORT>` → assigns the public domain + generates Traefik/LE labels.
- `SERVICE_PASSWORD_<NAME>` → Coolify-generated password; reference it (e.g. shared between app and its Postgres).
- For the DB: a sibling `postgres` service in the same compose with a named volume, or a Coolify-managed Postgres database resource.

### 2. Custom app built here (e.g. BeautyByJulia, Next.js)

1. Build a versioned image, push to **private GHCR**: `ghcr.io/mchristoffers/<app>`.
2. Deploy as a Coolify **`dockerimage`** application (`POST /api/v1/applications/dockerimage`).
3. Release via two manual GitHub Actions:
   - `build` → builds + pushes the image
   - `release` → PATCHes Coolify's image tag + triggers `GET /api/v1/deploy`
4. Repo secrets needed: `COOLIFY_URL`, `COOLIFY_TOKEN`, `COOLIFY_APP_UUID`.

## Service domain gotcha (the tricky part)

When a service is created, Coolify auto-generates an `*.sslip.io` domain and stores the per-service FQDN in its **database** — not just the `SERVICE_FQDN_*` env var. Setting the env var alone does **not** change Traefik routing, and the 4.1.1 API exposes no field for it. To set a real domain, update the DB row and redeploy:

```bash
# find the service_application uuid: GET /api/v1/services/<uuid> → applications[0].uuid
ssh master-1 "docker exec coolify-db psql -U coolify -c \"UPDATE service_applications SET fqdn='https://app.example.com:<containerport>' WHERE uuid='<service_application_uuid>';\""
# then redeploy:
ssh master-1 "curl -s -H 'Authorization: Bearer $TOKEN' 'http://localhost:8000/api/v1/deploy?uuid=<service_uuid>&force=true'"
```

## DNS (Cloudflare)

- Zone `mchristoffers.dev` is on Cloudflare, zone id `1efd3300a791a6ec4e7dd171c9493cae`.
- A scoped **"Edit zone DNS"** API token is in Bitwarden as Secure Note **"Cloudflare DNS API Token (mchristoffers.dev)"** (field `token`): `bw get item "Cloudflare DNS API Token (mchristoffers.dev)"`.
- For Coolify/Traefik Let's Encrypt to work, the A-record must be **DNS-only (grey cloud, `proxied:false`)** pointing to `178.105.233.193` — proxied/orange-cloud breaks the HTTP-01 challenge.

```bash
CF=<token from vault>; ZONE=1efd3300a791a6ec4e7dd171c9493cae
curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE/dns_records" \
  -H "Authorization: Bearer $CF" -H "Content-Type: application/json" \
  -d '{"type":"A","name":"<sub>","content":"178.105.233.193","proxied":false,"ttl":300}'
```

## Verification — always before claiming done

```bash
ssh master-1 "docker ps --filter name=<uuid> --format '{{.Names}} {{.Status}}'"   # healthy?
curl -s -o /dev/null -w 'http=%{http_code} ssl_verify=%{ssl_verify_result}\n' https://<domain>/   # expect 200, ssl_verify=0
echo | openssl s_client -connect <domain>:443 -servername <domain> 2>/dev/null | openssl x509 -noout -issuer -enddate   # expect Let's Encrypt
```
