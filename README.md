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

### `deploy-master1-compose`

Deploys and maintains private-repository Docker Compose applications on the
master-1 Coolify instance, with optional `staging` beside `main`. Coolify clones
with a deploy key and builds on master-1; GitHub Actions only run checks and
send signed push payloads through Cloudflare Access to Coolify's manual GitHub
webhook. Domain bindings are exact hostnames; other subdomains may belong to
other apps through wildcard DNS on the zone.

## Install

Install a skill globally for Claude Code and Codex:

```sh
npx skills add mchristoffers/MyClaude --skill feature-workflow --global \
  --agent claude-code --agent codex

npx skills add mchristoffers/MyClaude --skill discover-workflows --global \
  --agent claude-code --agent codex

npx skills add mchristoffers/MyClaude --skill deploy-master1-compose --global \
  --agent claude-code --agent codex
```

Update the installed skill after changes are published here:

```sh
npx skills update feature-workflow --global --yes
npx skills update discover-workflows --global --yes
npx skills update deploy-master1-compose --global --yes
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
├── deploy-master1-compose/
│   ├── SKILL.md
│   └── agents/
│       └── openai.yaml
├── discover-workflows/
│   ├── SKILL.md
│   └── agents/
│       └── openai.yaml
└── feature-workflow/
    ├── SKILL.md
    └── agents/
        └── openai.yaml
```
