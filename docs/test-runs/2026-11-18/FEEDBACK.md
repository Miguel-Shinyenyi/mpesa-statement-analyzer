FEEDBACK: W36 RERUN, W40 REAL RUNS, OPENCODE REAL CHECK
Date and time (Nairobi): Part A started 2026-11-18 02:41. Parts B and C ran 2026-11-20 20:30 to 20:55.
umwayi-os commit: 027dff2 for Parts A, B, C. Main later moved to 985b1b3 (only enforce check ran there).
Python 3.13.2. macOS 27.0.1. claude 2.1.327, kiro-cli 3.3.0, opencode 2.3.0.
Setup I did: a venv with pip install -e of the neutral copy so `umwayi` is on PATH, and a `python` shim to python3. Nothing was installed on the system. The allow list file was not installed, and no command stopped for permission.

PART A. W36 RERUN: FAIL (details in FEEDBACK-partA.md)
STEP 1 first run of bash demo-tests.sh (recorded, asciinema)
Expected: test_cli, test_goalrun, test_whole_system all pass.
Happened: all three failed.
* tests.goal.test_cli: 49 run, 1 failure, 1 error. Line: AssertionError: Tuples differ: ('running', 'start') != ('stopped', 'owner'). 18 s.
* tests.goal.test_goalrun: 213 run, 6 errors. Line: kill: the logbook could not record turning the switch off (logbook: the date 2026-11-17 is before the date of the last entry (2026-11-18). Dates never go backwards. Nothing was written), so it stays on. 162 s.
* tests.test_whole_system: 48 run, 1 failure, 1 error, 24 skipped. Lines: FileNotFoundError: [Errno 2] No such file or directory: '/proc'; AssertionError: Lists differ: [] != [78511]. 112 s.
Notes:
* The script calls `python`, not `python3`. This Mac has no `python`, so it fails at once. I used a PATH shim for the run. Blocks (for a stranger), fix: use python3 or $PY as the agent demos do.
* The goalrun error says dates went backwards: a test uses 2026-11-17 while the logbook had 2026-11-18. The run began at 02:41 Nairobi, just after midnight. Likely a test with a fixed or UTC date. Unproven. Annoys.
* The scenario count in REC-02 (49, 213, 47) is stale: whole_system is now 48 tests. Nice to have.

STEP 3 rerun of each module once (saved in recordings/2026-11-18/)
* test_cli: 49 OK, 25 s. The StopTests case test_stop_reaches_a_running_supervisor_within_its_watch passed. The first failure did not repeat. Flaky or timing.
* test_goalrun: 213 OK, 200 s. The first errors did not repeat. Fits the date theory.
* test_whole_system: still failing. 48 run, 1 failure, 1 error, 24 skipped.
  - test_02_memory_queue_and_archive: FileNotFoundError '/proc'.
  - test_the_end_checks_see_a_leftover_process: [] != [507].
  Cause: tests/whole_system_support.py lines 381 and 385 read /proc, which exists on Linux only. On macOS the leftover-process check finds nothing and the logbook wait fails. Blocks on a Mac. The same suite passes on Linux CI.
* Left behind processes: ps showed no umwayi or python process. Only the running Claude Code session.
* Branch origin/fix/test-harness-followup (166e708): it touches tests/agents/support.py only. It does not touch whole_system_support.py, so it does not explain the /proc failure. Its fake-log fix concerns a different case. Not merged, not pushed.

Four notes per step (clear to a stranger, says next step, slow without message, change):
* demo-tests.sh: no message when it takes 2 to 3 minutes per suite. Annoys. Print a line before each suite that says how long it takes.
* A failed suite does not stop the demo or say which module to rerun. Annoys.
* Whole-system on macOS: fails with a bare FileNotFoundError. Blocks. Skip the leftover check when /proc is missing, or use ps.

What I did not verify: that the date failure comes from the midnight run; why test_cli failed the first time; the whole-system suite on Linux; the Kiro or OpenCode paths.

