# Git

- Never put "Co-Authored-By" lines in commit messages.

# Python guidelines

## General

- Don't keep backwards compatibility for changes unless requested.

## Documentation

- Write google style docstrings for all public functions, classes, and modules.
- Don't write comments unless required to explain obscure choices.

## Tests

- Follow pytest convention for tests, so use flat test functions instead of test classes.
- Use pytest.parametrize when it makes sense.
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

## PROGRESS.md files

- when creating todo checklists for project plans, structure in terms of phases of features that are optimised for AI task-driven development, where each feature represents a working commit including any required tests.
- include steps for setting up infra for related tasks, i.e. testing infra for tasks that implement similar API methods.
- merge trivial tasks that don't require much context and can be verified together (e.g. boilerplate files, struct definitions with the code that uses them, tightly coupled modules, similar test cases into one parametrized task).
