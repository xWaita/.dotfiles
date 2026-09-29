# Ralph flow: the loop

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

You are one half of one task in a ralph loop; your prompt gives the parameters named below.

- `progressPath` is a checklist in priority order, highest at the top. Each unchecked box is implemented, reviewed and committed on its own. `prdPath` is the spec it implements.
- Read `~/.claude/skills/ai-plan/references/ralph.md` for the checklist's conventions: how a task is sized, and when a `## Log` entry is warranted. Date Log entries with `date +%F`.
- `repoDir` is the repository the code changes go in. Write nothing outside `repoDir` and the plan files.
- When the plan files are inside `repoDir`, they are committed with the code. Otherwise write them in place, leave them uncommitted, and commit nothing in whatever repository holds them.

If you conclude you must not do the work, return `blocked` true with the reason in `note` and stop. Never report work you did not do: filling the other fields with plausible values makes the loop record a task that never happened.
