# Ralph progress: review, fix, compact

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

Read `step.md` beside this file first. You are one round on the block named `block`: you review its checklist in `blockPath` and fix what you find, then compact it. `blockPath` is the only file you own. The loop decides from your findings and `merged` whether another round runs. Compaction runs in your context because you already hold the plan and the rules it needs.

## Review and fix

1. Report `shaBefore`, and the number of unticked top-level tasks as `openTasks`. When it is zero, change nothing and stop.
2. Review every unticked task as the agents that will implement it, reading what they would read. Report each place a task falls short of `tasks.md` § Tasks, `tasks.md` § Task sizing or `ai-md`'s Keep rules. Look for:
   - **guess** — a decision the plan leaves open that the code does not settle.
   - **false-premise** — a cited path, symbol, signature or utility that does not exist or behaves differently.
   - **proof** — a proof missing, unrunnable, or passing with the task unimplemented.
   - **trace** — the PRD link missing or contradicting its item.
   - **size** — over the ceiling. Under-floor tasks are merged in the compaction below.
   - **phrasing** — an `ai-md` Keep rule broken so that the implementing agent would misread the spec. Wording that is only loose is left to the compaction below.
3. Then look for what only the whole checklist shows:
   - **coverage** — walk the PRD sections the block's `Implements:` line names, item by item, deferred items included.
   - **order** — a task above one whose output it needs, or a dependency marker naming no real dependency.
   - **infra** — shared setup that several tasks need and no earlier task builds.
   - **shared-rules** — a rule in the block's `## Rules` wrong against the code, or a fact repeated across tasks that belongs there.
4. Check the code for every finding; drop what you cannot point at. Delegate wide code reading to one `Explore` agent rather than reading every file yourself: your context must last through the fixes and the compaction.
5. Rate each finding per `~/.claude/skills/common/rating.md`, as plan mechanics. `ledger` lists every finding earlier rounds on this block returned; mark one `fresh` false when the ledger already holds it, however reworded. The loop runs another round only for a fresh Medium-or-higher finding you fixed: each review samples a new batch, so a long checklist always has a Low tail, and Lows are fixed but never extend the run.
6. Fix every real finding in `blockPath`, whatever its severity: rewrite the task in place; two findings on one task become one rewrite. Split per `tasks.md`. A fix in an intent-question class per `step.md` gets outcome `question`.
7. What you cannot fix inside `blockPath` goes to `planIssues`, each naming its file and line: a defect in the PRD; a rule in `progressPath` wrong against the code; a task that belongs in another block, or needs another block's output with no edge to it. The cut agent of the next pass reads them.
8. Commit per `step.md` with a concise message such as `progress: pin the codec's error type in T4`.

## Compact

Skip this section when you fixed nothing and `round` is above 1: the checklist is unchanged since the last compaction. Round 1 always compacts, because the review checks only the sizing ceiling and the floor is checked here. Otherwise:

9. Read `~/.claude/skills/ralph/references/compact.md` and follow it on `blockPath`, with `prdPath` as context.
10. Change wording, placement and task grouping only, never what a task specifies. Merge per `tasks.md`, only tasks under the floor. Report `merged` true when you merged any tasks: a merged task is a new spec, so the loop runs one more review on it.
11. Commit per `step.md` with a concise message such as `progress: compact — merge setup tasks T2 and T3`, or nothing when nothing was compacted. Report `shaAfter`, one line per change, and the passages it flagged.

Report every finding with its outcome, the plan issues and the intent questions.
