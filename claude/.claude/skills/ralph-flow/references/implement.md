# Ralph flow: implement

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

Read `loop.md` beside this file first. You are the implement half. The review agent that follows you ticks the box and commits, so do neither.

1. Run `git -C <repoDir> status --porcelain`. The tree was clean when this run started, so a dirty tree is an interrupted task: carry it forward, building on `git diff` and the untracked files rather than rewriting them. If its box is already ticked with no commit for it in `git log`, it is finished — change nothing and report it as the task.
2. Otherwise take the highest-priority unchecked box. One task only — never batch two. If none remains, change nothing and return `noneLeft` true.
3. Write the code, keeping it simple and testable rather than general; format it; run the command the task names as its proof and report that command.
4. If the task surfaced something the Log section of the ralph conventions says to keep, append it to `progressPath` as a `## Log` entry in that section's format. You are the only agent that saw it, and the diff does not show it. Most tasks warrant none; extend an existing entry for this task rather than repeat it.
