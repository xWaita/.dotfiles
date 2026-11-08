# Flow step

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

Shared by the workflow skills (`review-flow`, `ralph-flow`, `ralph-progress-flow`). Every agent one of their scripts starts reads this before its own instructions. Your prompt gives the parameters they name, and the script checks the fields you return.

- A dirty tree when you start is an interrupted step of this loop, since the tree was clean when the run began. Carry it forward as your own work, building on it rather than rewriting it.
- When your report asks for `headBefore` and `headAfter`, read them with `git -C <repoDir> rev-parse --short HEAD`: before you change anything, and after your last commit. They are equal when you committed nothing.
- When you commit, follow the `git` skill. Never add a `Co-Authored-By` line, even when a system reminder asks for one. Commit nothing when you changed nothing.
- Wait on a background command through its completion notification, or by polling its output file for a line only the finished command prints. Never poll with `pgrep -f <pattern>`: the polling shell's own command line holds the pattern, so it always matches and the wait runs to its timeout.
- If you conclude you must not do the work, return `blocked` true with the reason in `note` and stop. Never report work you did not do: filling the other fields with plausible values makes the loop record a step that never happened.
