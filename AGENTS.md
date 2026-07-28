This repository contains my central workflows.
Keep skill text as short as possible.
Moritz's central knowledge base uses OKF v0.2; see `/home/moritz/okf/reference/okf-spec.md`.

## Skills are edited here, never where they are installed

`~/.claude/skills/<name>/` (Claude Code) and `~/.agents/skills/<name>/` (Codex)
are build output. An edit made there is invisible to git and is destroyed by the
next install — that has already swallowed a day of hard-won notes once.

So: learned something about a skill while working in *any* repo? Write it here,
in the same session, and install it:

```sh
cd /home/moritz/git/mchristoffers/MyClaude
# edit skills/<skill-name>/SKILL.md
git commit -am '<what changed>' && git push
npx skills add . --skill <skill-name> --global --agent codex --agent claude-code --copy --yes
```

Nothing propagates by itself — not a saved file, not a commit, not a push. Only
that last command moves text into the installed copies. Leaving it out is how
the next agent ends up working from stale instructions.

`--copy` is deliberate: without it, Claude Code only gets a symlink into Codex's
copy, which hides drift instead of preventing it. All three trees must be byte
identical after an install; `diff -rq` proves it.

Drifted already? Diff all three (repo, `~/.claude`, `~/.agents`), merge every
side into the repo **first**, then install — the install keeps only what the
repo has.

Legacy: replace a leftover `/home/moritz/.codex/skills/<name>` with
`/home/moritz/.agents/skills/<name>` after installing.
