---
name: research-gemini
description: Do online research/web search by delegating to Gemini CLI as an agent, instead of the built-in WebSearch tool. Use for ANY online lookup — current info, docs, sources, "what's the latest on X".
---

> Source: `~/git/mchristoffers/MyClaude/skills/research-gemini/SKILL.md`. Learned
> something here? Edit it there and reinstall (that repo's AGENTS.md) —
> never edit the installed copy, it is overwritten without warning.

# Web research via Gemini CLI

Don't use the built-in `WebSearch` tool. Instead delegate the research
question to Gemini CLI, which runs as its own agent with a built-in web
search tool — it can issue multiple searches, follow links, and synthesize
an answer on its own:

```sh
scripts/research.sh "<question>"
```

Phrase `<question>` as a real question/task for an agent ("what's the
current stable version of X and when did it release, with sources"), not a
bag of keywords — Gemini CLI will plan its own searches.

It prints Gemini's final synthesized answer to stdout. Treat it like a
research assistant's report: cite it, but fetch a source directly (e.g. with
`WebFetch`) if you need to verify a specific claim or need full page content.

Override the model with `GEMINI_RESEARCH_MODEL` (e.g. `gemini-2.5-pro` for
harder research; default is Gemini CLI's own default model).

## Setup (one-time, Moritz only)

Gemini CLI auths via Google OAuth, which needs an interactive browser login
and can't be scripted headlessly. If `scripts/research.sh` fails with an
auth error, tell Moritz to run `gemini` (no args) in his own terminal once,
pick "Login with Google" (free tier — no billing needed), and trust the
folder if prompted. After that, headless `-p` calls reuse the stored
credentials in `~/.gemini/`.
