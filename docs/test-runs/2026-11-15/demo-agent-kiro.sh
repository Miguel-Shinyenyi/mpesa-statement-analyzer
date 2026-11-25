#!/usr/bin/env bash
# Kiro CLI through umwayi, for real. From the umwayi-os repo root: bash demo-agent-kiro.sh
# Sign in first, yourself: kiro-cli login. umwayi never signs in for the CLI run. Needs kiro-cli on PATH.
. "$(dirname "$0")/demo-agent-common.sh"
# umwayi compares the hook command with the resolved path of the root (on macOS /var is /private/var).
ROOT_REAL="$(cd "$ROOT" && pwd -P)"
mkdir -p "$WORK/.kiro/hooks"
cat > "$WORK/.kiro/hooks/umwayi-check.json" <<H
{
  "version": "v1",
  "hooks": [
    {
      "name": "umwayi check before every tool",
      "description": "Asks umwayi-os before every tool call. Exit 2 blocks the call.",
      "trigger": "PreToolUse",
      "action": { "type": "command", "command": "python3 $REPO/adapters/kiro/hook.py --root $ROOT_REAL" },
      "timeout": 60
    }
  ]
}
H
cat > "$ROOT/agents.yaml" <<A
agents:
  - name: kiro-test
    platform: kiro
    command: kiro-cli
    workdir: $WORK
    trust_tools: [read_file]
    timeout_minutes: 5
A
allow kiro-test
clear
say "Kiro CLI, started through umwayi-os. The hook file sits in the scratch folder."
run agent validate
run agent check kiro-test
say "The kill switch is on. The agent must not start."
run kill on
run agent run kiro-test --cap-uu 100 --prompt "Reply with the single word hello."
run kill off
say "umwayi cannot watch Kiro's cost, so a cap below 100 UU is refused."
run agent run kiro-test --cap-uu 20 --prompt "Reply with the single word hello."
say "Now a real run: one prompt, capped at 100 UU, only read_file trusted."
run agent run kiro-test --cap-uu 100 --prompt "Reply with the single word hello."
run budget status
run logbook verify
