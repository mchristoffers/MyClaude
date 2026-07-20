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
   `instant_deploy=false`, and the Compose path.
4. Set variables with `PATCH /applications/{uuid}/envs/bulk`. Never print values.
5. Set the domain on the public service only, then deploy with
   `POST /applications/{uuid}/start`.
6. Verify HTTPS, container health, and volumes.

To update, push to the production branch and let the webhook deploy. Roll back by
reverting the commit or pinning the previous image tag; restore data only from a
backup. Back up volumes before schema-affecting upgrades.

Record the app UUID, domain, and Compose path in
`/home/moritz/okf/infra/<app>-master1.md`.
