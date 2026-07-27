---
name: deploy-master1-compose
description: "Deploy and maintain production and optional staging applications on master-1 Coolify from private GitHub repositories with a Docker Compose file. Coolify clones by deploy key and builds on master-1; GitHub Actions only run checks and send signed push payloads through Cloudflare Access to Coolify's manual GitHub webhook. Use for domains, secrets, volumes, deploys, rollbacks, staging, and retiring apps on master-1. Never use for the separate Homeserver Coolify."
---

# Workflow

Target: master-1 Coolify at `https://coolify.mchristoffers.dev`, never
`coolify-home.mchristoffers.dev`.

Coolify owns runtime, domains, env, volumes, cloning, build, and deploy. GitHub
Actions only trigger deploys. No GitHub App, GHCR, registry, image-push
pipeline, or production branch.

## Setup

- Branches: `main` for production, optional `staging` for stage.
- Create one Coolify Compose app per branch, using the private deploy key source
  and the repo's production Compose file.
- Remove repo-level GitHub webhooks; Actions are the only trigger.
- Before first build: `ssh master-1 'free -m; swapon --show'`. Add swap or stop
  non-critical apps if memory is tight; never let OOM choose.

## Domains

- Bind only exact hostnames, e.g. `https://example.com` or
  `https://stage.example.com`; do not treat a base domain as owning every
  subdomain.
- For Docker Compose apps, set service domains through
  `docker_compose_domains`, e.g.
  `[{ "name": "app", "domain": "https://example.com" }]`; do not use the
  top-level `domains` field.
- Other subdomains of the same zone may point to other Coolify apps.
- DNS for each hostname must point to master-1 in Cloudflare; Coolify only owns
  proxy routing after DNS reaches the server.
- Before changing a hostname, check no other Coolify app already has that FQDN.
- After binding, verify stored `fqdn`, `docker_compose_domains`, and the running
  Traefik labels/HTTPS route. Stale `sslip.io` FQDNs in Coolify should be
  corrected through the Coolify API.

Compose domain update:

```sh
curl -sS -X PATCH "$COOLIFY_URL/api/v1/applications/$APP_UUID" \
  -H "Authorization: Bearer $COOLIFY_TOKEN" \
  -H "CF-Access-Client-Id: $CF_ACCESS_CLIENT_ID" \
  -H "CF-Access-Client-Secret: $CF_ACCESS_CLIENT_SECRET" \
  -H "Content-Type: application/json" \
  --data '{"docker_compose_domains":[{"name":"app","domain":"https://example.com"}]}'
```

## Access

Coolify is behind Cloudflare Access:

```sh
. ~/.config/master1-coolify.env
curl -s -H "Authorization: Bearer $COOLIFY_TOKEN" \
  -H "CF-Access-Client-Id: $CF_ACCESS_CLIENT_ID" \
  -H "CF-Access-Client-Secret: $CF_ACCESS_CLIENT_SECRET" \
  "$COOLIFY_URL/api/v1/teams"
```

302 = missing Access headers. 401 = bad Coolify token.

## Actions trigger

GitHub secrets:

- `COOLIFY_GITHUB_WEBHOOK` =
  `https://coolify.mchristoffers.dev/webhooks/source/github/events/manual`
- `COOLIFY_GITHUB_SECRET_PRODUCTION`
- `COOLIFY_GITHUB_SECRET_STAGING` if staging exists
- `CF_ACCESS_CLIENT_ID`
- `CF_ACCESS_CLIENT_SECRET`

Read app webhook secrets through Coolify's app model, not raw DB columns
(database values are encrypted). Each branch gets one small workflow:

```yaml
name: Deploy production
on: { push: { branches: [main] }, workflow_dispatch: {} }
concurrency: { group: deploy-production, cancel-in-progress: true }
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm }
      - run: npm ci
      - run: npm test
      - name: Trigger Coolify
        env:
          WEBHOOK_SECRET: ${{ secrets.COOLIFY_GITHUB_SECRET_PRODUCTION }}
        run: |
          sig="$(python3 - <<'PY'
          import hashlib,hmac,os; from pathlib import Path
          print("sha256="+hmac.new(os.environ["WEBHOOK_SECRET"].encode(),Path(os.environ["GITHUB_EVENT_PATH"]).read_bytes(),hashlib.sha256).hexdigest())
          PY
          )"
          out="$(mktemp)"
          curl --fail-with-body -X POST "${{ secrets.COOLIFY_GITHUB_WEBHOOK }}" \
            -H "Content-Type: application/json" -H "X-GitHub-Event: push" \
            -H "X-GitHub-Delivery: ${{ github.run_id }}-${{ github.run_attempt }}" \
            -H "X-Hub-Signature-256: $sig" \
            -H "CF-Access-Client-Id: ${{ secrets.CF_ACCESS_CLIENT_ID }}" \
            -H "CF-Access-Client-Secret: ${{ secrets.CF_ACCESS_CLIENT_SECRET }}" \
            --data-binary "@$GITHUB_EVENT_PATH" --output "$out"
          cat "$out"; ! grep -q '"status":"failed"' "$out"
```

For staging, change name, branch, concurrency group, and secret to
`COOLIFY_GITHUB_SECRET_STAGING`.

## Operate

Push to `main`/`staging`. Action must return `Deployment queued.`; Coolify must
build an image tagged with that commit and swap the app. Roll back with
`git revert` on the same branch. Avoid force rebuilds unless stale cache is the
actual diagnosis.

Record app UUIDs, domains, Compose path, secrets, and test results in
`/home/moritz/okf/infra/<app>-master1.md`.
