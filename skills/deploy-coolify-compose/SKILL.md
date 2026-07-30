---
name: deploy-coolify-compose
description: "Deploy and operate private GitHub Docker Compose apps on Moritz's Coolify instances — master-1 (Hetzner VPS, production) or Homeserver (homelab): app setup, staging/prod branches, domains, exposure (public, Cloudflare Access, or internal), secrets, volumes, deploys, rollbacks, migrations, and retiring apps. Coolify clones/builds/deploys; GitHub Actions test, send signed manual webhook payloads through Cloudflare Access, then wait for the deployment result and fail on a broken build."
---

> Source: `~/git/mchristoffers/MyClaude/skills/deploy-coolify-compose/SKILL.md`. Learned
> something here? Edit it there and reinstall (that repo's AGENTS.md) —
> never edit the installed copy, it is overwritten without warning.

# Workflow

Coolify owns runtime, domains, env, volumes, cloning, build, and deploy. Actions
only run checks and trigger deploys. No GitHub App, GHCR, registry/image-push
pipeline, or `production` branch.

Discover repo/app details live from OKF, GitHub, Coolify, DNS, and the repo.
Do not hardcode stale assumptions.

## Ask up front

Per app, before touching anything, get an **explicit answer from Moritz** to each:

- Target: **master-1** or **Homeserver**.
- Exact domain.
- Exposure: **public**, **behind Cloudflare Access**, or **internal only**.
- Ready-made image or the repo's own Dockerfile build.
- Data store: the app's built-in/SQLite mode or a real DB service in the Compose
  file — it decides backup shape and RAM, and it is a one-way door once there is
  data.

These are Moritz's calls, not judgment calls to absorb. Never settle one by
inference — not from the app's nature, not from what a comparable app got, not
from the target's resources, not from an OKF note. Recommend by all means, but
the recommendation is not the answer.

**A refused or unanswered question is not consent to proceed on a default.**
If the question tool is denied or the answer does not come, ask again in plain
text and wait. What you may do meanwhile is only the part that every possible
answer shares — read the repo, check resources, list free ports. Do not create
the repo, the Coolify app, DNS, or ingress on an assumed answer; unwinding those
costs more than waiting. Announcing an assumption is not the same as getting an
answer, and "I'll say what I picked and he can correct me" pushes the work of
catching a wrong guess onto Moritz.

Record every answer verbatim in the OKF page, so the next change starts from the
decision rather than re-deriving it.

**Image tags are already settled — do not ask, and do not argue it a second
time.** Moritz's standing choice, stated 2026-07-29 while setting up Paperless:
every app tracks the moving tag (`:latest`, or the upstream equivalent) with
`pull_policy: always`, **major versions included**, and updates itself on a
`schedule:` cron in its deploy workflow. He does not want to be the one deciding
when to upgrade, and he does not care about rollback.

Pinning is therefore not a recommendation to repeat. What the choice does change
is where the safety net goes: an app that upgrades unattended across majors will
migrate its database one way, so **set up the backup as part of the initial
deploy, not later** — a dump on a daily host cron, timed before the update
window, verified once by running it. "I can't lose my data" is the constraint;
"I can go back to yesterday's version" is not. Keep a version env var
(`<APP>_VERSION`) wired up anyway so a broken release can be pinned by hand
without a repo change.

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

**Values containing `{}` must be literal, not `${VAR:-default}`.** A default like
`{created_year}/{title}` collides with Compose's own substitution syntax, and
Coolify substitutes a second time on top. Write such settings straight into the
Compose file with a comment; they are rarely worth making configurable.

Use literal sources for host bind mounts too: Coolify misparses
`${ROOT:-/host/path}/subdir` and may mount the root at the wrong container path,
leaving the intended path on a disposable anonymous volume. For `postgres:18`,
mount persistent storage at `/var/lib/postgresql`, not the old
`/var/lib/postgresql/data`; v18 keeps the real cluster in a versioned directory
under the parent.

**Never bind-mount a config file from the repo.** Coolify writes only
`docker-compose.yaml` and `.env` into `/data/coolify/applications/<uuid>/` — the
working tree is not materialised there. A relative `./conf/app.conf` mount is
rewritten to an absolute host path and registered in `local_file_volumes` with
`is_directory=true` and empty content, so Docker creates a *directory* and the
container dies with `not a directory`. Ship config by baking it into a small
image (`build:` context with a `COPY`, plus a syntax check in the Dockerfile).
Pasting it into Coolify's file-mount UI instead splits the source of truth.

**Paperless AI:** prefer Paperless v3's native `PAPERLESS_AI_*` configuration
over `clusterzx/paperless-ai`, a fork, or a custom worker. Moritz accepts its
manual suggest/review/apply flow; do not add automation around it. Use the
OpenAI-like backend with OpenRouter, `google/gemini-2.5-flash-lite`, and
`https://openrouter.ai/api/v1`; omit embeddings, RAG, extra UI, services, and
ports. Keep the API key only in Coolify. Validate `AIClient` with synthetic text
without creating a fake archive document.

## Domains

Check FQDN conflicts before binding. Verify HTTPS on the real hostname when done.

**HTTPS is mandatory on every user-facing path; no HTTP/LAN fallback.**
Moritz prefers Let's Encrypt wherever the endpoint supports it:

- master-1: Coolify Traefik obtains and renews Let's Encrypt.
- internal: native Tailscale Services obtain and renew Let's Encrypt.
- Homeserver tunnel: Cloudflare terminates browser TLS with its managed edge
  certificate; do not add Caddy/Let's Encrypt behind the tunnel just to change
  the invisible origin certificate.

Verify the hostname, issuer, TLS validation, and HTTP 200. Close direct plaintext
bindings or redirect them to HTTPS.

**master-1** — apex + wildcard already point there; keep explicit DNS records
only for tunnel/external/mail exceptions. Coolify binds exact hostnames per app:
put Compose app domains in `docker_compose_domains`, not top-level `domains`.
If the web service joins multiple networks, add `traefik.docker.network=coolify`.

For a public legacy alias of an internal Tailscale app, create a tiny
master-1 Coolify Docker-image resource whose Traefik `RedirectRegex` middleware
redirects both HTTP and HTTPS to the native Tailscale Service. Use a permanent
redirect only after the alias is final: Safari retains it across DNS flushes,
so reversing the hostname later requires clearing Website Data for both names.
Preserve path and query. This gives the alias Let's Encrypt without exposing the
app; the redirect target remains inaccessible outside the tailnet.

**Homeserver** — public apps go through the shared cloudflared tunnel; internal
apps use native Tailscale Services.

**One tunnel serves the whole host** — the homelab cloudflared tunnel
`758ee962-…`, container `homelab-tunnel-1`, already carrying every homelab
hostname. Never create a per-app tunnel; it would only add a container and
credentials for the same path.

There is no Traefik, so the web service publishes a host port and the tunnel
fronts it. Per app that is exactly three things:

1. A free host port — list the existing `service:` lines before picking one.
2. An ingress entry in `~/git/mchristoffers/homelab/cloudflared-config.yml`
   pointing at `http://192.168.178.112:<port>`, added **above** the trailing
   `http_status:404` catch-all, then `docker compose restart tunnel` there.
3. An explicit proxied CNAME to `<tunnel-id>.cfargotunnel.com` — it overrides
   the wildcard that points at master-1.

Leave the Coolify `fqdn` and `docker_compose_domains` empty. Set
`TRUSTED_PROXIES` plus the app's overwrite-host/protocol settings so it emits
correct HTTPS URLs. Cloudflare terminates TLS, so honour `X-Forwarded-Proto`
rather than the scheme the app sees, or it emits `http://` links.

Coolify's API **refuses** to clear `fqdn` on a `dockercompose` app ("This field
is not allowed", pointing at `docker_compose_domains`). Clear the auto-assigned
`*.sslip.io` value with `UPDATE applications SET fqdn = NULL WHERE uuid = '…'`
in `coolify-db`.

**Internal only** — use a native Tailscale Service: `svc:<app>` becomes
`https://<app>.tail28fd13.ts.net`, with MagicDNS and Let's Encrypt managed by
Tailscale. No Cloudflare record/tunnel, Funnel, Caddy, or sidecar. Publish the
app only on loopback (`127.0.0.1:<port>:<container-port>`), then:

```sh
sudo tailscale serve --service=svc:<app> --https=443 http://127.0.0.1:<port>
```

If Moritz explicitly wants his own domain **without making the app public**,
replace native HTTPS with a Caddy sidecar: bake Caddy plus `caddy-dns/cloudflare`
into the repo, obtain Let's Encrypt through DNS-01, bind it only on
`127.0.0.1:8443`, and forward the Service as raw TCP:

```sh
sudo tailscale serve --service=svc:<app> --https=443 off
sudo tailscale serve --service=svc:<app> --tcp=443 tcp://127.0.0.1:8443
```

Create an exact DNS-only A record from the custom name to the Service TailVIP
and set the app's canonical URL to that name. The TailVIP remains unroutable
outside Tailscale; prove this from a non-tailnet host. Persist Caddy `/data`,
force the Let's Encrypt ACME endpoint, and remove any superseded master-1
redirect. The `*.ts.net` URL no longer has a matching certificate in this mode.

Finish native-client setup too. For Paperless/Paperparrot, connect Tailscale on
iOS first, enter the exact custom origin without an extra path, then use the app
credentials; never configure the superseded `*.ts.net` name. Test login and sync,
and record the client name and non-secret setup values in the app's OKF page.

The `docker` node is `tag:server`. Define the Service (`tcp:443`), grant tailnet
members access to it, and auto-approve `tag:server` in the policy. Tailscale
admin OAuth (`all`) lives in `~/.config/tailscale-admin.env`; use the API rather
than asking Moritz for console clicks. Keep each app isolated from the external
`coolify` network unless it actually needs that network.

**The workflow's live-URL health check has to go for an internal app.** A
GitHub runner reaches neither the LAN nor the tailnet, so that step can only
fail. Drop it and leave a comment saying why — Coolify's deployment status is
then the last word.

**Homeserver name collisions** — the shared `coolify` network carries the
aliases `redis`, `postgres`, and `soketi` from Coolify's own containers. Prefix
backing services (`<app>-db`, `<app>-redis`) or they resolve to Coolify's
password-protected ones.

## Exposure

Always Moritz's call — ask every time, never infer it from the app, and record
the answer; if the question goes unanswered, wait for it (see **Ask up front**)
instead of falling back to a default. The tunnel and Traefik only carry traffic;
they authenticate nothing, so reaching an app is never the same as being allowed
into it.

**Public** — the app's own login is the only gate. Right for apps with real
account management (Nextcloud, AppFlowy). Confirm the app actually has login
enforced and self-registration closed before choosing it.

**Behind Cloudflare Access** — Zero Trust team `sadfroger.cloudflareaccess.com`
fronts the hostname, as with `coolify-home`. Right for dashboards and admin
panels with weak, shared, or absent auth. Two policies: one identity policy for
Moritz's email, plus a non-identity **service token** policy for anything
automated. Machine callers then send `CF-Access-Client-Id/Secret`.

Access breaks every non-browser client — native mobile apps, desktop sync
clients, WebDAV, CLI tools — because they cannot complete the login redirect and
just see a 302. If the app has such clients, either stay public or accept that
only the browser works. Say this out loud when Access is picked.

**Internal only** — no public ingress; reachable only through its native
Tailscale Service name. Cheapest and safest when nothing off-tailnet needs it.

## API access

Load the target's env file. Send Coolify auth, plus Cloudflare Access headers
over a public URL. 302 means missing Access headers; 401 means bad Coolify
token. On the Homeserver prefer the local URL — no Access needed. Sanctum tokens
contain a `|`, so keep them double-quoted.

**Creating the app already creates its env vars.** Coolify parses the Compose
file on app creation and inserts every `${VAR}` it finds with an empty value, so
seeding them with `POST /applications/{uuid}/envs` answers *"Environment variable
already exists. Use PATCH request to update it."* for most keys and 201 for the
few it missed. Just `PATCH` the whole set — it is idempotent and covers both.

**Use curl, never Python's urllib, against a Cloudflare-fronted URL.** Cloudflare
rejects its user agent with `error code: 1010` (HTTP 403) even when the Access
headers are correct — a retry loop then spins forever instead of failing. This
only bites over the public hostname; local calls are unaffected.

## Actions trigger

- `COOLIFY_GITHUB_WEBHOOK` — the target's `/webhooks/source/github/events/manual`
- `COOLIFY_GITHUB_SECRET_PRODUCTION`
- `COOLIFY_GITHUB_SECRET_STAGING` for stage
- `CF_ACCESS_CLIENT_ID`
- `CF_ACCESS_CLIENT_SECRET`
- `COOLIFY_API_TOKEN` — to poll the deployment result

Get app webhook secrets through Coolify's app model, not raw DB columns.

Use one workflow per branch: checkout, setup, install, test, HMAC-sign the
payload, POST it to Coolify's manual GitHub webhook with GitHub event headers and
Cloudflare Access headers, then **wait for the deployment to actually finish**.

Queueing is not success. Every workflow must:

1. Read `deployment_uuid` from the webhook response and fail if it is absent.
2. Poll `GET /api/v1/deployments/{uuid}` (Bearer token + Access headers) until
   the status leaves `queued`/`in_progress`. Derive the base URL by cutting the
   webhook secret at `/webhooks/` so no second secret can drift.
3. Treat `finished` as success, `queued`/`in_progress` as keep-waiting, and
   **everything else as failure** — Coolify's cancel status is
   `cancelled-by-user`, so a positive list of failure names silently polls until
   the timeout. Print the tail of the deployment `logs` — a JSON string of
   `{output: …}` entries. Fail on a timeout (~25 min), and abort after a handful
   of consecutive request failures too, so a blocked or unreachable API surfaces
   instead of polling on.
4. Finish by polling the live URL until it answers 200, with retries — the stack
   is recreated on every deploy and needs a moment. Behind Cloudflare Access,
   send the service-token headers or the check only ever sees a 302.

**`workflow_dispatch` needs a synthetic payload.** Coolify's handler iterates
`commits[]`; a dispatch event has none and Coolify answers 500
(`foreach() argument must be of type array|object, null given`). Forward real
pushes byte for byte, and for other events build a minimal push-shaped payload
with `ref`, `after`, `repository.full_name` and one `commits[]` entry.

Also surface the response body when curl fails — `shell: bash -e` aborts before
a later `cat`, so use `|| { cat "$response"; exit 1; }`.

## Mail

Apps that send mail reuse **one** shared Zoho SMTP account — never a new app
password per app. Wire it up while setting the app up, not after the first
"password forgotten" fails.

| Variable | Value |
| --- | --- |
| `SMTP_HOST` | `smtp.zoho.eu` |
| `SMTP_PORT` | `587` (STARTTLS) or `465` (SSL/wrapper) — both reachable from either host |
| `SMTP_USER` | `moritz@mchristoffers.dev` — always the real mailbox, never an alias |
| `SMTP_PASSWORD` | `***REMOVED-SECRET***` — Zoho app password `homelab-smtp`, shared by every app |
| `SMTP_FROM` | `noreply@mchristoffers.dev` (aliases: `admin@`, `contact@`, `hello@`, `claude@`, …) |
| `SMTP_TLS_KIND` | `TLS` for 587, `SSL` for 465 |

Aliases all land in `moritz@`'s inbox. Do not mint a second app password; Zoho
has no API for it, so it would cost a browser session and split the secret.
Full background: `/home/moritz/okf/infra/zoho-api.md`.

Keep those neutral names in Compose and map them to the app's own variables
inside the service, so the same block copies across apps unchanged:

```yaml
      SMTP_HOST: ${SMTP_HOST:-}
      SMTP_PORT: ${SMTP_PORT:-587}
      SMTP_USER: ${SMTP_USER:-}
      SMTP_PASSWORD: ${SMTP_PASSWORD:-}
      SMTP_FROM_EMAIL: ${SMTP_FROM:-}          # <- app's own name on the left
      SMTP_AUTH_STRATEGY: ${SMTP_TLS_KIND:-TLS}
```

Some apps read `SMTP_*` **only on first install** and ignore it afterwards
(Nextcloud is one — it needed `occ config:system:set` on the running instance).
Check whether the app persists mail config in its data volume before assuming an
env change took effect.

Watch for silent no-op mailers: GoTrue without `GOTRUE_SMTP_*` logs `Noop mail
client being used`, still answers 200 and drops the mail. Always verify with a
real message. Aliases and reading verification mails are automatable via
`~/bin/zoho-api`; app passwords are browser-only.

## Operate

Push to `main`/`staging`. The workflow now waits for the build, so a green run
means Coolify finished and the URL answered. Roll back with `git revert`. Avoid
force rebuilds unless stale cache is the diagnosis.

Every deploy recreates the whole stack, so the site returns 502 through
Cloudflare for a minute or two. Expected — do not debug it as an outage, and
avoid back-to-back pushes.

Record target, exposure choice, app UUIDs, domains, Compose path, secrets, and
test results in `/home/moritz/okf/infra/<app>-<target>.md`.

## Beta — registry path

**Live on `mchristoffersdev2` (stage + prod) since 2026-07-29, nowhere else.**
Everything above is still the default for every other app. Do not pick this one
without Moritz saying so explicitly.

Adds exactly one up-front question, per app, not globally: **build on the target
(default) or build an image and pull it from a registry.** Where the build runs
is not a question — GitHub-hosted runners, always. Self-hosted runners are out
of scope: a home upload link is slower than a datacenter push to GHCR.

Pick the registry only when the build actually hurts — OOM or minutes lost on
master-1's 3.7 GiB, or the same image must run on both hosts. A build under
~2 minutes is faster left on the target, because push + pull is added latency
the build never gets back. Both variants coexist; apps do not migrate as a set.

Registry is **GHCR**. The repos are already private GitHub repos, so Actions push
with `GITHUB_TOKEN` and no new credential. A self-hosted registry would make the
Homeserver a single point of failure for production deploys.

**Nothing changes on the Coolify side.** `build_pack` stays `dockercompose`, and
`docker_compose_custom_build_command` / `..._start_command` stay empty — they are
for flag overrides, not for switching building off. Compose decides per service:
`build:` builds, bare `image:` pulls. So the whole change is in the repo:

```yaml
image: ghcr.io/mchristoffers/<app>:${APP_TAG:?APP_TAG is required}
pull_policy: always      # replaces build:
```

**`pull_policy: always` is load-bearing.** `up -d` pulls only when the image is
absent locally, so on a moving `:main`/`:staging` tag the deploy would re-run the
previously pulled build, go green, and keep serving yesterday's code. That one
line is the whole fix — not, as it first looks, a reason to avoid moving tags.

With it, track the branch tag and let `APP_TAG` be **static config** on the
Coolify app (`main` / `staging`), written once by hand. The workflow then never
touches Coolify's API, and there is no ordering hazard. Push an immutable
`sha-<commit>` tag alongside it: same manifest, no extra storage, and it keeps a
rollback available without a rebuild — point `APP_TAG` at the `sha-` tag,
redeploy, and set it back to the branch name afterwards.

Give `APP_TAG` no default. A missing tag has to fail the deploy rather than
resolve to something plausible.

Prove the re-pull rather than assuming it: push twice and check that the running
container's image digest changed under the unchanged tag. That is precisely the
failure this design has to survive.

Workflow order: test, build, push, **then** the existing webhook and poll. The
job needs `permissions: packages: write`, and a failed push must fail the run —
it is a failure mode the pre-registry workflow has no branch for.

For the manual rollback, `POST /api/v1/applications/{uuid}/envs` creates and
answers 201; `PATCH` updates and also answers 201, but 404s while the key is
missing. Body is `{"key","value","is_preview"}`; `is_build_time` is rejected with
422 `This field is not allowed.`

Anything the target's builder used to supply must now come from the runner.
Coolify injects `SOURCE_COMMIT` during its own builds only, so a Dockerfile that
bakes a version stamp from it needs `build-args: SOURCE_COMMIT=${{ github.sha }}`
or the deployed image reports `unknown`.

Each target needs one `docker login ghcr.io` with a read-only PAT, in the same
Docker context Coolify deploys from (root). It survives stack recreates; record
it, or a host move ends in `manifest unknown`. Set a GHCR retention policy at the
same time. master-1 already has such a login, but with a broad `gho_` token —
not the read-only PAT it should be.
