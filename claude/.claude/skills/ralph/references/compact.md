# Plan compaction

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

Tighten plan documents in place against the plan conventions. Followed by `/ralph compact`, by `review-flow`'s compact step on a plan target, and by each `refine progress` round on its block file.

The target is the plan files the caller names: a plan directory's `PRD.md`, `PROGRESS.md` and `blocks/`, one of those files, or a single plan file.

- Invoke the **`md-compact`** skill for the three compaction passes (structure → redundancy → sentence clarity).
- Read `prd.md`, `tasks.md`, `blocks.md` and `layout.md` beside this file for the conventions to compact against. A single-file plan is compacted against `prd.md` and `tasks.md` only.

Compact toward:

- a concise spec stating the current target only;
- sibling tasks merged to the size `tasks.md` § Task sizing calibrates, with task ids repointed within the block file;
- Log entries kept only for facts a future agent can't recover from the spec and the code at the current commit;
- the table columns, frontmatter keys and section order `layout.md` gives, since the run parses them.

Never change what the plan specifies, never touch a ticked task, and never move a task between blocks: the block cut belongs to `/ralph refine progress`.
