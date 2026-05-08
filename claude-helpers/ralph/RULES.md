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
5. Update task status and progress in `PROGRESS.md`.
7. Git commit the change with a descriptive message.
8. If no incomplete tasks remain, add `ALL_TASKS_COMPLETE` on its own line at the end of `PROGRESS.md`.
9. Complete your response. When running ralph script with `--print`, Claude exits automatically and my ralph script will start a new session for the next task.

## Progress Template

When updating `PROGRESS.md`, use this template. keep it concise:

```
## [Date/Time]
- What was implemented
- Files changed
- **Learnings for future iterations:**
  - Patterns discovered
  - Gotchas encountered
  - Useful context for next session
---
```

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
