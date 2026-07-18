# My Skills

Personal [Agent Skills](https://agentskills.io/) that can be installed in Claude
Code, Codex, and other supported coding agents with Vercel's
[`skills`](https://github.com/vercel-labs/skills) CLI.

## Install

Install all skills globally for Claude Code and Codex:

```sh
npx skills add mchristoffers/MyClaude --skill '*' --global \
  --agent claude-code --agent codex
```

List the available skills without installing them:

```sh
npx skills add mchristoffers/MyClaude --list
```

## Layout

```text
skills/
└── example-skill/
    ├── SKILL.md
    └── agents/
        └── openai.yaml
```

Each skill is a self-contained directory whose `SKILL.md` contains YAML
frontmatter with its `name` and `description`, followed by the instructions an
agent loads when the skill is used.

Create another skill with:

```sh
cd skills
npx skills init my-new-skill
```
