---
name: ralph-flow
description: Run the ralph autonomous-development loop as a dynamic workflow over a plan directory's PRD.md and PROGRESS.md — one agent implements the highest-priority unchecked task, a second reviews it with /code-review high, fixes every finding, ticks the box and commits, repeating until no unchecked box remains, then runs review-flow over every commit the plan produced. Attended: watch it in /workflows. Manual only; run it with /ralph-flow from inside the project, naming the plan directory to work one other than ralph/, optionally --tasks N.
argument-hint: "[plan dir] [--tasks N]"
disable-model-invocation: true
---

# Ralph Flow

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

Arguments: $ARGUMENTS

Invoking this skill is the user's request to commit: each task is one commit of its code and, when they are in the repo, the plan files; on completion, review-flow adds its own commits.

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
- The session can commit without a prompt per tool call (auto or bypass mode, or allow rules); otherwise the run stalls on a permission prompt.

Pin `base` to `git rev-parse HEAD` (a full sha) now, and note whether `PROGRESS.md` already has a ticked box; §4 needs both.

## 3. Run the loop

Workflow rejects a `scriptPath` outside the working directory, so read `scripts/ralph-flow.js` from this skill's directory and pass its text as `script`, with `args`:

```json
{"prdPath": "<plan dir>/PRD.md", "progressPath": "<plan dir>/PROGRESS.md", "repoDir": "<git rev-parse --show-toplevel>", "maxTasks": 100}
```

All paths absolute.

Each task is two fresh agents — implement, then review+commit — so no implementer grades its own diff. Their instructions are `references/implement.md` and `references/review.md`, both built on `references/loop.md`; edit those to change agent behavior. The script only sequences the agents and checks what they report.

## 4. On return

The run returns `{stopReason, tasks}`; every task in `tasks` is committed. Report the stop reason, then one line per task: id, title, short sha, findings fixed of found.

- `complete` — no unchecked box remains. When `tasks` is non-empty, run the final review below. Then check whether the plan or repo docs (the plan's `PROGRESS.md`, a `CLAUDE.md` beside it) call for archiving the finished plan. If they do, name that step in the report: it falls to this session after the review, not to the loop.
- `cap` — boxes remain; rerun `/ralph-flow`. No final review: the run that completes the checklist reviews every task's commit.
- `blocked: …` — relay the agent's reason. No final review.

The final review covers every commit the plan produced, across reruns. Find its `base`:

- No ticked box at §2: the `base` pinned there.
- A ticked box at §2, plan files inside `repoDir`: the parent of this plan's first ticking commit. A path like `ralph/PROGRESS.md` is reused by earlier plans, so a bare `-G '\[x\]'` over its history finds theirs. Take `<fresh>`, the newest commit in `git log --format=%H -- <progressPath>` whose `git show <c>:<progressPath>` has no `[x]` (count with `grep -c`: `grep -q` exits early, and under `pipefail` the SIGPIPE'd `git show` reads as no match); then `<sha>` is the first line of `git log --reverse --format=%H -G '\[x\]' <fresh>..HEAD -- <progressPath>`, and `base` is `git rev-parse <sha>~1`.
- A ticked box at §2, plan files outside: earlier runs' commits are untraceable, so ask the user for the base.

Then read `~/.claude/skills/review-flow/SKILL.md` and follow it with the target `<base>..HEAD`.

If the workflow errors instead, an agent failed after the runtime's retries; the error names the task. Leave the tree alone — the next run's implement agent continues it — and rerun. Never hand-finish a task in this session: every commit must pass review by an agent that did not write it.
