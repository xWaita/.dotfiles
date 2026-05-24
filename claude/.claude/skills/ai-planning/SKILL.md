---
name: ai-planning
description: Trigger when working with PRD.md, PROGRESS.md, ralph, or AI-agent project planning/scoping.
user-invocable: false
---

# AI Planning Conventions

## PRD.md

- Keep concise — consumed by AI agents, not humans. Lead with normative statements (signature, behavior, invariant); strip prose rationale to one sentence per invariant max.
- Describe the current state only; do not reference what was previously planned.
- Separate spec from implementation: PRD is architecture/spec only. Implementation phases go in a separate PROGRESS.md.
- Upstream PRDs must not reference downstream/sibling packages whose tech choices are still open. The upstream describes its own public surface generically; the downstream PRD references the upstream.

## PROGRESS.md

- Structure as phases of features optimized for AI task-driven development, where each feature represents a working commit including any required tests.
- Include steps for setting up infra for related tasks (e.g. test helpers for tasks that implement similar API methods).
- Merge trivial tasks that don't require much context and can be verified together (e.g. boilerplate files, struct definitions with the code that uses them, tightly coupled modules, similar test cases into one parametrized task).
- **Log section:** only log facts a future agent would miss from reading PRD + code at the current commit. If the fact is already reflected in both sources, skip the entry. Delete invalidated entries outright — don't mark them superseded.

## Design philosophy

- Don't add spec surface for hypothetical future cases. Recommend the simpler design serving today's actual needs. Add structure only when a real requirement forces it.
