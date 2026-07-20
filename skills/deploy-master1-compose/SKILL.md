---
name: deploy-master1-compose
description: "Deploy and maintain production applications on master-1 Coolify from private GitHub repositories that ship a production Docker Compose file. Coolify clones, builds, and deploys on push to main with no GitHub Action and no image registry. Use for creating a master-1 application, connecting a private repo through the Coolify GitHub App, configuring domains, secrets and volumes, deploying, updating, rolling back, or retiring it. Never use for the separate Homeserver Coolify."
---

# Workflow

Target is master-1 Coolify at `https://coolify.mchristoffers.dev`, never the
Homeserver instance at `coolify-home.mchristoffers.dev`.

Coolify owns the whole pipeline: its GitHub App installs the webhook, clones the
private repo on push to `main`, builds any `build:` services on master-1, and
brings the stack up. Never add a GitHub Action or push images to a registry.

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
3. Create with `POST /applications/private-github-app` using
   `build_pack=dockercompose`, `git_branch=main`, `is_auto_deploy_enabled=true`,
   `instant_deploy=false`, and the Compose path.
4. Set variables with `PATCH /applications/{uuid}/envs/bulk`. Never print values.
5. Set the domain on the public service only, then deploy with
   `POST /applications/{uuid}/start`.
6. Verify HTTPS, container health, and volumes.

## Deploy and roll back

Every push to `main` rebuilds and redeploys from that commit — the commit is the
version. Pin base images and any upstream `image:` to explicit tags, never
`:latest`, so a rebuild of an old commit still produces the same result.

Roll back by reverting the commit, which triggers a rebuild. That is slower than
swapping a prebuilt image, so for an urgent outage prefer `git revert` of the
smallest change over redeploying an old commit wholesale. Back up volumes before
schema-affecting upgrades; an older image is not a safe rollback across a
migration, and restore data only from a backup.

Record the app UUID, domain, and Compose path in
`/home/moritz/okf/infra/<app>-master1.md`.
