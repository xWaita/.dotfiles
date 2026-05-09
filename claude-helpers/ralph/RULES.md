# Ralph Loop Development Rules **IMPORTANT**

This file is piped to Claude for autonomous development. Follow these rules.

## Project Specific File Structure

- `ralph/PRD.md` - Project architecture, module specs
- `ralph/PROGRESS.md` - Task checklist in priority order (top = highest priority) and progress

## Workflow

1. Read `ralph/PRD.md` and `ralph/PROGRESS.md`.
2. Select the highest priority incomplete task from `PROGRESS.md`.
3. Write the code for the task.
4. Format and test if testable code exists (`uv run pytest`).
5. Tick the task box in `PROGRESS.md`. Append a `## Log` entry only if the task surfaced non-obvious context for future sessions (see Progress Template).
6. If the implementation diverged from `PRD.md` or `PROGRESS.md` (e.g. renamed planned files, changed module boundaries, dropped/added a planned task), update those files to reflect the new plan. Keep `PRD.md` concise — describe the current state only; do not reference what was previously planned.
7. Git commit the change with a descriptive message.
8. If no incomplete tasks remain, add `ALL_TASKS_COMPLETE` on its own line at the end of `PROGRESS.md`.
9. Complete your response. When running ralph script with `--print`, Claude exits automatically and my ralph script will start a new session for the next task.

## Progress Template

Append a `## Log` entry to `PROGRESS.md` **only when the task surfaced
something a future ralph session needs and can't recover from
`git log --stat <commit>` or the code itself**. If there's nothing of
that kind, skip the entry.

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

## Rules

- One task per session - do not batch multiple tasks
- Always format and run tests before committing if tests exist
- Commit messages should be concise: `feat: add config module` or `test: add detector unit tests`
- Keep code simple and testable - avoid over-engineering
- NEVER touch files outside of this project git repository (which could be a monorepo)

## Commands

```bash
uv sync              # Install dependencies
uv run pytest        # Run tests
```
