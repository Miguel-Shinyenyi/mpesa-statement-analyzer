# Shared helper for demo-agent-claude.sh, demo-agent-kiro.sh and demo-agent-opencode.sh. Sourced, not run.
# Run each demo from the umwayi-os repo root. It builds a scratch root and a scratch working folder.
# FAST=1 skips pauses. U is the umwayi command.
set -u
REPO="$(pwd)"
[ -f "$REPO/umwayi/cli.py" ] || { echo "run this from the umwayi-os repo root"; exit 64; }
ROOT="$(mktemp -d)"
WORK="$(mktemp -d)"
cp "$REPO/rules.yaml" "$REPO/umwayi.json" "$ROOT/"
mkdir -p "$ROOT/memory"
export PYTHONPATH="$REPO" PYTHONWARNINGS=ignore
PY="${PY:-python3}"
pause() { [ "${FAST:-0}" = "1" ] || sleep "${1:-2}"; }
say() { printf '\n\033[1;33m# %s\033[0m\n' "$1"; pause 2; }
run() {
  printf '\033[1;32m$\033[0m umwayi'
  for a in "$@"; do case "$a" in *[\ \{\"?]*) printf " '%s'" "$a" ;; *) printf ' %s' "$a" ;; esac; done
  printf '\n'
  pause 1
  "$PY" -m umwayi --root "$ROOT" "$@"
  printf '\033[0;90m[exit %s]\033[0m\n' "$?"
  pause 3
}
# allow NAME: a Yes rule for starting the agent and for its budget check, in the scratch root only.
allow() {
  cat >> "$ROOT/rules.yaml" <<R

  - id: allow-$1
    title: Allow the scratch test agent $1
    text: The owner allows one scratch run of the test agent.
    cause: A demo in a scratch root.
    verdict: yes
    matchers:
      type: [agent_run]
      agent: [$1]

  - id: allow-budget-check
    title: Allow budget checks in the scratch root
    text: The owner allows the budget reservation of the scratch test run.
    cause: A demo in a scratch root.
    verdict: yes
    matchers:
      type: [budget_check]
R
}
