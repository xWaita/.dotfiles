---
name: refactor
description: Find refactoring opportunities that improve design, simplify code and clean up the codebase around a target — a branch, a PR/MR, files, or a commit range — reading the code the target plugs into, not just the diff. Reports findings rated by severity and edits nothing unless given --fix. Manual only; run it with /refactor, optionally naming the target.
argument-hint: "[--fix] [branch | PR/MR number | paths | commit range]"
disable-model-invocation: true
---

# Refactor

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

Arguments: $ARGUMENTS

A design pass over existing code. Correctness bugs are `/code-review`'s job; report one here only when it falls out of a refactor finding.

## Target

- A branch: its diff against the merge-base with the default branch.
- A PR number (`gh pr diff`) or MR number (`glab mr diff`).
- Paths: those files or directories in full.
- A commit range: that range's diff.
- No target: the current branch against the merge-base with the default branch, plus uncommitted changes. When that is empty, ask for a target and stop.

## Read wider than the target

The best refactor is usually invisible from inside the diff: a helper that already exists one module over, a caller that works around the new shape, a type whose invariant every user re-checks. Read the target in full, then what it plugs into — its callers and callees, the types it extends, sibling modules, and the repo utilities near any new code. Delegate that reading to `Explore` agents when the surface is wide.

A finding may change code outside the target only when the target touches that code or the refactor simplifies the target. Never sweep the rest of the repo.

## Hunt

- **Necessity** — a construct with no consumer, or a general construct (registry, strategy, mode switch, optional path) with only one; a pass-through layer that forwards without adding behavior; stored state derivable from its source; two mechanisms serving one purpose. Removing one often strands others — re-check what it leaves.
- **Structure** — a module owning two responsibilities; an invariant every caller enforces instead of the type that owns the data; a flag parameter selecting behavior; a layer reaching past its neighbor; a shape where one foreseeable change edits many modules.
- **Reuse** — hand-rolled code duplicating a repo utility, stdlib or dependency feature. Name its path.
- **Simplification** — dead code, needless indirection, convoluted control flow, names that misstate what a thing does.

Every refactor preserves behavior. A finding whose fix removes a capability — something the system does for its user, however rarely used — is an intent question, never a rated finding: only the user knows whether it is a requirement.

## Rate and verify

Rate each finding per `~/.claude/skills/common/rating.md`. Check each against the code and drop what you cannot point at; a structural objection with no concrete consequence is noise.

## Report

Two sections: **Findings** ordered by severity, ties broken by impact, then **Intent questions**, unrated. Per finding: severity and the two ratings behind it, `file:line`, the smell in one sentence, and the concrete alternative. Say so plainly when a section is empty.

```
## Findings
HIGH      impact moderate · exposure high
  src/sync.py:88 — <smell>. <alternative>.

## Intent questions
- src/export.py:12 — keep <capability>? Consumers: <…>. Cost: <code it carries>.
```

Then edit nothing and wait for the user to name which findings to apply.

### With `--fix`

Instead of waiting, apply every finding rated Medium or above, skip Low findings and intent questions, run the formatter and tests, then report as above, marking each finding applied or not. Leave the changes uncommitted: the caller owns the commit.
