---
name: deploy-master1-compose
description: "Deploy and maintain production and optional staging applications on master-1 Coolify from private GitHub repositories that ship a production Docker Compose file. Coolify clones, builds, and deploys on push to main/staging with no GitHub Action and no image registry. Use for creating a master-1 application, connecting a private repo through the Coolify GitHub App, configuring domains, secrets and volumes, deploying, updating, rolling back, or retiring it. Never use for the separate Homeserver Coolify."
---

# Workflow

Target is master-1 Coolify at `https://coolify.mchristoffers.dev`, never the
Homeserver instance at `coolify-home.mchristoffers.dev`.

Coolify owns the pipeline through a private GitHub App source: it clones the
private repo on push, builds any `build:` services on master-1, and brings the
stack up. Never add a GitHub Action or push images to a registry.

Default production branch is `main`. Optional staging is the same Coolify source
setup as production, only with `git_branch=staging` and a staging domain. Do not
create a separate staging webhook.

## API access

Cloudflare Access fronts the API, so every call needs both headers. The four
variables live in `~/.config/master1-coolify.env`:

```sh
curl -s -H "Authorization: Bearer $COOLIFY_TOKEN" \
     -H "CF-Access-Client-Id: $CF_ACCESS_CLIENT_ID" \
     -H "CF-Access-Client-Secret: $CF_ACCESS_CLIENT_SECRET" \
     -H "Accept: application/json" \
     "$COOLIFY_URL/api/v1/teams"
```

302 means the Access headers are missing or wrong; 401 means the Coolify token is.

## Check the build fits first

master-1 is 2 vCPU / 3.8 GB and runs live containers. Builds happen on that same
box, so before the first deploy of any service with a `build:` section:

```sh
ssh master-1 'free -m; swapon --show'
```

Require at least 2 GB of available memory or active swap. A Node build needs
roughly 1.5 GB, so prefer a slim base image and a multi-stage Dockerfile.

Order the Dockerfile so dependencies install before the source is copied
(`COPY package*.json` and install, then `COPY . .`). The dependency layer then
survives ordinary code pushes, and most deploys skip the expensive step.

If there is not enough, either add swap or stop other stacks for the duration of
the build — Moritz has approved stopping them while the remaining apps are
migrated. Stop them deliberately with `POST /applications/{uuid}/stop` and
restart them after; do not leave the OOM killer to choose, because it reaps
running production containers rather than the build. Say which public sites will
go down before stopping anything.

## Steps

1. Confirm the repo is private and the Compose file uses named volumes and
   publishes no database ports.
2. Discover UUIDs live: `GET /projects`, `/servers`, `/github-apps`.
   A real private GitHub App source is required. If it is missing or incomplete,
   set it up first; do not replace this workflow with deploy-key apps or manual
   webhooks unless Moritz explicitly asks for a temporary fallback.
3. Create production with `POST /applications/private-github-app` using
   `build_pack=dockercompose`, `git_branch=main`, `is_auto_deploy_enabled=true`,
   and the Compose path. Set `instant_deploy=false` so env/domain setup happens
   before the first start; later `main` pushes still auto-deploy.
   If staging is wanted, create a second app the same way with
   `git_branch=staging` and its own domain/env/volumes. Use the same GitHub App
   source; only the branch differs.
4. Set variables with `PATCH /applications/{uuid}/envs/bulk`.
5. Set the domain on the public service only, then deploy with
   `POST /applications/{uuid}/start`.
6. Verify HTTPS, container health, and volumes.

## Deploy and roll back

Every push to the app branch (`main` for production, `staging` for staging)
rebuilds and redeploys immediately. There is no release tag and no manual step.
Roll back with `git revert`, which triggers the same rebuild.

A normal deploy runs `docker compose build --pull` and reuses Docker's layer
cache. Forcing a rebuild adds `--no-cache`, which rebuilds every layer and is the
most likely deploy to exhaust memory. Never force a rebuild as a debugging
reflex; do it only when a stale layer is the actual diagnosis.

Back up volumes before schema-affecting upgrades; an older image is not a safe
rollback across a migration, and restore data only from a backup.

Record the app UUID, domain, and Compose path in
`/home/moritz/okf/infra/<app>-master1.md`.
