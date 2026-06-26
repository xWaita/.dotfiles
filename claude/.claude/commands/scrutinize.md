---
description: Scrutinize a target for bugs, correctness issues, refactoring opportunities, anti-patterns, and unorthodox implementation
argument-hint: code location | git branch | commit range | PR
allowed-tools: [Read, Glob, Grep, Bash, Agent]
---

Scrutinize the target below for issues. Report findings for me to accept for fixing — do not edit any code.

Target:

$ARGUMENTS

## Resolve the target

Interpret `$ARGUMENTS` and gather the exact code to scrutinize:
- File, directory, glob, or symbol/function name → scrutinize that code as it currently stands (resolve symbols with Grep).
- Git branch, commit, or commit range (e.g. `main..feature`, a SHA, `HEAD~3..`) → scrutinize the changes it introduces (`git diff` / `git show`), reading surrounding context as needed.
- A PR (`#123` or URL) → fetch with `gh pr diff` and scrutinize the changes.
- Empty → scrutinize the current uncommitted diff (`git diff HEAD`).

State the interpretation you chose in one line before reporting.

## Choose breadth (adaptive)

- Small target (a single file, symbol, or small diff) → scrutinize directly in this context.
- Large target (a directory, broad glob, or branch/range spanning many files) → fan out parallel **read-only** sub-agents, split by dimension (or by file group for very large targets), then dedupe and merge their findings. Use the Explore / general-purpose agent type; sub-agents must not edit.

## What to scrutinize

- **Bugs & correctness** — logic errors, off-by-one, unhandled edge cases, error/exception handling, resource leaks, async/concurrency pitfalls, incorrect assumptions.
- **Refactoring opportunities** — duplication, dead code, needless complexity, a hand-rolled thing an existing utility/library already does (search before claiming none exists).
- **Anti-patterns** — violations of the active CLAUDE.md guidelines, leaky abstractions, hidden mutable/global state, swallowed errors, misplaced responsibilities.
- **Unorthodox / non-idiomatic** — code that takes a strange route where a standard idiom exists; surprising or hard-to-follow constructs.

Check findings against the active CLAUDE.md and project conventions; cite the rule when one applies.

## Report

List findings ranked by severity. For each:
- `path:line` location
- severity (high / medium / low), with a confidence note when unsure
- one-line description of the issue
- the **why** — the concrete consequence or the rule it violates
- a brief suggested fix

Be concrete, not speculative — don't pad with style nits the formatter handles, and don't invent issues to fill a list. If the target is clean, say so. Do not modify code; present the findings as proposed fixes for me to accept.
