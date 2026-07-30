# My Skills

Personal [Agent Skills](https://agentskills.io/) for Claude Code, Codex, and
other compatible coding agents, distributed with Vercel's
[`skills`](https://github.com/vercel-labs/skills) CLI.

## Available skills

### `feature-workflow`

Completes new features autonomously in a worktree, including verification,
commits, pushes, merge, and cleanup. Planning stays with the host agent;
implementation runs through the Kimi Code CLI (`kimi`) with an OpenRouter
provider.

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
npx skills add mchristoffers/MyClaude --skill feature-workflow --global \
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
npx skills update feature-workflow --global --yes
npx skills update discover-workflows --global --yes
npx skills update deploy-coolify-compose --global --yes
npx skills update read-codex-chat --global --yes
```

List the skills in this repository without installing them:

```sh
npx skills add mchristoffers/MyClaude --list
```

## Activate the workflow persistently

Copy the block from [`AGENTS_SNIPPETS.md`](AGENTS_SNIPPETS.md)
into any persistent instruction scope where the workflow should apply:

- Repository-wide Codex instructions: `AGENTS.md`
- User-wide Codex instructions: `~/.codex/AGENTS.md`
- Repository-wide Claude Code instructions: `CLAUDE.md`
- User-wide Claude Code instructions: `~/.claude/CLAUDE.md`
- A supported machine-managed instruction file

The block mentions the skill by name and contains no home-relative, absolute, or
agent-specific skill path. Each agent resolves its own installed skill location.

When a repository already uses `AGENTS.md` as the shared source of instructions,
Claude Code can consume the same file through a minimal `CLAUDE.md`:

```markdown
@AGENTS.md
```

## Layout

```text
AGENTS_SNIPPETS.md
skills/
├── deploy-coolify-compose/
│   ├── SKILL.md
│   └── agents/
│       └── openai.yaml
├── discover-workflows/
│   ├── SKILL.md
│   └── agents/
│       └── openai.yaml
├── feature-workflow/
│   ├── SKILL.md
│   └── agents/
│       └── openai.yaml
└── read-codex-chat/
    ├── SKILL.md
    └── agents/
        └── openai.yaml
```
