FEEDBACK: Claude Code rerun after W45
Date and time: 2026-11-15 16:17 Nairobi time.
umwayi-os commit: 0c5125d (main, merge of PR 110; the W45 fix is in PR 111, merged earlier today).
Tools: 2.1.322 (Claude Code), Python 3.13.2, macOS 27.0.1.
Run: bash demo-agent-claude.sh from a neutral copy of the repo at /tmp/umwayi-demo, with your Claude Code login (plan pro). One prompt, capped at 20 UU. Recorded twice, once with VHS (mp4) and once with asciinema (cast). Each recording is a separate real run.

What each command did (same in both runs):
- umwayi agent validate: ok, exit 0.
- umwayi agent check claude-test: Gated, exit 0. Login "Claude subscription (plan: pro)". The hook self-test blocked its event.
- umwayi kill on: exit 0.
- umwayi agent run (kill switch on): Ask me first, "Agent claude-test was not started", exit 3.
- umwayi kill off: exit 0.
- umwayi agent run (real): Claude replied "hello". "Agent claude-test finished (exit 0)" after 6 to 9 s. "settled, measured 4 UU (39685 micros)". Exit 0.
- umwayi budget status: used 4 UU of 500 a day. Of used: measured 100%, declared 0%, unknown 0%. "There is no units.yaml: every reading is unknown and the limits are the placeholders."
- umwayi logbook verify, as printed: "ok: 10 entries, the format is valid and the hash matches the record" and "info: the hash chain is not started (umwayi logbook seal --chain --by NAME starts it)". Exit 0.

What changed since the morning run: the morning run (7da3e67, Claude Code 2.1.322) ended with exit 2, "its telemetry report was not valid", and settled 20 UU as unknown. Now the same prompt ends with exit 0 and a measured 4 UU. The fix is PR 111 (W45): umwayi/telemetry.py now accepts a whole-number asDouble for token counts.

What I did not verify:
- Only one Claude Code version (the one above) and one prompt.
- I did not check the 4 UU figure against Anthropic's own billing. A subscription is not billed by it.
- I did not seal the hash chain, so "chain intact" is not tested here. The logbook says the chain is not started.
- I did not test a longer run, a tool call through the hook, or the cap being hit.
- I did not rerun the scenario tests.

Files: umwayi-agent-claude-rerun.mp4 (53 s, 2.2 MB), umwayi-agent-claude-rerun.cast (4.8 KB), FEEDBACK.md.
Privacy: no home path and no username on screen in the mp4 frames I checked or in the cast text. I used a neutral path for claude and the copy of the repo.