PART B. W40 REAL RUNS
Claude Code: PASS. Measured 5 UU in 7 s. Logbook ok. See W40-RECORD.md.
Kiro: gate refused first (demo script writes an unresolved path), then Kiro's service failed: ModelRegistryUnavailableError, cost unknown. Not retried.
OpenCode chat: PASS, 9 s, unknown 100 UU.
Tiny goal G-0001: FAIL at tests. The builder built working code (2 tests OK). The tester failed check 5 because the plan says only two new files and the supervisor adds a part file by right.
Enforce check: the command exists on 985b1b3 only. It says enforced and refuses every agent until the owner runs enforce set cooperative.
Notes per step (clear to a stranger, next step, slow without message, change):
* demo-agent-kiro.sh path bug. Blocks on macOS under /tmp. The refusal text is clear and names the fix (pwd -P), but the script itself should resolve $REPO. Fix: REPO=$(pwd -P).
* Kiro error text says "try again" for a server error. Annoys: umwayi prints exit 2 and books 100 UU as unknown for a run that never started a model call. Nice to have: say that the cost is unknown because the run failed.
* goal approve printed no question, only the result, when driven by a terminal. Annoys: I could not tell whether it asked. Nice to have: print what it is approving before it asks.
* goal approve refusal about the timeout (20 vs 23) is clear and gives the number. Good.
* Plan check 5 vs the part files. Blocks a clean first goal. Change: the guide's prompt should say that the two part files are expected, or the tester should be told they are allowed.
* goal report says "Branch: (none), tip (none)" and "Files changed: not counted" for a failed task although a commit exists in the worktree. Annoys: the owner cannot see where the builder's work is. Nice to have: print the worktree path and branch even when failed.
* goal run printed nothing for about a minute, status says "Builder: not running" 5 s after start. Nice to have.
* The logbook records only the command word for a blocked command, so I cannot say which git command was blocked. Annoys (known, by design).
* The tiny goal prompt file claude/claude-code-two-short-prompts-2026-11-15.txt does not exist here. Annoys.
* units.yaml is missing, so budget says "every reading is unknown and the limits are the placeholders" on every status. Nice to have: one line to create it.
Not verified in Part B: a Kiro reply or Kiro tool call, a goal that passes, goal merged, a Kiro tester, cost against the vendor's own bill.

