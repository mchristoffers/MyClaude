# My Skills

Personal [Agent Skills](https://agentskills.io/) for Claude Code, Codex, and
other compatible coding agents, distributed with Vercel's
[`skills`](https://github.com/vercel-labs/skills) CLI.

## Available skills

### `kimi`

Runs the Kimi Code CLI to implement a given plan or task purely as code —
nothing else: no planning, no worktree or branch management, no committing, no
merging. Invoked explicitly by name; never model-invoked.

### `discover-workflows`

Analyzes chats and suggests repeated, stable workflows as new Agent Skills.

### `read-codex-chat`

Reads a past Codex conversation from its local rollout file, extracting only the
user and assistant message texts so the megabytes of tool-call and reasoning
events never reach the context window.

### `deploy-coolify-compose`

Deploys and maintains private-repository Docker Compose applications on either
Coolify instance — master-1 (Hetzner VPS, public production) or the Homeserver
(homelab) — with optional `staging` beside `main`. The target, the domain, and
ready-made image versus own Dockerfile build are settled up front. Coolify
clones with a repo-scoped deploy key and builds on the target host; GitHub
Actions only run checks and send signed push payloads through Cloudflare Access
to Coolify's manual GitHub webhook. master-1 routes through its Traefik and
wildcard DNS; the Homeserver has no proxy and routes through the homelab
cloudflared tunnel with an explicit CNAME.

## Install

Install a skill globally for Claude Code and Codex:

```sh
npx skills add mchristoffers/MyClaude --skill kimi --global \
  --agent claude-code --agent codex

npx skills add mchristoffers/MyClaude --skill discover-workflows --global \
  --agent claude-code --agent codex

npx skills add mchristoffers/MyClaude --skill deploy-coolify-compose --global \
  --agent claude-code --agent codex

npx skills add mchristoffers/MyClaude --skill read-codex-chat --global \
  --agent claude-code --agent codex
```

Update the installed skill after changes are published here:

```sh
npx skills update kimi --global --yes
npx skills update discover-workflows --global --yes
npx skills update deploy-coolify-compose --global --yes
npx skills update read-codex-chat --global --yes
```

List the skills in this repository without installing them:

```sh
npx skills add mchristoffers/MyClaude --list
```

## Layout

```text
AGENTS.md
reference/
└── skill-frontmatter.md
skills/
├── deploy-coolify-compose/
│   ├── SKILL.md
│   └── agents/
│       └── openai.yaml
├── discover-workflows/
│   ├── SKILL.md
│   └── agents/
│       └── openai.yaml
├── kimi/
│   └── SKILL.md
└── read-codex-chat/
    ├── SKILL.md
    └── agents/
        └── openai.yaml
```
