This repository contains my central workflows.
Keep skill text as short as possible.

This repo is dual-published:

- As **`MyClaude`**, a native Claude Code plugin (`.claude-plugin/plugin.json`).
- As **`myclaude`**, a cross-vendor [Agent Plugins](https://agent-plugins.org)
  package (root `plugin.json`) for ChatGPT, Codex, Cursor, VS Code, etc.

# Standard

## Agent Plugins 1.0.0

The cross-vendor package in this repo (root `plugin.json`) targets the
[Agent Plugins](https://agent-plugins.org) spec — the open packaging standard
published 2026-08-06 by a Technical Steering Committee of Amazon, Cursor
(Anysphere), GitHub, Microsoft, OpenAI, and Vercel (which initiated it).

A plugin is a directory with a root `plugin.json` manifest plus two optional,
fixed-location component dirs — never declared inline in `plugin.json`:

- `skills/` — Agent Skills, one subdirectory each.
- `mcp.json` — MCP server configs (stdio, Streamable HTTP, or legacy
  HTTP+SSE), each entry with an explicit `type`.

## API skills: download the vendor's OpenAPI spec as-is

When a skill is about using an API, download the vendor's official OpenAPI
spec (or equivalent published schema) into `references/` verbatim — don't
split it into per-resource files, re-summarize it, or build a custom index
over it, even if that would be smaller or more convenient to grep. Large is
fine; a plain `jq`/`grep` over the native file beats a bespoke abstraction
that can drift from the source or drop details.

Auth for the API always comes from an environment variable (e.g.
`FOO_API_TOKEN`) that Moritz already has set — never a hardcoded key, a file
on disk, or a prompt asking him to paste one in.
