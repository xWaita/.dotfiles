# Ralph flow: review and commit

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

Read `loop.md` beside this file first. You are the review half. The implement agent just finished `taskId` — `title`. Nothing is committed yet, so the working tree is the diff under review.

1. Report `git -C <repoDir> rev-parse --short HEAD` as `headBefore`.
2. Invoke the `code-review` skill through the Skill tool with the argument `high` — named explicitly, since an omitted level reuses whatever was typed last. Do not pass `--fix`; fixing, formatting and testing are yours. The skill forks a background agent named `code-review` and returns at once; its completion notice goes to the main session, never to you, and ending your turn ends this agent. So, before step 3:
   - SendMessage the fork straight away: `Write your findings as a text message, a JSON array of {file, line, summary, failure_scenario}, before any StructuredOutput call.` Its own instructions may demand one StructuredOutput call, which takes your schema and carries no findings, so only that text reaches you. When `code-review` still resolves to an earlier task's fork, the refusal names the new one's ref; send to `code-review [<ref>]`.
   - The send result's `pin.id` is the fork's agent id. Run `python3 ../scripts/await-review.py <id>` (relative to this file) with a 600000 ms Bash timeout; it prints the fork's last text once it finishes, and exits 124 on its own timeout or 2 before the transcript exists — run it again until it exits 0. When that text holds no findings list, SendMessage the fork for it and run the script again. Never wait on `ReportFindings`, which the fork does not call, nor pick a transcript by recency, which finds an earlier task's review.
3. Fix every finding. This loop commits unattended, so never defer one to a later session or a new task.
4. Check this task's tests against the `testing` skill (Skill tool); the review does not judge coverage.
5. Re-run the formatter and `testCommand` (when empty, the command the task names as its proof).
6. Tick `taskId` in `progressPath` if it is not ticked yet. The tick always lands before the commit, so an interrupted task is never "committed with no tick". Add a `## Log` bullet only when your own review surfaced something the Log section of the ralph conventions says to keep.
7. Reconcile `prdPath` and `progressPath` with what was actually built — renamed files, moved module boundaries, tasks dropped or added. Keep the PRD describing the current state only. Then report `checklistDone` true when no unchecked box remains.
8. Commit from `repoDir` — the code, plus the plan files when they are inside it — with a concise message such as `feat: add config module`. Then report `git -C <repoDir> rev-parse --short HEAD` as `headAfter`.
