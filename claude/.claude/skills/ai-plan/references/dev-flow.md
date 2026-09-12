# Dev-Flow Plan File

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

Read when the plan is a single file under `~/.claude/plans/` — the `/dev-flow` shape.

## Shape

One file: spec above, task checklist below. No `## Log` section — one session runs the whole arc and still holds what a log would carry forward.

End the plan with a checklist of discrete tasks, each a change plus the tests that verify it. Every file a task writes goes in its list; `after T<n>` marks an ordering dependency.

- [ ] **T1 — what changes** · `path/a.rs`, `path/b.rs`
- [ ] **T2 — what changes** · `path/c.rs` · after T1

## Task sizing

Partition by files, not by commit. Two tasks run concurrently exactly when their file lists are disjoint and neither depends on the other, so cut along file boundaries first and then check each piece is a coherent change. Two tasks writing the same file is not a partition — it is a clobber.

- **The floor sits lower than ralph's.** No task carries its own review, and `/dev-flow` groups small or tightly coupled tasks into one implementer at delegation time. A task too thin to justify its own agent still belongs in the plan; the orchestrator merges it.
- **The ceiling sits higher than ralph's.** An implementer's context carries the change and its tests, not a review-and-fix arc.
- **Serialization is the real cost.** An `after T<n>` dependency idles a slot until its predecessor returns, while the single end-of-run review covers the combined diff either way. Between two valid partitions, prefer the one with the larger disjoint set.
