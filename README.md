# My Skills

Personal [Agent Skills](https://agentskills.io/) for Claude Code, Codex, and
other compatible coding agents, distributed with Vercel's
[`skills`](https://github.com/vercel-labs/skills) CLI.

## Available skill

### `feature-workflow`

Completes every Git-repository change autonomously in a worktree, including
verification, commits, pushes, merge, and cleanup.

## Install

Install the skill globally for Claude Code and Codex:

```sh
npx skills add mchristoffers/MyClaude --skill feature-workflow --global \
  --agent claude-code --agent codex
```

Update the installed skill after changes are published here:

```sh
npx skills update feature-workflow --global --yes
```

List the skills in this repository without installing them:

```sh
npx skills add mchristoffers/MyClaude --list
```

## Activate the workflow persistently

Copy the block from [`templates/feature-workflow.md`](templates/feature-workflow.md)
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
skills/
└── feature-workflow/
    ├── SKILL.md
    └── agents/
        └── openai.yaml
templates/
└── feature-workflow.md
```
