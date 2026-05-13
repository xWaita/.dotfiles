# Git

- Never put "Co-Authored-By" lines in commit messages.

# Python guidelines

## General

- Don't keep backwards compatibility for changes unless requested.
- Always import at top level.

## Documentation

- Every public function, class, and module gets at least a one-line google-style docstring. Add more only when there's something non-obvious to say (contract, gotcha, rationale, tuning range, methodology).
- No lead paragraph that restates the class/module definition. No Args/Returns that paraphrase the signature.
- Keep `Attributes:` entries that document non-obvious field semantics; drop the rest.
- Anti-example: `def diff(a, b) -> a - b` gets `"""Difference."""` — never an Args block describing `a` and `b`.
- No comments unless explaining an obscure choice. Don't remove existing comments unless stale.

## Tests

- Follow pytest convention for tests, so use flat test functions instead of test classes.
- Use pytest.parametrize when it makes sense. Label test cases with pytest.param(..., id="")
- Only test public behaviour and interfaces.
- Tests should be simple.

### What not to test

- **Dataclass/model defaults** — testing that a dataclass has expected defaults is testing the language.
- **Trivial wrappers** — if a function just delegates to another and returns its result, don't test it separately.
- **Library guarantees** — don't test that libraries raise expected exceptions (e.g. HTTP errors from `requests`).
- **Error propagation** — if there's no try/except, don't write tests proving exceptions bubble up.
- **Constructor assignments** — don't test that `self.x = x` works.
- **Glue/orchestration code** — don't mock every dependency of a 4-line function to assert call order.

### What to test

- Logic: validation, branching, calculations, transformations.
- Edge cases in business logic (boundary values, empty inputs).
- Integration of multiple components working together.

### Consolidation

- Merge near-identical tests into a single parametrized test.

# AI planning

## PRD.md files

- Keep concise. It will be interpreted by an AI agent for planning and for generating PROGRESS.md files.
- Describe the current state only; do not reference what was previously planned.

## PROGRESS.md files

- When creating todo checklists for project plans, structure in terms of phases of features that are optimised for AI task-driven development, where each feature represents a working commit including any required tests.
- Onclude steps for setting up infra for related tasks, i.e. test helpers for tasks that implement similar API methods.
- Merge trivial tasks that don't require much context and can be verified together (e.g. boilerplate files, struct definitions with the code that uses them, tightly coupled modules, similar test cases into one parametrized task).
