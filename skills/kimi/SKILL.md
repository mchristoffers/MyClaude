---
name: kimi
description: "Runs the Kimi Code CLI to implement a given plan or task purely as code — nothing else (no planning, no git, no merging)."
disable-model-invocation: true
---

> Source: `~/git/mchristoffers/MyClaude/skills/kimi/SKILL.md`. Learned
> something here? Edit it there and reinstall (that repo's AGENTS.md) —
> never edit the installed copy, it is overwritten without warning.

# Kimi Code CLI

Pure wrapper around the Kimi Code CLI for code implementation. Nothing else —
no planning, no worktree/branch management, no committing, no merging. The
caller is responsible for all of that.

Run:

```sh
kimi --quiet -w <worktree-or-repo-path> -p '<plan or task description>'
```

## Setup (once)

Install with `uv tool install --python 3.13 kimi-cli`, then point
`~/.kimi/config.toml` at OpenRouter:

```toml
default_model = "kimi-k2.7-code"

[providers.openrouter]
type = "openai_legacy"
base_url = "https://openrouter.ai/api/v1"
api_key = "<OPENROUTER_API_KEY>"

[models."kimi-k2.7-code"]
provider = "openrouter"
model = "moonshotai/kimi-k2.7-code"
max_context_size = 262144
```
