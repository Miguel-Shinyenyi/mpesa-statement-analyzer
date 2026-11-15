# Test runs

Feedback and recordings from real runs of umwayi-os. This repo is private. Nothing here is published.

Each run lives in `docs/test-runs/DATE/` on a branch named `test-runs/DATE`. The guide reads that branch directly on GitHub.

What is in `2026-11-15/`:

- `FEEDBACK.md`: the Claude Code rerun after W45 (exit 0, measured 4 UU).
- `umwayi-agent-claude-rerun.*`: that run, as mp4 and cast.
- `umwayi-agent-claude-before-W45.*`: the same run before the fix (exit 2, 20 UU unknown).
- `umwayi-agent-opencode.*` and `umwayi-agent-kiro.*`: the first real OpenCode and Kiro runs.
- `umwayi-demo.mp4`: the terminal walkthrough, scenes 1 to 7.
- `07-test-run-feedback.txt`: the long feedback file and the checklist items.
- `00`, `05` and `06` text files: the video pack notes.
- `demo*.sh` and `demo.tape`: the scripts that made the recordings. Run them from the umwayi-os repo root.

Left out on purpose: the scenario test recordings (large, and they show a home path) and every GIF.

A cast file plays with `asciinema play FILE.cast`.
