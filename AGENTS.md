This repository contains my central workflows.
Keep skill text as short as possible.
Moritz's central knowledge base uses OKF v0.2; see `/home/moritz/okf/reference/okf-spec.md`.

After changing a skill in this repo, commit and push the repo change, then
reinstall the changed skill globally for Codex and Claude Code:

```sh
npx skills add . --skill <skill-name> --global --agent codex --agent claude-code --copy --yes
```

Installed skills do not auto-update from live edits on main.
