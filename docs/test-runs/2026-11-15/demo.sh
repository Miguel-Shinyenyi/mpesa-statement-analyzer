#!/usr/bin/env bash
# umwayi-os terminal demo. Run from the umwayi-os repo root: bash demo.sh
# It builds a scratch root, so it never touches your real files. Every command is real.
# Set FAST=1 to skip the pauses (for a test run).
set -u
REPO="$(pwd)"
[ -f "$REPO/umwayi/cli.py" ] || { echo "run this from the umwayi-os repo root"; exit 64; }
ROOT="$(mktemp -d)"
cp "$REPO/rules.yaml" "$REPO/umwayi.json" "$ROOT/"
mkdir -p "$ROOT/memory"
export PYTHONPATH="$REPO"
pause() { [ "${FAST:-0}" = "1" ] || sleep "${1:-2}"; }
say() { printf '\n\033[1;33m# %s\033[0m\n' "$1"; pause 2; }
run() {
  printf '\033[1;32m$\033[0m umwayi'
  for a in "$@"; do case "$a" in *[\ \{\"?]*) printf " '%s'" "$a" ;; *) printf ' %s' "$a" ;; esac; done
  printf '\n'
  pause 1
  python -m umwayi --root "$ROOT" "$@"
  printf '\033[0;90m[exit %s]\033[0m\n' "$?"
  pause 3
}
clear
say "umwayi-os: your rules come before every AI helper acts"
run --version

say "1. The rules gate. Every action gets one of three answers."
run check '{"type":"read_memory"}'
run check '{"type":"git_push","branch":"main"}'
run check '{"type":"deploy","target":"prod"}'

say "2. Ask me first becomes a question in your queue, never a guess."
run queue add --kind decision --recommendation "No, deploy from a branch" "Deploy to prod?"
run queue list

say "3. Every change is written to a logbook you can verify."
run logbook verify
run logbook seal --chain --by miguel
run logbook verify

say "4. One switch stops every helper, job and workflow."
run kill on
run kill status
run kill off

say "5. A budget in UU, one US cent of list price. Spend is reserved before it starts."
run budget status

say "6. Goals: the guide plans, you approve, a builder works in its own worktree."
run goal --help

say "7. The same rules in front of every tool: Claude Code, Kiro, OpenCode."
run agent --help

say "Scratch root: $ROOT (delete it when you are done)"
