---
name: deploy-master1-compose
description: "Deploy and maintain production applications on master-1 Coolify from private GitHub repositories that ship a production Docker Compose file using upstream images. Use for creating a master-1 application, connecting a private repo through the Coolify GitHub App, configuring domains, secrets and volumes, deploying, updating, rolling back, or retiring it. Never use for the separate Homeserver Coolify."
---

# Workflow

Git is the source of truth. Use build pack `dockercompose` through Coolify's
GitHub App; never add a Dockerfile or GHCR pipeline.

1. Read [references/topology.md](references/topology.md) before any API or server
   action, and [references/lifecycle.md](references/lifecycle.md) before creating,
   changing, rolling back, or deleting anything.
2. Resolve repo, branch, Compose path, public service, internal port, domain,
   variable names, and volume expectations. Ask only when a missing choice
   materially changes production, especially the domain.
3. Run the read-only preflight in `lifecycle.md`; resolve every error first.
4. Create the project, application, variables, and domain in that order. Deploy
   last, then verify HTTPS, health, and volume attachment.
5. Maintain by changing the repo and letting the webhook deploy. Back up before
   schema-affecting upgrades. Roll back through Git, not through data.
6. Record durable topology in `/home/moritz/okf/infra/<app>-master1.md`, update
   the parent `index.md`, and append a dated `log.md` entry.
7. Report repo/branch/commit, Coolify UUID, domain, deploy and health result,
   persistence state, and rollback point.

Treat references as known topology, not live state; verify UUIDs, versions, DNS,
and repo access read-only before mutation. Never print secret values. Never route
to Homeserver Coolify as a fallback, and never add either host to the other.
