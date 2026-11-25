#!/usr/bin/env bash
# OpenCode through umwayi, for real, on its free route. From the umwayi-os repo root: bash demo-agent-opencode.sh
# Needs opencode 2.2.3 or newer on PATH. The route is opencode/big-pickle (the signed-out free tier).
# OpenCode has a chat only, so this feeds one message and then :quit.
. "$(dirname "$0")/demo-agent-common.sh"
cat > "$ROOT/agents.yaml" <<A
agents:
  - name: oc-free
    platform: opencode
    command: opencode
    workdir: $WORK
    provider: opencode
    model: opencode/big-pickle
    timeout_minutes: 5
A
allow oc-free
clear
say "OpenCode, started through umwayi-os. The plugin gates every tool call."
run agent validate
run agent check oc-free
say "The kill switch is on. The chat must not start."
run kill on
printf '\033[1;32m$\033[0m printf %s | umwayi agent chat oc-free\n' "'Reply with the single word hello.\n:quit\n'"
printf 'Reply with the single word hello.\n:quit\n' | "$PY" -m umwayi --root "$ROOT" agent chat oc-free; printf '\033[0;90m[exit %s]\033[0m\n' "$?"; pause 3
run kill off
say "Now a real chat: one message, then :quit."
printf '\033[1;32m$\033[0m printf %s | umwayi agent chat oc-free\n' "'Reply with the single word hello.\n:quit\n'"
printf 'Reply with the single word hello.\n:quit\n' | "$PY" -m umwayi --root "$ROOT" agent chat oc-free; printf '\033[0;90m[exit %s]\033[0m\n' "$?"; pause 3
run budget status
run logbook verify
