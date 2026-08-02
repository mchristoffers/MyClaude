# SKILL.md format reference

> Source: https://agentskills.io/specification (fetched 2026-08-02) — the
> open Agent Skills spec, originally published by Anthropic, that
> `npx skills` / skills.sh (Vercel) and Claude Code both build on. This is
> the notation we actually author in this repo.

## Directory structure

```
skill-name/
├── SKILL.md          # Required: metadata + instructions
├── scripts/          # Optional: executable code
├── references/       # Optional: documentation
├── assets/           # Optional: templates, resources
└── ...
```

## Frontmatter (base spec)

| Field | Required | Constraints |
|---|---|---|
| `name` | Yes | Max 64 chars. Lowercase letters, digits, hyphens only. No leading/trailing/consecutive hyphens. Must match the parent directory name. |
| `description` | Yes | Max 1024 chars, non-empty. What the skill does *and* when to use it — include the keywords an agent needs to match on. |
| `license` | No | License name or reference to a bundled license file. |
| `compatibility` | No | Max 500 chars. Environment requirements (target product, system packages, network access). Most skills don't need this. |
| `metadata` | No | Arbitrary string→string map for extra properties outside the spec. |
| `allowed-tools` | No | Space-separated string of pre-approved tools. Experimental, support varies by client. |

```yaml
---
name: pdf-processing
description: Extract PDF text, fill forms, merge files. Use when handling PDFs.
license: Apache-2.0
metadata:
  author: example-org
  version: "1.0"
---
```

## Progressive disclosure

Agents load skills in three stages, which is the reason to keep bodies short:

1. **Metadata** (~100 tokens): `name` + `description`, loaded at startup for every skill.
2. **Instructions** (< 5000 tokens recommended): the full `SKILL.md` body, loaded once the skill activates.
3. **Resources**: `scripts/`, `references/`, `assets/` files, loaded only as needed.

Keep `SKILL.md` under 500 lines; push detail into `references/`.

## Validation

```sh
skills-ref validate ./my-skill
```

From https://github.com/agentskills/agentskills.

## Claude Code extensions (not in the base spec)

Claude Code recognizes extra frontmatter fields the base spec doesn't define —
these only take effect where Claude Code reads the installed copy
(`~/.claude/skills/...`), not necessarily for Codex or other clients reading
the same file via `npx skills add`. The one we currently rely on:

- `disable-model-invocation: true` — only the user can invoke the skill
  (`/name`); Claude never auto-triggers it. Used by [skills/kimi](../skills/kimi/SKILL.md).

Full list: https://code.claude.com/docs/en/skills#frontmatter-reference
