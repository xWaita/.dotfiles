---
name: ai-planning
description: Trigger when working with PRD.md, PROGRESS.md, ralph, or AI-agent project planning/scoping.
user-invocable: false
---

# AI Planning Conventions

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

Invoke the **`ai-md`** skill — PRD.md and PROGRESS.md have no reader but an agent. What follows is only what's specific to planning docs.

## PRD.md

- A PRD's normative units are signatures, behaviors, and invariants; budget rationale at one sentence per invariant.
- Separate spec from implementation: PRD is architecture/spec only. Implementation phases go in a separate PROGRESS.md.
- Upstream PRDs must not reference downstream/sibling packages whose tech choices are still open. The upstream describes its own public surface generically; the downstream PRD references the upstream.
- Plan directories (e.g. `ralph/`) are ephemeral — never cite them from durable artifacts (skills, package CLAUDE.md, code comments). Durable knowledge a plan produced belongs in those artifacts directly; point at reference implementations in code instead.

## PROGRESS.md

- Structure as phases of features optimized for AI task-driven development, where each feature represents a working commit including any required tests.
- Include steps for setting up infra for related tasks (e.g. test helpers for tasks that implement similar API methods).
- Merge trivial tasks that don't require much context and can be verified together (e.g. boilerplate files, struct definitions with the code that uses them, tightly coupled modules, similar test cases into one parametrized task).
- **Log section:** only log facts a future agent would miss from reading PRD + code at the current commit.

## Design philosophy

- Don't add spec surface for hypothetical future cases. Recommend the simpler design serving today's actual needs. Add structure only when a real requirement forces it.
