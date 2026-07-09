---
name: testing
description: Trigger when writing or reviewing tests, deciding what to test, test coverage/strategy, or language-specific test conventions (pytest, fixtures, parametrize, test_*.py).
user-invocable: false
---

# Testing

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

Optimize for signal density: every test should increase confidence more than maintenance cost.

## Pre-flight: before writing any test

Ask yourself:

1. What bug does this catch?
2. How likely is that bug?
3. How costly would that bug be?
4. Would another test already catch it?

If the answers are weak, skip the test.

## What to test (high-signal)

Focus heavily on:

- State machines
- Persistence / recovery
- Retries / reconnects
- Async / concurrency
- Duplicate / out-of-order events
- Idempotency
- Partial failures
- Stale data handling
- End-to-end position convergence

## What NOT to test (low-signal)

Minimize or skip tests for:

- DTOs
- Trivial wrappers
- Getters / setters
- Logging
- Obvious transformations
- Implementation structure

## How to test

- Test behavior, not implementation details.
- Prefer invariant / property tests over many example tests.
- Test edge cases aggressively; middle-case tests are often redundant.
- Mock only system boundaries and external dependencies.
- Prefer compositional / integration tests over many tiny unit tests.
- Test risk, not code volume.
- Avoid asserting incidental details (exact logs, call counts, wording, ordering unless required).
- Do not test third-party libraries or the standard library.
- Delete brittle or redundant tests aggressively.

## Preferred test shape

For each subsystem, write:

- One happy path
- One catastrophic path
- One weird edge case

Favor fewer high-signal tests over exhaustive low-signal coverage.

## Language-specific conventions

After applying the philosophy above, read the reference file matching the language under test:

- Python — `references/python.md`
