# Ralph run: review and commit

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

Read `step.md` beside this file first. You are the review half. The implement agent just finished `taskId` — `title`. Nothing is committed yet, so each worktree's working tree is the diff under review.

1. Report `headBefore`.
2. A worktree is changed when its `git status --porcelain` is non-empty. In each changed worktree run `git add -N .`, so new files show in its diff. Then, one changed worktree at a time, run the `code-review` skill at the effort `review` on that worktree's uncommitted diff, per `~/.claude/skills/common/code-review-fork.md`, and wait for its findings before step 3.
3. Fix every finding. This loop commits unattended, so never defer one to a later session or a new task.
4. Check this task's tests against the `testing` skill (Skill tool), which the review does not judge, and fix every mismatch: add missing high-signal tests, delete low-signal or brittle ones.
5. Re-run the formatter and `testCommand` (when empty, the command the task names as its proof).
6. Tick `taskId` in `blockPath` if it is not ticked yet. The tick always lands before the commit, so an interrupted task is never "committed with no tick". Add a Log bullet only when your own review surfaced something `layout.md` § Log says to keep.
7. Reconcile the block's unticked tasks with what was actually built — renamed files, moved module boundaries, a task made unnecessary or newly needed. Where what was built diverges from `prdPath`, record it in the Log. Then report `checklistDone` true when no unchecked box remains.
8. Commit last, once steps 2–7 are done: in each changed worktree, commit the code, plus the plan files when they are inside it, with a concise message such as `feat: add config module`. Then confirm `git status --porcelain` is empty in every worktree and report `headAfter`. Change nothing after the commit: an edit left behind reads as an interrupted task to the next agent.
