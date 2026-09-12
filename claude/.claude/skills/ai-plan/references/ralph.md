# Ralph Plan Files

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

Read when the plan is `ralph/PRD.md` + `ralph/PROGRESS.md` — the `/ralph` loop's shape.

## Shape

- `PRD.md` — spec only.
- `PROGRESS.md` — the task checklist in priority order, highest at the top, followed by a `## Log` section.

## Task sizing

One task is one session, one commit, and one `/code-review high`. Three forces set the size, and only the middle of that range satisfies all three.

- **Floor — the restart.** The session starts cold and re-reads PRD, PROGRESS, and the code the task touches before writing a line. It pays that whatever the task's size, so a task that adds one struct field spends its whole context arriving. Merge it into the task that uses the field.
- **Floor — the review.** The review is the only read the code gets before an unattended commit, and a diff with no caller and no test gives it nothing to judge against. A task must produce a change whose correctness is decidable from the diff.
- **Ceiling — the arc.** Implement, format, test, review, fix every finding, re-test, commit, update PROGRESS all run in that same context. A task spanning many modules fills the window before the review-and-fix half, which is where the quality comes from.

Calibrate to a working commit: one behavior plus its tests, typically one to three source files and a test file. If you cannot name the single behavior the commit adds, it is two tasks.

## Log

Append a `## Log` entry **only when the task surfaced something a future ralph session needs and can't recover from `git log --stat <commit>` or the code itself**. If there's nothing of that kind, skip the entry. Entries go in chronological order — newest at the bottom.

Format:

```
## YYYY-MM-DD — Task N
- One bullet per non-obvious carry-forward fact. No prose, no preamble.
---
```

Skip:

- "Implemented task N" / what was built — the checkbox + commit message cover it.
- File-by-file changelogs — `git log -1 --stat` is authoritative.
- Standard tooling behaviour (uv resolves workspaces, ruff reformats, pytest collects, etc.).
- Restating the PRD or the task description.

Keep:

- Library/API gotchas a future agent would re-derive the hard way (e.g. `model_validator(mode="before")` mutates the dict before `frozen=True` takes effect).
- Cross-task constraints surfaced mid-implementation (e.g. "task 7 must repoint notebooks importing `alpha_gen.utils.{stats,plot}` to `nbutils.*`").
- Decisions that diverge from the PRD or override its mapping table.
