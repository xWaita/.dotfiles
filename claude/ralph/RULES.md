# Ralph Loop Development Rules **IMPORTANT**

This file is piped to Claude for autonomous development. Follow these rules.

## Project Specific File Structure

- `ralph/PRD.md` - Project architecture, module specs
- `ralph/PROGRESS.md` - Task checklist in priority order (top = highest priority) and progress

## Workflow

1. Invoke the **`ai-plan`** skill and read `ai-plan/references/ralph.md` for the plan-document conventions, then read `ralph/PRD.md` and `ralph/PROGRESS.md`.
2. Run `git status`. Uncommitted changes mean a previous session was interrupted (e.g. by a usage limit), so resume its work rather than starting fresh. This assumes the tree was clean when the loop started.
   - If `PROGRESS.md` ticks a task that has no commit in `git log`, that task is finished: do steps 9–11 for it and end the session.
   - Otherwise the changes are partial work on the highest priority incomplete task: read `git diff` and the untracked files, then continue that task from step 4, building on the changes rather than rewriting them. Step 6 reviews the whole diff, inherited changes included.
3. Select the highest priority incomplete task from `PROGRESS.md`.
4. Write the code for the task.
5. Format and test if testable code exists (`uv run pytest`).
6. Invoke the **`code-review`** skill with `high`, fix every finding, then re-run the formatter and tests. The loop commits unattended, so this is the only read the code gets — never defer a finding to a later session or file it as a new task. Name the level explicitly; an omitted level reuses whatever was typed last.
7. Check the task's tests against the **`testing`** skill — `code-review` ranks coverage below correctness and does not review them against it.
8. Tick the task box in `PROGRESS.md`. Append a `## Log` entry per the conventions loaded in step 1.
9. If the implementation diverged from `PRD.md` or `PROGRESS.md` (e.g. renamed planned files, changed module boundaries, dropped/added a planned task), update those files to reflect the new plan. Keep `PRD.md` concise — describe the current state only; do not reference what was previously planned.
10. Git commit the change with a descriptive message.
11. If no incomplete tasks remain, add `ALL_TASKS_COMPLETE` on its own line at the end of `PROGRESS.md`.
12. Complete your response. When running ralph script with `--print`, Claude exits automatically and my ralph script will start a new session for the next task.

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