PART C. OPENCODE REAL CHECK (2.3.0, free route opencode/big-pickle, no sign in, no credentials)
Steps:
1. agent check: PASS. "Gated: the checks for an OpenCode chat of agent oc-free passed."
2. chat: PASS after my driver was fixed. One message: the model read notes.txt (rule oc-read gave Yes), answered green, wrote out.txt after one permission request (rule oc-ask-write, then oc-perm-ask, answered y). "[stop reason: end_turn]", exit 0, 77 s. Logbook: one rule entry per tool call plus "the agent ran with every tool call checked by the layer 9 hook". I did not see the word canary in the logbook or the screen. Not verified.
3. planted opencode.json: PASS. "no: other config: ... opencode.json exists in the workdir or a folder above it", "Refused: agent oc-free cannot be gated, so it was not started (exit 2)".
4. OpenCode's files: the real ~/.config/opencode did not change. OpenCode wrote into the real ~/.local/share/opencode (opencode.db, log, a shell output file) and downloaded a 2.6 MB helper opencode-pty into the real ~/.cache/opencode. This matches KNOWN-LIMITS 251 (no private HOME). It is not a deviation from the docs. I did not remove anything.
5. The eight points:
 a. PASSED. opencode v2.3.0.
 b. PASSED, without the umwayi plugin. Raw opencode acp: initialize, session/new, session/prompt, one stopReason "end_turn", then the process stopped. With the plugin: only through the chat above.
 c. PASSED. Stopped with SIGTERM after the stopReason: exit 143 (that is the signal, not OpenCode's own code). Standard input closed after the stopReason: it ended by itself, exit 0, within 20 s.
 d. PASSED. Order: available_commands_update, several agent_thought_chunk, agent_message_chunk "hello", usage_update, then the prompt result with stopReason and usage. The reply is agent_message_chunk text. Thought text arrives as separate agent_thought_chunk updates. A tool's output in the reply: not tried (my prompt used no tool in the raw run).
 e. PASSED. The raw acp run had pipes on all three streams and no terminal. stderr was empty (0 bytes) and it asked nothing. opencode run with stdin from /dev/null also worked: stdout "hello", stderr only the banner "> build · big-pickle".
 f. PARTLY. The chat shows one hook entry per tool call (read, shell, write) in the logbook. The word canary was not seen. Not verified.
 g. PASSED as above (item 4).
 h. NOT CONFIRMED. opencode run --help lists --model provider/model#variant, --thinking (shows thinking blocks) and --format. No documented effort or reasoning flag. The #variant suffix may select one; not tried.
 Comparison, opencode run -m opencode/big-pickle "Reply with the single word hello." with stdin from /dev/null: exit 0, 4 s, stdout "hello", stderr 27 bytes (banner). No terminal needed.
Deviations from the docs: none found. One surprise: exit 143 on SIGTERM is not 0.
Notes per step:
* The chat reads permission answers from the same input as messages. Blocks any scripted use: a fixed list of lines breaks when the model makes an extra tool call. Change: print "answering with the next line" or accept an --answer flag. Annoys.
* The permission line "The agent asks to use a tool: out.txt [edit]" shows a path in one run and a relative name in another. Nice to have.
* The first chat took longer than 5 s with no message after the question (77 s in total). Nice to have: a waiting line.
Task 10.51 is NOT ticked. The owner ticks it.
Not verified in Part C: the plugin canary line, a tool's output inside agent_message_chunk, a documented effort flag, the OpenCode Zen free tier limits.

PUSHED BRANCHES: see the final report.

FINDING F1 (for umwayi-os, to be taken from here): the plan's check 5 contradicts the part files
- What: the guide's plan for goal G-0001 had check 5: "git status shows only hello.py and test_hello.py as new files and no other file changed". The supervisor adds docs-parts/status-log/G-0001-T-01.md to every packet "by right", and the plan itself listed it ("the last two by right"). The builder did what the packet allowed and committed the part file. The tester then failed check 5.
- Proof: goal show G-0001 (Files line with the two "by right" files and check 5); builder commit bb8b677 in the scratch worktree: hello.py, test_hello.py, docs-parts/status-log/G-0001-T-01.md; tester verdicts "1 pass, 2 pass, 3 pass, 4 pass, 5 fail"; T-01 "running to failed (reason tests)", cause check_failed; spent 23 of 200 UU. python3 -m unittest in the worktree: 2 tests OK. Files: B-goal-run-report.log, B-goal-logbook.md.
- Why it matters: a correct task fails and the owner pays the spend. A strict "only these files" check in a plan will fail on every goal, since the part files are always there.
- Proposals (the owner decides): (a) tell the guide in its prompt that the two part files are expected and must not be named in a "no other file" check; (b) tell the tester that files "by right" are allowed; (c) have the supervisor drop or rewrite a check that says "only" and names a file set.
- Second part of the same finding: the failed task's report says "Branch: (none), tip (none)" and "Files changed: not counted", but the builder's commit exists in the worktree. The owner cannot see where the work is. Proposal: print the worktree path and branch for a failed task.
- Severity: blocks (a first goal cannot pass), annoys (the report).
- Seen once, on one goal. Not verified: that it repeats on a second goal, or with a Kiro tester.

RERUN ON 985b1b3, 2026-11-20 21:00 to 21:15 (as Miguel, with Miguel's permission to run enforce set cooperative in the scratch roots; files in rerun-985b1b3/)
Setup: a second neutral copy at 985b1b3 (PR 155, enforce check). The agents were set to cooperative with "enforce set cooperative --agent NAME --until 2026-11-27" and the typed word, one agent at a time, in scratch roots only. The real umwayi-os rules and enforcement files were not touched.
Part A on 985b1b3: PASS for the two goal suites, FAIL for the third.
* tests.goal.test_cli: 49 OK, 28 s. tests.goal.test_goalrun: 213 OK, 216 s. Both passed on the first run, at 21:01, not just after midnight. This fits the date theory for the first failures on Nov 18, but it is not proven.
* tests.test_whole_system: 48 run, 1 failure, 1 error, 24 skipped, 137 s. Same two causes: FileNotFoundError '/proc' and "[] != [43052]". The macOS failure is stable.
Part B on 985b1b3 (demo scripts with one added enforce set line, named -coop; the originals refuse on 985b1b3 because the default is enforced):
* Claude Code: PASS. "Budget: run d899a0980255515a settled, measured 5 UU (42190 micros)." 8 s. Logbook "ok: 11 entries".
* Kiro: FAIL, a different error from the first time: "Error: Kiro could not load the available models because this account does not have access to them. (code -32000): {"errorType":"ModelRegistryAccessDeniedError",...}". Exit 2, unknown 100 UU. So the first error (ModelRegistryUnavailableError) and this one point to the account or its credits. Not retried again.
* OpenCode chat: PASS. hello, end_turn, 10 s, unknown 100 UU.
* Tiny goal, second goal on a fresh root: FAIL, the same way. The new plan had "Check 5: git status shows only hello.py and test_hello.py as new or changed files" and the same two "by right" part files. Verdicts 1 pass to 4 pass, 5 fail. Spent 23 of 200 UU on the task, 30 UU on the goal. "Branch: (none), tip (none)". So finding F1 repeats on a second goal and on 985b1b3. It is now seen twice.
New notes from the rerun:
* The demo scripts do not run on 985b1b3 as they are: the default is enforced and nothing in them runs enforce set. Blocks. Add the line, or a note at the top of each script.
* goal start prints the line "enforcement: enforced" although all three agents were cooperative per agent. Annoys: it looks like the set did not work. Nice to have: print the mode per agent.
* enforce set cooperative asks for a typed word and prints nothing about what it is about to change before the prompt. Nice to have. After the word it printed "One logbook entry was written." Clear.
* Not verified in the rerun: a passing goal, a Kiro run, the OpenCode points b to h again (not repeated).
