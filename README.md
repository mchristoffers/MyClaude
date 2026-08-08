# MyClaude

Personal [Agent Skills](https://agentskills.io/) for Claude Code, Codex, and
other compatible coding agents. Published two ways from the same `skills/`
tree:

- **Claude Code plugin** `myclaude` (`.claude-plugin/plugin.json`) — installs
  as one unit via Claude Code's native plugin system.
- **[Agent Plugins](https://agent-plugins.org)** `myclaude` (root
  `plugin.json`) — the OpenAI/Microsoft/Amazon/Cursor/Vercel cross-vendor
  standard, for ChatGPT, Codex, Cursor, VS Code, GitHub Copilot, Kiro.

Individual skills can still be pulled with Vercel's
[`skills`](https://github.com/vercel-labs/skills) CLI (used below for Codex,
which has no native plugin support yet).

## Available skills

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

### Claude Code (native plugin, whole bundle)

Via a marketplace add + install:

```sh
claude plugin marketplace add mchristoffers/MyClaude
claude plugin install myclaude@MyClaude --scope user
```

Or, without a marketplace, as a local skills-directory plugin (what this repo
uses for Moritz's own machine — see `AGENTS.md`):

```sh
mkdir -p ~/.claude/skills/MyClaude
rsync -a --exclude='.git' --exclude='.worktrees' \
  /path/to/MyClaude/ ~/.claude/skills/MyClaude/
```

It then auto-loads next session as `myclaude@skills-dir` — no install step.
Verify with `claude plugin list` / `claude plugin details myclaude@skills-dir`.

### Codex, or any other Agent Plugins-compatible client

Point the client at this repo (it carries a spec-compliant root `plugin.json`)
per that client's own plugin-install flow, or install a single skill directly
with Vercel's CLI:

```sh
npx skills add mchristoffers/MyClaude --skill deploy-coolify-compose --global \
  --agent codex

npx skills add mchristoffers/MyClaude --skill discover-workflows --global \
  --agent codex

npx skills add mchristoffers/MyClaude --skill read-codex-chat --global \
  --agent codex
```

Update after changes are published here:

```sh
npx skills update deploy-coolify-compose --global --yes
npx skills update discover-workflows --global --yes
npx skills update read-codex-chat --global --yes
```

List the skills in this repository without installing them:

```sh
npx skills add mchristoffers/MyClaude --list
```

## Layout

```text
.claude-plugin/
└── plugin.json          # Claude Code native plugin manifest (name: myclaude)
plugin.json               # Agent Plugins 1.0.0 manifest (cross-vendor)
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
└── read-codex-chat/
    ├── SKILL.md
    └── agents/
        └── openai.yaml
```
