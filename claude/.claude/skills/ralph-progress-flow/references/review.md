# Ralph progress flow: review, fix, compact

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

Read `round.md` beside this file first. You are the round: you review the checklist and fix what you find, then compact it. The loop decides from your findings and `merged` whether another round runs. Compaction runs in your context because you already hold the plan and the rules it needs.

## Review and fix

1. Report `headBefore`, and the number of unticked top-level tasks as `openTasks`. When it is zero, change nothing and stop.
2. Review every unticked task as the ralph session that will implement it, reading what that session would read. Report each place a task falls short of `ai-plan`'s Tasks section, `ralph.md`'s Task sizing or `ai-md`'s Keep rules. Look for:
   - **guess** — a decision the session would have to make that the plan leaves open. One the code already settles unambiguously is no guess; reading the code is what tells them apart.
   - **false-premise** — a path, symbol, signature or utility the task cites that does not exist, or behaves differently from how the task describes it.
   - **proof** — the proof command is missing, would pass with the task unimplemented, or cannot run.
   - **trace** — the task's link to the PRD is missing or contradicts the item it cites.
   - **size** — the task sits over the sizing ceiling. Measure its footprint from the code, not from the task's own file list. Under-floor tasks are merged in the compaction below.
   - **phrasing** — wording that makes the session misread the spec: one term for two concepts or two terms for one, a reference ("it", "as in task 3") that breaks when the task is read alone, a rule stated without its exceptions, or stale text competing with the current spec. Wording that is only loose is left to the compaction below.
3. Then look for what only the whole checklist shows:
   - **coverage** — traceability between the PRD and the tasks, in either direction, deferred items included. Walk the PRD item by item.
   - **order** — a task above one whose output it needs, or a dependency marker naming no real dependency.
   - **ownership** — a file written by more than one task beyond what the shared rules allow.
   - **infra** — shared setup that several tasks need and no earlier task builds.
   - **shared-rules** — a preamble rule that is wrong against the code, or a fact repeated across tasks that belongs in the preamble once.
4. Check the code for every finding; drop what you cannot point at. Delegate wide code reading to one `Explore` agent rather than reading every file yourself: your context must last through the fixes and the compaction.
5. Rate each finding per `~/.claude/skills/common/rating.md`, as plan mechanics. `ledger` lists every finding earlier rounds returned; mark one `fresh` false when the ledger already holds it, however reworded. The loop runs another round only for a fresh Medium-or-higher finding you fixed: each review samples a new batch, so a long checklist always has a Low tail, and Lows are fixed but never extend the run.
6. Fix every real finding in `progressPath`, whatever its severity: rewrite the task in place, with no superseded history per `ai-md`; two findings on one task become one rewrite. A split follows `ralph.md`; renumber after it and repoint every task-number reference, in `PROGRESS.md` and `PRD.md`. A fix in an intent-question class per `round.md` gets outcome `question`; a PRD defect you cannot fix around goes to `prdIssues`.
7. Commit with a concise message such as `progress: pin the codec's error type in task 4`.

## Compact

Skip this section when you fixed nothing and `round` is above 1: the plan is unchanged since the last compaction. Round 1 always compacts, because the review checks only the sizing ceiling and the floor is checked here. Otherwise:

8. Read `~/.claude/skills/ai-compact/SKILL.md` and follow it on `progressPath`, with `prdPath` as context: in `PRD.md` repoint task-number references a merge renumbered, and change nothing else. It is a manual-only skill, so read it rather than invoking it through the Skill tool.
9. Change wording, placement and task grouping only, never what a task specifies. Merge only tasks under the floor: a split that follows `ralph.md` leaves both halves above it, so a merge cannot undo one. Report `merged` true when you merged any tasks: a merged task is a new spec, so the loop runs one more review on it.
10. Commit the plan files you changed with a concise message such as `progress: compact — merge setup tasks 2 and 3`, or nothing when nothing was compacted. Report `headAfter`, one line per change, and the passages it flagged.

Report every finding with its outcome, the PRD issues and the intent questions.
