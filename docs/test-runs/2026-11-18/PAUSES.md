PAUSES: where umwayi or an agent waited and what I answered as Miguel (scratch folders only)
1. goal approve G-0001 (first try). Not a prompt: refused with "builder timeout 20, needs 23". Answer: raised the scratch builder timeout to 25. Reason: my own scratch setting was too small.
2. goal approve G-0001 (second try). Typed "yes" and "y" through a pseudo terminal. The command printed no question to show, only "Approved goal G-0001: 1 tasks queued". Reason: the task and budgets are the ones in the prompt.
3. OpenCode chat 1. "The agent asks to use a tool: out.txt [edit]. The rules say Ask me first. Allow once? [y/N]". My script sent no answer, so the line ":quit" was read as the answer: No. Result: [stop reason: cancelled], no file. My mistake, not the tool's.
4. OpenCode chat 2. Asked: "wc -c notes.txt && cat -A notes.txt [execute]". My y answered it (a read-only command on a scratch file). Then the write prompt read ":quit": No. Cancelled. Again my script. The model's tool calls differ between runs.
5. OpenCode chat 3 (new scratch root, driver answers each prompt). Asked: "/private/tmp/umwayi-run/oc/work/out.txt [edit] ... Allow once? [y/N]". Answered y. Reason: a write of a file named in the prompt, inside the scratch folder. The file out.txt holds "done".
6. Planted opencode.json in the scratch workdir. No prompt: "no: other config ... exists in the workdir" and "Refused ... cannot be gated" (exit 2). I removed the file afterwards.
7. Kiro: nothing waited for me.
8. Claude Code: no permission prompt reached me. The allow list file was not installed, but no command stopped.
