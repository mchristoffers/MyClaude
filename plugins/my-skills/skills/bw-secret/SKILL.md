---
name: bw-secret
description: Use when a task needs a password, API key, token, or other secret — fetch single fields from the Users Bitwarden vault via the bw CLI. Also use when any bw command fails, to diagnose the cause and repair the machine setup.
---

# Fetching secrets from Bitwarden

## Fetch flow

1. **Session check:** `[ -s /dev/shm/bw-session ]`. If missing, the vault is locked. Ask the User  to run `! bw-open`, then continue.
2. **Fetch exactly one field per command**, prefixing every call (env vars don't persist between Bash calls):
   `BW_SESSION=$(cat /dev/shm/bw-session) bw get password <item>`
   Other fields: `bw get username|totp|notes|uri <item>`. Custom fields: `bw get item <item> | jq -r '.fields[] | select(.name=="<field>").value'`
3. **Don't print the secret** when avoidable — pipe it straight into the consuming command or env (`API_KEY=$(... bw get password x) some-command`).
4. **When done**, offer to lock again: the User runs `! bw-close`, or run `rm -f /dev/shm/bw-session && bw lock` yourself.

## Invariants

- Never `bw export`

## Error triage

| Symptom | Cause | Fix |
|---|---|---|
| `bw: command not found` | CLI not installed | [setup.md](references/setup.md) §1 |
| `You are not logged in.` | machine never logged in | setup.md §2 |
| `/dev/shm/bw-session` missing or `Vault is locked.` | vault locked | ask the User: `! bw-open` |
| the User reports `bw-open: command not found` | shell helpers missing | setup.md §3 |
| bw calls denied/blocked unexpectedly | permission rules/hook missing or wrong | setup.md §4 |
| `More than one result was found.` / `Not found.` | ambiguous or wrong item name | `... bw list items --search <name> \| jq -r '.[] \| .name'` (names only), let the User pick |

On any setup gap, open [references/setup.md](references/setup.md) and walk through it with the User from the failing section onward, verifying each step.