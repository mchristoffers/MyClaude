# MyClaude

My personal [Claude Code](https://claude.com/claude-code) marketplace — skills,
commands and agents, versioned in one repo and synced across all my machines.

## Layout

```
MyClaude/
├── .claude-plugin/
│   └── marketplace.json        # the marketplace manifest (lists plugins)
└── plugins/
    └── my-skills/              # one plugin = one installable bundle
        ├── .claude-plugin/
        │   └── plugin.json     # plugin manifest
        └── skills/
            └── hello-marketplace/
                └── SKILL.md     # example skill (smoke test)
```

A **marketplace** is just this git repo + `marketplace.json`. It lists one or
more **plugins**. Each plugin can contain `skills/`, `commands/`, `agents/`,
`hooks/`, etc. Skills live under `plugins/<plugin>/skills/<skill>/SKILL.md`.

## Install on a new machine

```sh
/plugin marketplace add mchristoffers/MyClaude
/plugin install my-skills@myclaude
```

`mchristoffers/MyClaude` is the GitHub `owner/repo` shorthand; a full git URL or
local path works too. `myclaude` is the marketplace `name` from
`marketplace.json` (not the repo name).

### Or: auto-enable from settings (no manual install per machine)

Add this to your synced `~/.claude/settings.json` so a freshly-cloned machine
provisions itself:

```jsonc
{
  "extraKnownMarketplaces": {
    "myclaude": {
      "source": { "source": "github", "repo": "mchristoffers/MyClaude" }
    }
  },
  "enabledPlugins": {
    "my-skills@myclaude": true
  }
}
```

## Update everywhere

After pushing changes here:

```sh
/plugin marketplace update myclaude
```

Existing installs pick up the new skills on next launch.

## Add a new skill

1. `mkdir -p plugins/my-skills/skills/<skill-name>`
2. Create `plugins/my-skills/skills/<skill-name>/SKILL.md` with frontmatter:

   ```markdown
   ---
   name: <skill-name>
   description: Use when … (be specific — this is how Claude decides to load it)
   ---

   <instructions Claude follows once the skill is invoked>
   ```

3. Commit & push, then `/plugin marketplace update myclaude` on each machine.

Want to split skills into themed bundles? Add another plugin directory under
`plugins/` and register it in `marketplace.json`.
