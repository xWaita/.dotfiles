# Ralph flow: review and commit

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

Read `loop.md` beside this file first. You are the review half. The implement agent just finished `taskId` — `title`. Nothing is committed yet, so the working tree is the diff under review.

1. Report `git -C <repoDir> rev-parse --short HEAD` as `headBefore`.
2. Run the `code-review` skill with the argument `high` per `~/.claude/skills/common/code-review-fork.md`, and wait for its findings before step 3.
3. Fix every finding. This loop commits unattended, so never defer one to a later session or a new task.
4. Check this task's tests against the `testing` skill (Skill tool); the review does not judge coverage.
5. Re-run the formatter and `testCommand` (when empty, the command the task names as its proof).
6. Tick `taskId` in `progressPath` if it is not ticked yet. The tick always lands before the commit, so an interrupted task is never "committed with no tick". Add a `## Log` bullet only when your own review surfaced something the Log section of the ralph conventions says to keep.
7. Reconcile `prdPath` and `progressPath` with what was actually built — renamed files, moved module boundaries, tasks dropped or added. Keep the PRD describing the current state only. Then report `checklistDone` true when no unchecked box remains.
8. Commit from `repoDir` — the code, plus the plan files when they are inside it — with a concise message such as `feat: add config module`. Then report `git -C <repoDir> rev-parse --short HEAD` as `headAfter`.
