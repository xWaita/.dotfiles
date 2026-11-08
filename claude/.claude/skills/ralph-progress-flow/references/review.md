# Ralph progress flow: review, fix, compact

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

Read `round.md` beside this file first. You are the round: you review the checklist and fix what you find, then compact it. The loop decides from your findings and `merged` whether another round runs. Compaction runs in your context because you already hold the plan and the rules it needs.

## Review and fix

1. Report `headBefore`, and the number of unticked top-level tasks as `openTasks`. When it is zero, change nothing and stop.
2. Review every unticked task as the ralph session that will implement it, reading what that session would read. Report each place a task falls short of `ai-plan`'s Tasks section, `ralph.md`'s Task sizing or `ai-md`'s Keep rules. Look for:
   - **guess** — a decision the plan leaves open that the code does not settle.
   - **false-premise** — a cited path, symbol, signature or utility that does not exist or behaves differently.
   - **proof** — a proof missing, unrunnable, or passing with the task unimplemented.
   - **trace** — the PRD link missing or contradicting its item.
   - **size** — over the ceiling. Under-floor tasks are merged in the compaction below.
   - **phrasing** — an `ai-md` Keep rule broken so that the session would misread the spec. Wording that is only loose is left to the compaction below.
3. Then look for what only the whole checklist shows:
   - **coverage** — walk the PRD item by item, deferred items included.
   - **order** — a task above one whose output it needs, or a dependency marker naming no real dependency.
   - **infra** — shared setup that several tasks need and no earlier task builds.
   - **shared-rules** — a shared rule wrong against the code, or a fact repeated across tasks that belongs among the shared rules.
4. Check the code for every finding; drop what you cannot point at. Delegate wide code reading to one `Explore` agent rather than reading every file yourself: your context must last through the fixes and the compaction.
5. Rate each finding per `~/.claude/skills/common/rating.md`, as plan mechanics. `ledger` lists every finding earlier rounds returned; mark one `fresh` false when the ledger already holds it, however reworded. The loop runs another round only for a fresh Medium-or-higher finding you fixed: each review samples a new batch, so a long checklist always has a Low tail, and Lows are fixed but never extend the run.
6. Fix every real finding in `progressPath`, whatever its severity: rewrite the task in place; two findings on one task become one rewrite. Split per `ralph.md`. A fix in an intent-question class per `round.md` gets outcome `question`; a PRD defect you cannot fix around goes to `prdIssues`.
7. Commit with a concise message such as `progress: pin the codec's error type in task 4`.

## Compact

Skip this section when you fixed nothing and `round` is above 1: the plan is unchanged since the last compaction. Round 1 always compacts, because the review checks only the sizing ceiling and the floor is checked here. Otherwise:

8. Read `~/.claude/skills/ai-compact/SKILL.md` and follow it on `progressPath`, with `prdPath` as context: in `PRD.md` repoint task-number references a merge renumbered, and change nothing else. It is a manual-only skill, so read it rather than invoking it through the Skill tool.
9. Change wording, placement and task grouping only, never what a task specifies. Merge per `ralph.md`, only tasks under the floor. Report `merged` true when you merged any tasks: a merged task is a new spec, so the loop runs one more review on it.
10. Commit the plan files you changed with a concise message such as `progress: compact — merge setup tasks 2 and 3`, or nothing when nothing was compacted. Report `headAfter`, one line per change, and the passages it flagged.

Report every finding with its outcome, the PRD issues and the intent questions.
