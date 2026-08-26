---
name: dev-flow
description: Plan, delegate, review — the workflow for one large dev task. Writes or adopts a plan whose task checklist assigns files per task, hands each task to an implementer sub-agent, then reviews the combined diff. Manual only; run it with /dev-flow, either at the start of the task or once a plan already exists.
disable-model-invocation: true
---

# Dev Flow

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

Plan → delegate → review. You were invoked deliberately, so run the whole arc from wherever it starts: with no plan yet, write one; with a plan already in hand, adopt it. Either way step 1 is what gates delegation.

## 1. The plan

The plan file under `~/.claude/plans/` is the handoff contract, not a sketch: a sub-agent cannot ask a follow-up question, so anything the plan leaves unstated gets guessed silently.

- **Writing it fresh:** plan in the main session, in plan mode — it persists the file for you.
- **Adopting an existing plan:** read it against the requirements below and edit the file to close every gap before delegating. A plan written without delegation in mind usually carries the spec but no task checklist.

Invoke the **`ai-planning`** skill and follow it, with one deviation: PRD.md and PROGRESS.md merge into this single plan file — spec above, task checklist below.

The spec must name:

- Exact file paths, and the functions or symbols within them
- Existing utilities to reuse, with their paths
- The verification command — the specific test, build, or run that proves the change works

### Task checklist

End the plan with a checklist of discrete tasks. Each is one coherent unit — a change plus the tests that verify it. The checklist is also what makes delegation mechanical: one task maps to one implementer, and two tasks are safe to run concurrently exactly when their file lists are disjoint and neither depends on the other.

- [ ] **T1 — what changes** · `path/a.rs`, `path/b.rs`
- [ ] **T2 — what changes** · `path/c.rs` · after T1

Every file a task writes goes in its list, and a file belongs to exactly one task. Add `after T<n>` only for a real ordering dependency — an unnecessary one serializes work that could have run in parallel.

## 2. Hand off for compaction

Optional. Everything the remaining steps read is now in the plan file, so this is the cheapest point in the arc to shed context — but only offer it when this session's planning was substantial: wide exploration, many files read, a long plan. After a handful of reads the stop costs more than it saves; go straight to step 3.

When you do offer it, stop and tell the user to run `/compact` — or `/clear` if nothing in the conversation matters beyond the plan — then re-invoke `/dev-flow` with the plan file path. Name that path in full; after a `/clear` you will not remember it. You cannot do this yourself: `/compact` is a command only the user can submit.

Skip it when you were invoked against a plan that already existed — that user already arrived with a fresh window.

## 3. Delegate

Launch one `implementer` sub-agent per task, each given the plan file path and its task id.

- Send every task with no unmet dependency in one message so they run in parallel; wait for that batch, then send the next.
- Group tasks into a single implementer when they are small or tightly coupled. Never split one task across two implementers.
- You own the plan file. Implementers never edit it — concurrent writes would clobber each other. Tick the checklist yourself as reports come back.
- Relay each implementer's assumptions and blockers to the user; its report is not shown to them.

## 4. Review

Once every implementer has returned, run `code-review` over the combined diff — one review, so it sees the interactions between what separate agents wrote.

Effort matches the diff: `medium` when the change is well contained, `high` for most, `xhigh` or `max` when it spans many files or you cannot confirm it from the changed lines alone. Take the higher level when torn — below `high` the review is precision-biased and suppresses uncertain findings.

Check the tests against the `testing` skill yourself — `code-review` ranks coverage below correctness and does not review them against it.
