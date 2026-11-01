---
name: ai-plan
description: Conventions for AI-agent plan documents — the spec/implementation split, task decomposition, and how task size is calibrated per workflow. Trigger when working with PRD.md, PROGRESS.md, a plan file under ~/.claude/plans/, ralph, dev-flow, or AI-agent project planning/scoping. Run /ai-plan to write or extend a plan for a described change.
argument-hint: [change to plan]
---

# AI Plan Conventions

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

Invoke the **`ai-md`** skill — plan documents have no reader but an agent. What follows is only what's specific to planning docs.

## Workflow shapes

Two workflows execute these plans, and their task sizing does not transfer between them. Read the matching reference before decomposing anything:

- `references/ralph.md` — the `/ralph` loop, planned as `ralph/PRD.md` + `ralph/PROGRESS.md`.
- `references/dev-flow.md` — `/dev-flow`, planned as one file under `~/.claude/plans/` that merges both halves.

## PRD.md

- A PRD's normative units are signatures, behaviors, and invariants; budget rationale at one sentence per invariant.
- Separate spec from implementation: PRD is architecture/spec only. Implementation phases go in the task checklist.
- Spec the target state, not the first slice: the PRD covers every committed feature (see Design philosophy), including those this plan does not build, so the design accommodates them instead of hardening a shape later work must tear up. Mark each deferred item `Deferred:` inline, next to the surface it shapes; spec only what today's design depends on (data shapes, public signatures, invariants, extension points), never its internals. A deferred item is a constraint on this plan's design, never work for it.
- When the design stores, moves or computes over data at scale, state the workload: volume and growth, hot paths, access pattern, retention, latency and memory targets. Pin each efficiency-relevant value the design depends on (format, codec, chunk or batch size, streaming vs loading); an unstated value ships as the library default.
- Upstream PRDs must not reference downstream/sibling packages whose tech choices are still open. The upstream describes its own public surface generically; the downstream PRD references the upstream.
- Plan directories (e.g. `ralph/`) are ephemeral — never cite them from durable artifacts (skills, package CLAUDE.md, code comments). Durable knowledge a plan produced belongs in those artifacts directly; point at reference implementations in code instead.

## Tasks

Structure the checklist as phases of features, each feature a working unit including any required tests.

- Every in-scope PRD item is implemented by some task, and every task traces back to a PRD item. Deferred items get no task; a task touching a surface a deferred item shapes must leave that item buildable without reworking the task's output. Neither half restates what the other owns.
- Pin per task: exact file paths and the signatures or symbols within them, plus existing utilities to reuse with their paths. The implementing agent cannot ask a follow-up question, so anything left unstated is guessed silently.
- Name the command or test that proves each task done.
- A file is written by exactly one task. Mark an ordering dependency only where one really exists.
- Include steps for setting up infra shared by related tasks (e.g. test helpers for tasks that implement similar API methods).
- Merge tasks that are each too small for their own session, related or not; the workflow reference sets the floor and the ceiling. One command must still prove the merged task (parametrize similar test cases, pair boilerplate with the code that uses it).

## Task sizing

Every task is executed by an agent starting from nothing: it reads the plan and the code it touches before writing a line, and everything it then does has to fit in that one context. Size is therefore bounded at both ends — large enough to be worth the startup it pays for, small enough to finish inside one window. Where those bounds sit is what the two references calibrate; do not carry a size intuition from one workflow to the other.

## Design philosophy

- Design for the committed target state; add no surface for hypothetical cases. A feature is committed when the user has stated the intent to build it (this request, an existing plan or roadmap, project docs); anything else is hypothetical. Between designs that serve the committed state equally, recommend the simpler.

## Invoked as `/ai-plan`

Write the plan for the change below, or extend it where it already exists — read the existing plan first, and read the code being specced against before writing. Establish the committed target state from the request, existing plans and project docs; when the change is the first slice of something larger whose later slices are unstated, ask for them before writing the PRD. Default to the ralph shape, `ralph/PRD.md` + `ralph/PROGRESS.md`; when the argument names an existing plan file, extend that file in its own shape instead. Loaded as background conventions instead, this section does not apply.

$ARGUMENTS
