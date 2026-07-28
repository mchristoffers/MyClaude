---
name: deploy-master1-compose
description: "Deploy and operate private GitHub Docker Compose apps on Moritz's master-1 Coolify: app setup, staging/prod branches, domains, secrets, volumes, deploys, rollbacks, migrations, and retiring apps. Coolify clones/builds/deploys; GitHub Actions only test and send signed manual webhook payloads through Cloudflare Access. Never use for Homeserver Coolify."
---

# Workflow

Use master-1 Coolify: `https://coolify.mchristoffers.dev`. Never use
`coolify-home.mchristoffers.dev`.

Coolify owns runtime, domains, env, volumes, cloning, build, and deploy. Actions
only run checks and trigger deploys. No GitHub App, GHCR, registry/image-push
pipeline, or `production` branch.

Discover repo/app details live from OKF, GitHub, Coolify, DNS, and the repo.
Do not hardcode stale assumptions.

## Repository

Every app needs its own private GitHub repo first, holding the production
Compose file. Create it before touching Coolify.

Compose either pulls a ready-made image or builds the repo's own Dockerfile.

Ask Moritz up front, per app: exact domain, and ready-made image vs own build.

## Setup

- Branches: `main` = production, optional `staging` = stage.
- One Coolify Docker Compose app per branch.
- Use repo-scoped read-only deploy key/SSH access.
- Use the repo's production Compose file unless the repo proves otherwise.
- Compose holds every service the app needs — web, DBs, caches, queues, search,
  workers, cron — plus its volumes and networks. Never wire separate Coolify
  database or service resources into an app.
- Stage and production must not share volumes.
- Remove repo-level GitHub webhooks; Actions are the only trigger.
- Before first build, check master-1 memory/swap. Do not let OOM decide.

## Domains

- DNS preference: apex + wildcard point to master-1.
- Keep explicit DNS records only for tunnel/external/mail exceptions.
- Coolify still binds exact hostnames per app.
- Docker Compose app domains go in `docker_compose_domains`, not top-level
  `domains`.
- If the web service joins multiple networks, add
  `traefik.docker.network=coolify`.
- Check FQDN conflicts before binding.
- Verify stored `fqdn`, `docker_compose_domains`, Traefik labels, and HTTPS.

## Access

Load `/home/moritz/.config/master1-coolify.env`. Send both Coolify auth and
Cloudflare Access headers. 302 means missing Access headers; 401 means bad
Coolify token.

## Actions trigger

- `COOLIFY_GITHUB_WEBHOOK`
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

Record app UUIDs, domains, Compose path, secrets, and test results in
`/home/moritz/okf/infra/<app>-master1.md`.
