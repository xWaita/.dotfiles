---
name: dev-flow
description: Plan, delegate, review — the workflow for one large dev task. Writes or adopts a plan whose task checklist assigns files per task, hands each task to an implementer sub-agent, then commits the result and runs review-flow over it. Manual only; run it with /dev-flow, either at the start of the task or once a plan already exists.
disable-model-invocation: true
---

# Dev Flow

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

Plan → delegate → review. You were invoked deliberately, so run the whole arc from wherever it starts: with no plan yet, write one; with a plan already in hand, adopt it. Either way step 1 is what gates delegation.

Invoking this skill is the user's request to commit: the implementers' work as one commit, then review-flow's own commits. The plan file is never committed.

## 1. The plan

The plan file under `~/.claude/plans/` is the handoff contract, not a sketch: a sub-agent cannot ask a follow-up question, so anything the plan leaves unstated gets guessed silently.

- **Writing it fresh:** plan in the main session, in plan mode — it persists the file for you.
- **Adopting an existing plan:** read it against the requirements below and edit the file to close every gap before delegating. A plan written without delegation in mind usually carries the spec but no task checklist.

Invoke the **`ai-plan`** skill and read `ai-plan/references/dev-flow.md` — that reference owns this plan's shape and how its tasks are sized. The checklist it produces is what makes delegation mechanical: one task maps to one implementer, and two tasks are safe to run concurrently exactly when their file lists are disjoint and neither depends on the other.

## 2. Hand off for compaction

Optional. Everything the remaining steps read is now in the plan file, so this is the cheapest point in the arc to shed context — but only offer it when this session's planning was substantial: wide exploration, many files read, a long plan. After a handful of reads the stop costs more than it saves; go straight to step 3.

When you do offer it, stop and tell the user to run `/compact` — or `/clear` if nothing in the conversation matters beyond the plan — then re-invoke `/dev-flow` with the plan file path. Name that path in full; after a `/clear` you will not remember it. You cannot do this yourself: `/compact` is a command only the user can submit.

Skip it when you were invoked against a plan that already existed — that user already arrived with a fresh window.

## 3. Delegate

Launch one `implementer` sub-agent per task, each given the plan file path and its task id.

- Before the first launch, `git status --porcelain` must be empty; otherwise ask whether those are the user's own edits, which step 4's commit would absorb. Then pin `base` to `git rev-parse HEAD`, a full sha.
- Send every task with no unmet dependency in one message so they run in parallel; wait for that batch, then send the next.
- Group tasks into a single implementer when they are small or tightly coupled. Never split one task across two implementers.
- You own the plan file. Implementers never edit it — concurrent writes would clobber each other. Tick the checklist yourself as reports come back.
- Relay each implementer's assumptions and blockers to the user; its report is not shown to them.

## 4. Review

Once every implementer has returned, commit their combined work as one commit with a concise message such as `feat: add config module`.

Then read `~/.claude/skills/review-flow/SKILL.md` and follow it with the target `<base>..HEAD` — one loop over the whole change, so it sees the interactions between what separate agents wrote. When one of its preconditions fails, stop there: the work is committed, and the user can run `/review-flow <base>..HEAD` themselves.
