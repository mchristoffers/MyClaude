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
no planning, no worktree/branch management, no committing, no merging, and no
verification: Kimi does not run tests and does not review its own work. The
caller is responsible for all of that.

Kimi shares no context with you. Everything it needs goes into the prompt, and
everything it learned comes back through a file — nothing else survives the run.

## Prepare before running

1. **Plan file** — write the package to `.tasks/<nn>-<slug>-plan.md` in the repo:
   goal, affected components, steps, acceptance criteria, out of scope, risks.
   One work package per file; split anything bigger.
2. **File list** — grep out the 2–6 files it will touch and the types/APIs it must
   not break. You do the searching, not Kimi. Leave the test files out unless the
   plan is to write them.
3. **Repo map** — one line per relevant module (`path — what it does, key
   exports`). A dozen lines beat a directory dump. "Unfamiliar" means unfamiliar
   *to Kimi*: it starts blank every run, so anything you know from your own
   session has to be restated here. Wrote the same map a third time? Park it in
   this repo's auto memory (`~/.claude/projects/<repo>/memory/`) as a topic file
   and paste from there — not in okf, which stays free of per-repo detail.

Never `-p 'find out what you need'`. An unscoped run re-reads the repo at every
step and burns more than the cheaper model saves.

## Run

```sh
kimi --quiet -w <worktree-or-repo-path> -p 'Implement the plan in .tasks/<nn>-<slug>-plan.md.

Files in scope:
  <path>   # change this
  <path>   # types/API — read only, do not change

Repo map:
  <path> — <what it does, key exports>

Do not explore beyond these files. Implement only: do not run tests, do not
verify or review your own work, do not commit, branch or merge.
When done, write .tasks/<nn>-<slug>-progress.md: what changed per file,
decisions taken, and anything you could not implement.'
```

One invocation per work package. Never chain packages into one run, and keep the
prompt prefix byte-identical across retries of the same package — a stable prefix
is what the provider-side prompt cache keys on.

## After the run

Verification starts here, not inside Kimi. Read the progress file, not the
transcript, then check the work yourself: run the tests, review the diff.

```sh
git diff --stat
```

Pull full content into your context only for what the diff actually touched.

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
