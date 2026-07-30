---
name: read-codex-chat
description: Read a past Codex chat from its local rollout file, loading only the user and assistant message texts. Use when asked to find, read, recap, or look something up in an earlier Codex or ChatGPT-Codex conversation.
---

> Source: `~/git/mchristoffers/MyClaude/skills/read-codex-chat/SKILL.md`. Learned
> something here? Edit it there and reinstall (that repo's AGENTS.md) —
> never edit the installed copy, it is overwritten without warning.

# Read a Codex chat

Never `cat`, `Read`, or grep a whole rollout file into context. They run 1 MB+
and are ~95% events (tool calls, tool output, reasoning, token counts). The
message texts alone are ~20 KB and carry the entire conversation.

## Locate

Sessions: `~/.codex/sessions/<YYYY>/<MM>/<DD>/rollout-<ts>-<id>.jsonl`, older ones
`~/.codex/archived_sessions/`. `~/.codex/session_index.jsonl` maps
`thread_name` → `id`, but covers only recent threads.

By title:

```sh
grep -i 'TITLE' ~/.codex/session_index.jsonl
find ~/.codex/sessions ~/.codex/archived_sessions -name "*<id>*"
```

No hit? List recent sessions with their first user message as preview:

```sh
cd ~/.codex
for f in $(ls -t sessions/*/*/*/*.jsonl archived_sessions/*.jsonl 2>/dev/null | head -20); do
  id=$(basename "$f" | sed 's/.*-\([0-9a-f-]\{36\}\)\.jsonl/\1/')
  name=$(grep -F "$id" session_index.jsonl | tail -1 | jq -r '.thread_name')
  first=$(jq -r 'select(.payload.type=="user_message") | .payload.message' "$f" | head -1 | cut -c1-70)
  printf '%s\t%s\t%s\n' "$f" "${name:-–}" "$first"
done
```

## Extract

Write the texts to a scratch file, then read that file — not the rollout:

```sh
jq -r 'select(.type=="response_item" and .payload.type=="message"
  and (.payload.role=="user" or .payload.role=="assistant"))
  | "\n### " + (.payload.role|ascii_upcase) + "\n"
  + ([.payload.content[]?.text // ""] | join("\n"))' "$F" > /tmp/codex-chat.md
wc -c /tmp/codex-chat.md
```

Check the size first. Over ~80 KB, list message roles and lengths and read only
the relevant span instead of the whole file.

`role: developer` is dropped on purpose — it is the injected system preamble. The
first few `user` blocks are usually wrappers too (`<recommended_plugins>`,
AGENTS.md under `<INSTRUCTIONS>`, an injected `<skill>` body); skip them, the real
prompt follows.

## Report

Summarize what was asked, what was decided, what actually landed, and what
silently did not. Codex narrates each step, so the last assistant message alone
often misses failures earlier in the run.
