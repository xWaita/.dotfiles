---
name: ralph-flow
description: Run the ralph autonomous-development loop as a dynamic workflow over a plan directory's PRD.md and PROGRESS.md — one agent implements the highest-priority unchecked task, a second reviews it with /code-review high, fixes every finding, ticks the box and commits, repeating until no unchecked box remains. Attended: watch it in /workflows. Manual only; run it with /ralph-flow from inside the project, naming the plan directory to work one other than ralph/, optionally --tasks N.
argument-hint: "[plan dir] [--tasks N]"
disable-model-invocation: true
---

# Ralph Flow

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

Arguments: $ARGUMENTS

Invoking this skill is the user's request to commit: each task is one commit of its code and, when they are in the repo, the plan files.

## 1. Resolve the plan

- The plan directory is the argument, else `ralph/`. `PRD.md` and `PROGRESS.md` must sit directly inside it; never search deeper or fall back to `ralph/`. With `PRD.md` but no `PROGRESS.md`, point at `/ai-plan` and stop; with neither, name what you looked for and stop.
- Any directory qualifies, including an archived or staged plan under `ralph/` or a path in another repository. Never create, move or archive a plan; a finished plan stays put and a rerun against it is a no-op.
- `repoDir` is `git rev-parse --show-toplevel` of the working directory — where the code changes and commits go, whatever the plan directory. Plan files join the commit only when they sit inside `repoDir`; otherwise they are written in place and left uncommitted.
- `--tasks N` caps committed tasks, default 100 — a backstop against a checklist that never empties, not a target.

## 2. Preconditions

Stop and tell the user when any fails:

- The working directory is inside a git repo.
- A plan directory outside the working directory is readable *and writable* — add it with `/add-dir`, or the review agent is permission-blocked on the tick.
- `git status --porcelain` is empty. Otherwise ask whether it is the user's own edits (the first commit would absorb them) or an interrupted run of this loop, which the implement agent resumes — "interrupted" means proceed.
- No other loop that commits the plan files, such as `/ralph-refine` over the same plan, runs against the repo. A clean tree does not prove that — ask.
- The session can commit without a prompt per tool call (auto or bypass mode, or allow rules); otherwise the run stalls on a permission prompt.

## 3. Run the loop

Workflow rejects a `scriptPath` outside the working directory, so read `scripts/ralph-flow.js` from this skill's directory and pass its text as `script`, with `args`:

```json
{"prdPath": "<plan dir>/PRD.md", "progressPath": "<plan dir>/PROGRESS.md", "repoDir": "<git rev-parse --show-toplevel>", "maxTasks": 100}
```

All paths absolute.

Each task is two fresh agents — implement, then review+commit — so no implementer grades its own diff. Their instructions are `references/implement.md` and `references/review.md`, both built on `references/loop.md`; edit those to change agent behavior. The script only sequences the agents and checks what they report.

## 4. On return

The run returns `{stopReason, tasks}`; every task in `tasks` is committed. Report the stop reason, then one line per task: id, title, short sha, findings fixed of found.

- `complete` — no unchecked box remains.
- `cap` — boxes remain; rerun `/ralph-flow`.
- `blocked: …` — relay the agent's reason.

If the workflow errors instead, an agent failed after the runtime's retries; the error names the task. Leave the tree alone — the next run's implement agent continues it — and rerun. Never hand-finish a task in this session: every commit must pass review by an agent that did not write it.
