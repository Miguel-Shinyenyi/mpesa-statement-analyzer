W40 RECORD: PROOF ON REAL AGENTS (run on 2026-11-20 Nairobi, Part A started 2026-11-18)
Facts only. Test root /private/tmp/umwayi-demo, copy of umwayi-os 027dff2 (no .git, no home path). Python 3.13.2, macOS 27.0.1.
Main moved to 985b1b3 during the run. Only `enforce check` was run on 985b1b3 (copy /private/tmp/umwayi-demo2).

CLAUDE CODE (claude 2.1.327)
- Command: bash demo-agent-claude.sh (agent check, kill switch refusal, real run, budget status, logbook verify).
- Exit codes: check 0, run with kill switch on 3, real run 0.
- Line that matters: "Budget: run 60240b07e3634bb2 settled, measured 5 UU (42366 micros)." Agent finished in 7 s. Output "hello".
- Logbook verify: "ok: 10 entries, the format is valid and the hash matches the record" and "info: the hash chain is not started".
- Recording: B-claude.cast, B-claude.log.
- Did not work: nothing failed. A sign-in warning printed: "this sign-in ends between 2026-11-27 and 2026-11-30".
- Not verified: the cost against Anthropic's own billing; a run with a tool call.

KIRO (kiro-cli 3.3.0)
- Command: bash demo-agent-kiro.sh, twice.
- Run 1 from /tmp/umwayi-demo: agent check said "no: kiro hook file ... Add the hook file". Exit 2 for check, and for the run "Refused: agent kiro-test cannot be gated". Nothing started, no credits used. Cause: the script writes the hook with the path /tmp/umwayi-demo, umwayi expects the resolved /private/tmp/umwayi-demo (macOS link). The demo script does not resolve $REPO.
- Run 2 from the resolved path: gate passed, the run started. Exit 2. Line: "Error: Kiro could not load the available models. Please try again. (code -32000): {"errorType":"ModelRegistryUnavailableError","retryErrorType":"SERVER_ERROR"}" and "Agent kiro-test exited with code 1 (exit 2)." Budget: "settled, unknown 100 UU (1000000 micros)". Cost: unknown.
- I did not retry: this is not the known sign-in timeout, and the account is low on credits.
- Logbook verify: "ok: 12 entries, the format is valid and the hash matches the record".
- Recording: B-kiro.cast and .log (run 1), B-kiro2.cast and .log (run 2).
- Not verified: a Kiro reply, a Kiro tool call through the hook, whether the failure is the account or Kiro's service.

OPENCODE (opencode 2.3.0, free route opencode/big-pickle)
- Command: bash demo-agent-opencode.sh. Agent check passed. Kill switch refused the chat (exit 3). Real chat exit 0 after 9 s, output "hello", "[stop reason: end_turn]".
- Budget: "settled, unknown 100 UU". OpenCode has no cost reading, so unknown.
- Logbook verify: "ok: 10 entries, the format is valid and the hash matches the record".
- Recording: B-opencode.cast, B-opencode.log.
- Not verified: agent run for OpenCode (refused by design, not tried).

TINY GOAL G-0001 (builder claude-builder, tester claude-tester, guide claude-guide, all Claude Code, sonnet, medium; plan 20, task 200, goal 250 UU)
- Deviation: the tester is Claude Code, not Kiro, because Kiro's service failed. The tester is a separate agent from the builder.
- The prompt file claude/claude-code-two-short-prompts-2026-11-15.txt does not exist on this Mac. I used the goal text from RECORD-goal-run-2026-11-15.md.
- goal start: 11 s, plan with one task T-01 and five checks. Spent 6 UU.
- goal approve: first try refused: "The builder's timeout_minutes in agents.yaml is 20; the largest task needs at least 23". I raised it to 25 in the scratch root. Second try approved.
- goal run: exit 2 after about 1 minute. T-01 "failed (tests)", cause check_failed. Tester verdicts: checks 1 to 4 pass, check 5 fail. Spent 23 of 200 UU on the task, 29 of 250 on the goal. "Branch: (none), tip (none)".
- What the builder did: committed hello.py, test_hello.py and docs-parts/status-log/G-0001-T-01.md. python3 -m unittest in the worktree: 2 tests OK.
- Why check 5 failed: the plan says only hello.py and test_hello.py may be new. The part file is also new. The packet lists the part files "by right".
- Blocked builder commands (logbook): builder-no-chain gave No to 3 git commands and 1 printf; cc-no-destroy gave No to 1 printf; "No rule gave Ask me first" for 2 git commands and 1 python3 command (the command word is all the logbook keeps).
- Logbook verify: "ok: 56 entries, the format is valid and the hash matches the record". Budget day: 28 UU of 500, measured 100%.
- Recording: B-goal-run-report.log, B-goal-logbook.md. No video: the goal ran in the background, not under a recorder.
- Not verified: a passing goal end to end, goal merged, a Kiro tester.

ENFORCE CHECK (umwayi 985b1b3, against the goal root)
Output: "enforcement: enforced", then for each of claude-guide, claude-builder, claude-tester: environment, confinement, detect-after, untrusted-read refused (unavailable), network refused (network), "refused: not confined (unavailable). Allowed next: run `umwayi enforce set cooperative --agent NAME --until DATE` at your terminal, or wait for the build." Last line: "3 agent(s) checked. Nothing was started and nothing was written."
So on 985b1b3 every agent run is refused until you run enforce set cooperative. I did not run it. 027dff2 has no enforce command.

ROUND 2 ADDITIONS
- Claude Code on 985b1b3 with the fixed script: measured 5 UU in 3 s. OpenCode chat: unknown 100 UU, 10 s. Kiro: ModelRegistryAccessDeniedError again, unknown 100 UU, not retried.
- Tiny goal G-0002: T-01 in review (checked), 6 of 6 verdicts pass, 31 UU task, 37 UU goal, branch umwayi/g-0002-t-01 tip 85a32658c34f, logbook ok 83 entries. Not merged.
