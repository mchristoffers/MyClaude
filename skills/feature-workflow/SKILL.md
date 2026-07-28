---
name: feature-workflow
description: "Use only when implementing a new product or code feature in a Git repository. Do not use for bug fixes, refactors, maintenance, documentation, configuration, or read-only tasks. Complete the feature autonomously in a worktree through verification, merge, push, and cleanup."
---

# Workflow

Always use a worktree for new features.

- Ask once upfront which planner and implementer to use, offering the defaults below.
- Commit every existing change to the default branch with a suitable message and push before starting.
- Inspect the repository and reuse or create a worktree.
- Create an ignored `.agent-work/PROGRESS.md` and keep it current.
- Create a feature branch using the repository's naming rules.
- Plan the implementation with the chosen planner, never through OpenRouter.
- Implement the plan only in the worktree with the chosen implementer.
- Run the required baseline and final tests; fix failures.
- Commit the intended changes and push the feature branch.
- Merge into the default branch and push it without asking.
- Delete the feature branch, progress file, and worktree after a successful push.

After that one choice, complete the workflow autonomously. Never ask for merge
approval, overwrite user changes, or force destructive Git operations.

# Planner and implementer

Defaults:

- Plan in a subagent on the host agent's own model at its highest reasoning
  effort:
  - Claude Code: Opus 5 subagent
  - Codex: `codex exec -m gpt-5.6-sol -c model_reasoning_effort="xhigh"`
- Implement with the Kimi Code CLI: `kimi --quiet -w <worktree> -p '<plan>'`

# Kimi Code CLI

Install once with `uv tool install --python 3.13 kimi-cli`, then point
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
