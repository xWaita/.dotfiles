---
name: refactor-review
description: Review the design of a plan or of code for necessity, structure, reuse and simplification — constructs with no requirement behind them, smells, hand-rolled code a utility already covers, over-engineering — reading what the target plugs into, not just its text. Targets plan files or a branch, PR/MR, paths or commit range. Reports findings rated by severity and edits nothing unless given --fix. Manual only; run it with /refactor-review, optionally naming the target.
argument-hint: "[--fix] [plan files | branch | PR/MR number | paths | commit range]"
disable-model-invocation: true
---

# Refactor Review

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

Arguments: $ARGUMENTS

The design lens. Correctness belongs to `/ai-review` on plans and `/code-review` on code, and efficiency belongs to `/perf-review`. Report a defect or a perf issue here only when it falls out of a design finding.

## Target

- Plan files (`PRD.md`, `PROGRESS.md`, a `~/.claude/plans/` file): review them together as one design. On a plan target, invoke the **`ai-plan`** skill, and whichever of `ai-plan/references/ralph.md` or `ai-plan/references/dev-flow.md` matches the plan's shape, for the design philosophy the plan is judged against.
- A branch: its diff against the merge-base with the default branch.
- A PR number (`gh pr diff`) or MR number (`glab mr diff`).
- Paths: those files or directories in full.
- A commit range: that range's diff.
- No target: the current branch against the merge-base with the default branch, plus uncommitted changes. When that is empty, use `ralph/PRD.md` + `ralph/PROGRESS.md` if they exist. Otherwise ask for a target and stop.

## Read wider than the target

The best refactor is usually invisible from inside the target: a helper that already exists one module over, a caller that works around the new shape, a type whose invariant every user re-checks. Read the target in full, then what it plugs into: its callers and callees, the types it extends, sibling modules, and the repo utilities near any new code. For a plan, this is the existing code it specifies against. Also read the recorded design intent — the plan or PRD behind the code, the PR/MR description, nearby docs — so each fix can be checked against what the user chose. Delegate that reading to `Explore` agents when the surface is wide.

A finding may change code outside the target only when the target touches that code or the refactor simplifies the target. Never sweep the rest of the repo.

When a ledger of earlier rounds sits beside a plan, read it and count its findings per construct. A construct patched in several rounds goes through the necessity pass first, because repeated fixes indict the construct, not its details.

## Hunt — necessity

This is the first pass. A flaw inside a construct that should not exist is fixed by deleting the construct, so judge existence before shape.

Start from the whole: sketch the simplest design that meets the stated requirements (a repo utility, a stdlib or library feature, a far smaller shape) and diff the target against it. Deleting construct by construct never finds "this subsystem could be one function". Each surplus in the diff is a candidate.

Then list every construct the target introduces (type, field, parameter, flag, mode, option, validation rule, special case) and name its consumers: the requirement, flow or other construct that reads it. Each pattern below yields a candidate, not yet a finding:

- **No consumer**, or only a test, a log line or a report count: remove it.
- **One consumer of a general construct** (a registry, a strategy, a mode switch, an optional path): specialise it to that consumer.
- **Two mechanisms serving one purpose**: keep the one that serves it better.
- **Stored derived state**: compute it from its source, and the invalidation problem goes away with it.
- **Pass-through layer** that forwards without adding behavior: call through.
- **Justified only by another construct**: judge the root, and list the cascade its removal deletes. A removal makes more constructs vestigial, so re-run this pass over what it leaves.

Classify each candidate, and every finding below, per `~/.claude/skills/common/intent-questions.md`. Removing a mechanism is a rated finding. Removing a capability, replacing a design choice, or a fix that carries a migration cost is an intent question.

## Hunt — shape

- **Structure smells**: a module owning two responsibilities; an invariant enforced by every caller instead of by the type that owns the data; a flag parameter selecting behavior; a layer reaching past its neighbor; a shape where one foreseeable requirement change edits many modules.
- **Reuse**: hand-rolled code, or a plan specifying new code, that duplicates a repo utility, stdlib or dependency feature. Name its path. This includes existing code that should be changed first because the target bolts onto it.
- **Simplification**: dead code, needless indirection, convoluted control flow, names that misstate what a thing does.
- **Over-engineering**: surface for hypothetical future cases. Recommend the simpler design and say what it gives up; classify it as in the necessity pass.

Every refactor preserves behavior. On a plan target, that means it preserves capabilities.

## Rate and verify

Rate each finding per `~/.claude/skills/common/rating.md`. Check each against the code and drop what you cannot point at, because a structural objection with no concrete consequence is noise. A necessity finding points at the construct's definition and its consumer list, and its consequence is the spec or code its removal deletes.

## Report

Two sections: **Findings** ordered by severity, ties broken by impact, then **Intent questions** per `~/.claude/skills/common/intent-questions.md`. Per finding, give:
- the severity and the two ratings behind it
- the `file:line`
- the smell in one sentence
- the concrete alternative and its consequence: what it deletes, or what the code looks like in six months if the target ships as is

Say so plainly when a section is empty. Every report carries each finding in full; never compress one to a pointer at an earlier message.

```
## Findings
HIGH      impact moderate · exposure high
  src/sync.py:88 — <smell>. <alternative>. <consequence>.
```

Then edit nothing and wait for the user to name which findings to apply.

### With `--fix`

Instead of waiting, apply every finding rated Medium or above and every Low that is an easy win (small, local, adding no new surface). Skip other Lows and the intent questions. Run the formatter and tests when the target has them, then report as above, marking each finding applied or not. Leave the changes uncommitted, because the caller owns the commit. On a plan target, the fixes are edits to the plan files under the `ai-plan` conventions: a fix rewrites the text it replaces rather than adding beside it.
