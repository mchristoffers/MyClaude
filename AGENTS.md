This repository contains my central workflows.
Keep skill text as short as possible.
Moritz's central knowledge base uses OKF v0.2; see `/home/moritz/okf/reference/okf-spec.md`.
SKILL.md frontmatter notation: see [reference/skill-frontmatter.md](reference/skill-frontmatter.md).

This repo is dual-published:

- As **`MyClaude`**, a native Claude Code plugin (`.claude-plugin/plugin.json`).
- As **`myclaude`**, a cross-vendor [Agent Plugins](https://agent-plugins.org)
  package (root `plugin.json`) for ChatGPT, Codex, Cursor, VS Code, etc.

Both manifests point at the same `skills/` directory, so a skill only has to be
written once.

## Skills are edited here, never where they are installed

`~/.claude/skills/MyClaude/` (Claude Code) and `~/.agents/skills/<name>/`
(Codex, via `npx skills`) are build output. An edit made there is invisible to
git and is destroyed by the next install — that has already swallowed a day of
hard-won notes once.

So: learned something about a skill while working in *any* repo? Write it here,
in the same session, and reinstall it:

```sh
cd /home/moritz/git/mchristoffers/MyClaude
# edit skills/<skill-name>/SKILL.md
git commit -am '<what changed>' && git push

# Claude Code (user scope, whole plugin as one unit):
rm -rf ~/.claude/skills/MyClaude
mkdir -p ~/.claude/skills/MyClaude
rsync -a --exclude='.git' --exclude='.worktrees' . ~/.claude/skills/MyClaude/

# Codex (per skill, unchanged):
npx skills add . --skill <skill-name> --global --agent codex --copy --yes
```

Nothing propagates by itself — not a saved file, not a commit, not a push. Only
those commands move text into the installed copies. Leaving them out is how the
next agent ends up working from stale instructions.

`rsync`/`--copy` is deliberate: a symlink into this repo (or into Codex's copy)
hides drift instead of preventing it. Everything installed must be byte
identical to the repo after an install; `diff -rq` proves it. Restart Claude
Code (or run `claude plugin list` in a new session) to pick up skill-content
changes made this way — a running session keeps its already-loaded copy.

Drifted already? Diff repo vs `~/.claude/skills/MyClaude` vs `~/.agents/skills`,
merge every side into the repo **first**, then reinstall — the install keeps
only what the repo has.

Legacy: replace a leftover `/home/moritz/.codex/skills/<name>` with
`/home/moritz/.agents/skills/<name>` after installing.
