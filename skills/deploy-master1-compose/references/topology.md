# Master-1 production topology

## Required target

- Host: Hetzner VPS `master-1`
- Historical public IPv4: `178.105.233.193`; verify live state with `hcloud`
- SSH alias: `master-1`, user `root`, dedicated key configured in `~/.ssh/config`
- Coolify: self-hosted production instance on master-1
- Internal API: `http://127.0.0.1:8000/api/v1`
- Public dashboard: `https://coolify.mchristoffers.dev`, protected by Cloudflare
  Access
- API token file: `/home/moritz/.bbj_coolify_token`, mode 600; read it only from
  the helper and never print it

The supported API route is an SSH local forward to master-1, then a local request
to port 8000. The helper implements this so the bearer token remains local.

## Hard separation rule

The Homeserver also runs Coolify at `192.168.178.112:8000` and
`coolify-home.mchristoffers.dev`. It is a separate control plane and must never
manage master-1. Never move a production deployment there as an implicit
fallback, and never add either host as a server in the other Coolify.

## Sources of current truth

Read these progressively when needed:

- `/home/moritz/okf/index.md`
- `/home/moritz/okf/infra/cloudflare-account.md`
- `/home/moritz/okf/infra/coolify-homeserver.md`
- `/home/moritz/.claude/projects/-home-moritz-git-mchristoffers-agents/memory/coolify-api-access.md`
- `/home/moritz/.claude/projects/-home-moritz-git-mchristoffers-mealie/memory/coolify-infra.md`

The OKF credential documents contain plaintext secrets by owner choice. Read only
the exact field required for an authorized action. Never print whole credential
files, include them in diffs, or copy values into the skill.

## Existing production examples

BeautyByJulia and Mealie historically run on this instance. Use them only to
understand patterns; do not mutate their resources during another application's
workflow.
