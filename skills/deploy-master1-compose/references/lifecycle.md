# Coolify private-repository Compose lifecycle

## Read-only preflight

Run all of these before any mutation:

1. Confirm the local repository and remote with `git` and `gh`; require GitHub
   visibility `PRIVATE` and the intended branch to exist remotely.
2. Run `scripts/validate-compose.sh <repo> <compose-path> [env-example]`. Resolve
   every error and explain any warning before production deployment.
3. Check `hcloud server describe master-1 -o json`. Stop if the server is not
   running or either primary IP is provider-blocked.
4. Run `scripts/master1-api.sh GET /teams` and read-only inventory calls for
   `/servers`, `/projects`, `/github-apps`, `/applications`, and `/services`.
5. Select only master-1's own localhost server in master-1's Coolify.
6. Verify the selected Coolify GitHub App can read the private repository. If
   authorization is absent, pause for the user to grant it in GitHub.
7. Check the requested DNS name for conflicts and inspect existing Coolify
   domains before creation.

If SSH/API connectivity fails, report the precise failed layer. Never fall back
to Homeserver Coolify.

## Creation order

State the exact target and effect before each mutation. Keep creation reversible
and deploy last:

1. Create or reuse a dedicated project and its `production` environment.
2. Create the application with `POST /applications/private-github-app` using the
   discovered project, server, environment, and GitHub App UUIDs.
3. Re-read the created resource and verify repository, branch, build pack,
   Compose location, and destination before continuing.
4. Configure variables through the application environment API. Generate strong
   secrets when authorized, pass them via a temporary mode-600 JSON file, then
   remove it.
5. Configure the public domain only for the intended service and internal port.
   Keep databases, caches, migration jobs, and admin ports private.
6. Create or update the Cloudflare record only when authorized.
7. Trigger the first deployment, poll status, then verify HTTPS, health, and
   persistent volume attachment.

## Maintenance and retirement

- Inspect the live resource and deployment history before changing it.
- Make Compose/image changes in the repository, validate, commit, and push. Let
  the webhook auto-deploy the production branch.
- Prefer explicit immutable upstream image versions for controlled upgrades.
- Back up database and persistent volumes before schema-affecting upgrades.
- Update variables through Coolify, then redeploy and verify.
- Diagnose failures from deployment logs and container health before retrying; do
  not loop forced deployments.
- To retire, stop first. Delete only with explicit confirmation of whether
  volumes and configuration must be preserved. Default to preserving both.

## Official interfaces

- Private GitHub App creation:
  `POST /applications/private-github-app`
- Application inventory/detail/update/delete:
  `GET /applications`, `GET|PATCH|DELETE /applications/{uuid}`
- Environment variables:
  `GET /applications/{uuid}/envs`,
  `PATCH /applications/{uuid}/envs/bulk`
- Deploy/start:
  `GET|POST /applications/{uuid}/start?force=false`
- Generic deploy webhook:
  `GET /deploy?uuid={uuid}&force=true`
- GitHub integrations: `GET /github-apps`
- Discovery: `GET /teams`, `/servers`, `/projects`

Verify request fields against the live Coolify version or current official API
reference before every creation workflow:

- https://coolify.io/docs/api-reference/api/applications/create-private-github-app-application
- https://coolify.io/docs/applications/build-packs/docker-compose
- https://coolify.io/docs/knowledge-base/docker/compose

## Creation payload shape

Construct JSON with `jq`, not string concatenation. Discover every UUID live.
Start from this shape and confirm it against the installed version:

```json
{
  "project_uuid": "DISCOVER",
  "server_uuid": "DISCOVER",
  "environment_name": "production",
  "github_app_uuid": "DISCOVER",
  "git_repository": "mchristoffers/example",
  "git_branch": "main",
  "ports_exposes": "3000",
  "build_pack": "dockercompose",
  "name": "example",
  "base_directory": "/",
  "docker_compose_location": "/docker-compose.production.yml",
  "is_auto_deploy_enabled": true,
  "is_force_https_enabled": true,
  "autogenerate_domain": false,
  "instant_deploy": false
}
```

Do not send `force_domain_override=true` unless the user explicitly chooses to
replace a verified conflicting route.

## Compose contract

- Use official/upstream `image:` entries; reject custom `build:` entries for this
  workflow.
- Use named volumes for persistent application and database data.
- Use service DNS names internally and omit custom networks unless required.
- Do not publish database/cache ports on the host.
- Express Coolify-editable values as `${NAME}`, defaults as `${NAME:-value}`, and
  required secrets as `${NAME:?message}`.
- Mark one-shot migration jobs `exclude_from_hc: true` when supported by the live
  Coolify version. Stock Docker Compose does not recognize this Coolify extension.
- Assign the external URL to the actual public service and its internal port.

## Secrets

Generate secrets with `openssl rand -base64 36` or an equivalent CSPRNG. Store
payload JSON in `mktemp`, set mode 600 before writing, use it once, then delete it
with a trap. Keep values out of command arguments, terminal output, Git, OKF, and
final responses.

After bulk update, re-read only variable keys and metadata. Do not request or
display secret values merely to verify them.

## Domain handling on older master-1 Coolify

First use the supported `docker_compose_domains`/application update API and
verify persistence with a fresh GET plus deployable Compose inspection. On
Coolify 4.1.1, a Compose service FQDN may fail to persist because its source of
truth is `service_applications.fqdn`.

Database fallback is last resort:

1. Obtain explicit approval for direct Coolify database modification.
2. Back up the Coolify database.
3. Query the application and service rows read-only and show sanitized targets.
4. Update only the exact matching `service_applications` row in a transaction.
5. Re-read the row, redeploy, and verify Traefik routing.
6. Restore from backup if verification fails.

Never use this fallback based only on remembered IDs or table structure.

## DNS and TLS

Check the Cloudflare zone and existing records before mutation. For direct
master-1 Traefik/Let's Encrypt HTTP-01, create DNS-only A/AAAA records unless the
live topology explicitly uses a tunnel or DNS challenge. Confirm the hostname
resolves to master-1 before expecting certificate issuance.

## Verification and rollback

Verify in layers: API deployment state, container state/health, proxy route,
HTTPS response, application-specific health/version endpoint, then a persistence
check if safe. Capture the pre-change commit/image tag as the rollback point.

Rollback configuration through Git first. Treat database migrations separately:
an older image is not a safe rollback when its schema is incompatible. Restore
data only from an identified backup with explicit authorization.
