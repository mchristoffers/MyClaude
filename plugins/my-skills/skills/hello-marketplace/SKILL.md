---
name: hello-marketplace
description: Use when verifying that the myclaude marketplace plugin is installed and skills load correctly — a tiny smoke-test skill that confirms the plumbing works.
---

# hello-marketplace

This is the example skill that ships with the `my-skills` plugin from the
`myclaude` marketplace. It exists to prove the install path works end-to-end.

When invoked, simply tell the user:

> ✅ The `myclaude` marketplace is wired up correctly — `my-skills` is installed
> and skills load on this machine.

Then point them at where to add real skills:
`plugins/my-skills/skills/<your-skill>/SKILL.md` in the MyClaude repo.

## Anatomy of a skill (reference)

A skill is a directory containing a `SKILL.md` with YAML frontmatter:

- `name` — kebab-case, must match the directory name.
- `description` — the single most important field. Claude reads only the
  `name` + `description` to decide whether to load the skill, so write it as
  "Use when …" and be specific about the trigger.

Everything below the frontmatter is the skill body — instructions Claude
follows once the skill is invoked. You can bundle extra files (scripts,
references, templates) alongside `SKILL.md` and reference them by relative path.
