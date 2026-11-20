#!/usr/bin/env bash
# Shows the scenario tests running. From the umwayi-os repo root: bash demo-tests.sh
# The whole-system file is tests/test_whole_system.py; the goal scenarios are in tests/goal/.
set -u
export PYTHONWARNINGS=ignore
[ -f umwayi/cli.py ] || { echo "run this from the umwayi-os repo root"; exit 64; }
say() { printf '\n\033[1;33m# %s\033[0m\n' "$1"; sleep "${PAUSE:-2}"; }
run() { printf '\033[1;32m$\033[0m %s\n' "$*"; sleep 1; "$@"; echo; sleep "${PAUSE:-2}"; }
clear
say "The goal commands, tested end to end with a fake agent"
run python3 -m unittest -v tests.goal.test_cli
say "The supervisor: start steps, the watch, the stop, the merge check"
run python3 -m unittest -v tests.goal.test_goalrun
say "The whole system: the owner's day through every layer"
run python3 -m unittest -v tests.test_whole_system
