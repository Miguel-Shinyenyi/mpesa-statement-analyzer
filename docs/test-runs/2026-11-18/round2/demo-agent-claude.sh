#!/usr/bin/env bash
# Claude Code through umwayi, for real. From the umwayi-os repo root: bash demo-agent-claude.sh
# Uses your own Claude Code login (a subscription). It sends one small prompt. Needs claude on PATH.
. "$(dirname "$0")/demo-agent-common.sh"
cat > "$ROOT/agents.yaml" <<A
agents:
  - name: claude-test
    platform: claude-code
    command: claude
    workdir: $WORK
    max_turns: 3
    timeout_minutes: 5
A
allow claude-test
coop claude-test
clear
say "Claude Code, started through umwayi-os. The rules and the gate come first."
run agent validate
run agent check claude-test
say "The kill switch is on. The agent must not start."
run kill on
run agent run claude-test --cap-uu 20 --prompt "Reply with the single word hello."
run kill off
say "Now a real run: one prompt, capped at 20 UU."
run agent run claude-test --cap-uu 20 --prompt "Reply with the single word hello."
run budget status
run logbook verify
