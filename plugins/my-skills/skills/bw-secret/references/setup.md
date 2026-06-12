# Bitwarden CLI — machine setup (reproduces the User's reference setup)

Walk through this interactively with the User. After each section, run the verify command before moving on. Steps marked `!` are interactive — the User runs them himself by typing `! <command>` in the Claude Code prompt.

## §1 Install the CLI

Prerequisites: Node.js with a global npm prefix on PATH, plus `jq` (needed by §4's hook and for custom-field extraction).

```bash
npm install -g @bitwarden/cli
```

**Verify:** `bw --version` prints a version (reference machine: 2026.5.0) and `which jq` resolves.

## §2 Server + login

Point at the US cloud and log in (interactive — email, master password, possibly 2FA):

```bash
bw config server https://vault.bitwarden.com
```

Then the User runs: `! bw login`

**Verify:** `bw status` reports `"status":"locked"` (logged in, vault locked — the desired resting state).

## §3 Shell helpers in ~/.bash_aliases

Append this block verbatim to `~/.bash_aliases` (create the file if needed; ensure `~/.bashrc` sources it):

```bash
# Bitwarden-Tresor-Helfer
# bw-open  — Tresor entsperren, Session-Key nach /dev/shm (RAM-only, weg nach Reboot)
# bw-close — Session-Key löschen und Tresor sperren
bw-open() {
    (umask 077; bw unlock --raw > /dev/shm/bw-session) \
        && echo "Tresor offen. Key: /dev/shm/bw-session — schließen mit: bw-close" \
        || { rm -f /dev/shm/bw-session; echo "Unlock fehlgeschlagen." >&2; return 1; }
}
bw-close() {
    rm -f /dev/shm/bw-session
    bw lock
}

# bw-unlock — Tresor entsperren und Session-Key als BW_SESSION in die aktuelle Shell exportieren
# bw-lock   — Tresor sperren und BW_SESSION wieder aus der Umgebung entfernen
bw-unlock() {
    local key
    key=$(bw unlock --raw) || { echo "Unlock fehlgeschlagen." >&2; return 1; }
    export BW_SESSION="$key"
    echo "Tresor offen. BW_SESSION gesetzt — sperren mit: bw-lock"
}
bw-lock() {
    bw lock
    unset BW_SESSION
}
```

`bw-open`/`bw-close` are what Claude relies on (the session key in `/dev/shm` survives across Bash tool calls; exported env vars don't). `bw-unlock`/`bw-lock` are for the User's own shell sessions.

**Verify:** `bash -ic 'type bw-open bw-close bw-unlock bw-lock'` resolves all four.

## §4 Claude Code permission rules + bw-export kill switch

Merge into `~/.claude/settings.json` (don't overwrite other keys). Two layers: declarative `deny`/`ask` rules, and a PreToolUse hook that hard-blocks `bw export` even in `bypassPermissions` mode (the `ask` rule only bites outside bypass).

```json
{
  "permissions": {
    "deny": [
      "Bash(bw export)",
      "Bash(bw export:*)"
    ],
    "ask": [
      "Bash(bw:*)"
    ]
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.command // \"\"' | grep -qE '(^|[;&|`$( ])bw[[:space:]]+export' && echo '{\"hookSpecificOutput\":{\"hookEventName\":\"PreToolUse\",\"permissionDecision\":\"deny\",\"permissionDecisionReason\":\"bw export ist gesperrt (Tresor-Komplettexport)\"}}' || true"
          }
        ]
      }
    ]
  }
}
```

**Verify:** restart the Claude Code session, then attempt `bw export` via Bash — the hook must deny it with the "Tresor-Komplettexport" message.

## §5 Smoke test

1. the User: `! bw-open`
2. Claude: `BW_SESSION=$(cat /dev/shm/bw-session) bw get username <some-item>` returns a (harmless) field.
3. the User: `! bw-close` — then `bw status` reports locked and `/dev/shm/bw-session` is gone.
