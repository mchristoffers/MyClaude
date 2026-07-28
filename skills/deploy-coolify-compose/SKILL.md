---
name: deploy-coolify-compose
description: "Deploy and operate private GitHub Docker Compose apps on Moritz's Coolify instances — master-1 (Hetzner VPS, production) or Homeserver (homelab): app setup, staging/prod branches, domains, secrets, volumes, deploys, rollbacks, migrations, and retiring apps. Coolify clones/builds/deploys; GitHub Actions only test and send signed manual webhook payloads through Cloudflare Access."
---

# Workflow

Coolify owns runtime, domains, env, volumes, cloning, build, and deploy. Actions
only run checks and trigger deploys. No GitHub App, GHCR, registry/image-push
pipeline, or `production` branch.

Discover repo/app details live from OKF, GitHub, Coolify, DNS, and the repo.
Do not hardcode stale assumptions.

## Ask up front

Per app, before touching anything:

- Target: **master-1** or **Homeserver**.
- Exact domain.
- Ready-made image or the repo's own Dockerfile build.

## Target

Two independent instances. Never add one host to the other's Coolify, never
reuse hostnames or credentials across them.

| | master-1 | Homeserver |
| --- | --- | --- |
| Use for | public production | homelab, heavy/stateful |
| Coolify | `https://coolify.mchristoffers.dev` | `http://localhost:8000`, public `https://coolify-home.mchristoffers.dev` |
| Creds | `/home/moritz/.config/master1-coolify.env` | `/home/moritz/.config/home-coolify.env` |
| Proxy | Coolify Traefik | none — Tailscale holds `:443` |
| Ingress | Traefik + wildcard DNS | cloudflared tunnel + explicit CNAME |
| Budget | ~3.7 GiB RAM, tight disk | ~13 GiB RAM, roomy |

Pick the Homeserver when the app is stateful, storage-hungry, or not worth VPS
resources. Check the target's free memory, swap, and disk before the first
build; do not let OOM decide.

## Repository

Every app needs its own private GitHub repo first, holding the production
Compose file. Create it before touching Coolify.

Compose either pulls a ready-made image or builds the repo's own Dockerfile.

- Branches: `main` = production, optional `staging` = stage.
- One Coolify Docker Compose app per branch.
- Compose holds every service the app needs — web, DBs, caches, queues, search,
  workers, cron — plus its volumes and networks. Never wire separate Coolify
  database or service resources into an app.
- Stage and production must not share volumes.
- Use repo-scoped read-only deploy keys. One key per repo; GitHub rejects a
  deploy key already registered on another repo.
- Remove repo-level GitHub webhooks; Actions are the only trigger.

## Domains

Check FQDN conflicts before binding. Verify HTTPS on the real hostname when done.

**master-1** — apex + wildcard already point there; keep explicit DNS records
only for tunnel/external/mail exceptions. Coolify binds exact hostnames per app:
put Compose app domains in `docker_compose_domains`, not top-level `domains`.
If the web service joins multiple networks, add `traefik.docker.network=coolify`.

**Homeserver** — no Traefik, so the web service publishes a host port and the
homelab cloudflared tunnel `758ee962-…` fronts it: add an ingress entry to
`~/git/mchristoffers/homelab/cloudflared-config.yml` pointing at
`http://192.168.178.112:<port>`, then `docker compose restart tunnel` there.
Add an explicit proxied CNAME to `<tunnel-id>.cfargotunnel.com` — it overrides
the wildcard that points at master-1. Leave the Coolify `fqdn` and
`docker_compose_domains` empty. Set `TRUSTED_PROXIES` plus the app's
overwrite-host/protocol settings so it emits correct HTTPS URLs.

**Homeserver name collisions** — the shared `coolify` network carries the
aliases `redis`, `postgres`, and `soketi` from Coolify's own containers. Prefix
backing services (`<app>-db`, `<app>-redis`) or they resolve to Coolify's
password-protected ones.

## Access

Load the target's env file. Send Coolify auth, plus Cloudflare Access headers
over a public URL. 302 means missing Access headers; 401 means bad Coolify
token. On the Homeserver prefer the local URL — no Access needed. Sanctum tokens
contain a `|`, so keep them double-quoted.

## Actions trigger

- `COOLIFY_GITHUB_WEBHOOK` — the target's `/webhooks/source/github/events/manual`
- `COOLIFY_GITHUB_SECRET_PRODUCTION`
- `COOLIFY_GITHUB_SECRET_STAGING` for stage
- `CF_ACCESS_CLIENT_ID`
- `CF_ACCESS_CLIENT_SECRET`

Get app webhook secrets through Coolify's app model, not raw DB columns.

Use one workflow per branch: checkout, setup, install, test, HMAC-sign
`GITHUB_EVENT_PATH`, POST it to Coolify's manual GitHub webhook with GitHub event
headers and Cloudflare Access headers, and fail unless Coolify queues deploy.

## Operate

Push to `main`/`staging`. Verify Action output, Coolify build, image tag =
commit, and live URL. Roll back with `git revert`. Avoid force rebuilds unless
stale cache is the diagnosis.

Record target, app UUIDs, domains, Compose path, secrets, and test results in
`/home/moritz/okf/infra/<app>-<target>.md`.
