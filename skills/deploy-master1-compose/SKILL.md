---
name: deploy-master1-compose
description: "Deploy and maintain production applications on master-1 Coolify from private GitHub repositories that ship a production Docker Compose file using upstream images. Use for creating a master-1 application, connecting a private repo through the Coolify GitHub App, configuring domains, secrets and volumes, deploying, updating, rolling back, or retiring it. Never use for the separate Homeserver Coolify."
---

# Workflow

Target is master-1 Coolify at `https://coolify.mchristoffers.dev`, never the
Homeserver instance at `coolify-home.mchristoffers.dev`.

## API access

Cloudflare Access fronts the API, so every call needs both headers:

```sh
curl -s -H "Authorization: Bearer $COOLIFY_TOKEN" \
     -H "CF-Access-Client-Id: $CF_ACCESS_CLIENT_ID" \
     -H "CF-Access-Client-Secret: $CF_ACCESS_CLIENT_SECRET" \
     -H "Accept: application/json" \
     https://coolify.mchristoffers.dev/api/v1/teams
```

A 302 means the Access headers are missing or wrong; a 401 means the Coolify
token is. Ask the user to export the three variables if any are unset.

## Steps

1. Confirm the repo is private, the branch exists, and the Compose file uses
   `image:` entries with named volumes and no published database ports.
2. Discover UUIDs live: `GET /projects`, `/servers`, `/github-apps`.
3. Create with `POST /applications/private-github-app` using `build_pack=dockercompose`,
   `git_branch=main`, `is_auto_deploy_enabled=true`, `instant_deploy=false`, and
   the Compose path.
4. Set variables with `PATCH /applications/{uuid}/envs/bulk`. Never print values.
5. Set the domain on the public service only, then deploy with
   `POST /applications/{uuid}/start`.
6. Verify HTTPS, container health, and volumes.

## Deploy on push

Coolify's GitHub App installs the webhook itself. With `is_auto_deploy_enabled:
true` and `git_branch: main`, every push to `main` redeploys the stack from that
commit. No GitHub Action, no registry, no build step.

Versioning is the `image:` tag pinned in the Compose file, so upgrading is:
bump the tag, commit, push to `main`. Coolify redeploys with the new image.
Roll back by reverting that commit. Never use `:latest` — an unpinned tag makes
both the deployed version and the rollback target ambiguous.

Restore data only from a backup, and back up volumes before schema-affecting
upgrades; an older image is not a safe rollback across a migration.

Record the app UUID, domain, and Compose path in
`/home/moritz/okf/infra/<app>-master1.md`.
