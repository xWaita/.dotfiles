---
name: ai-review
description: Review a plan for correctness — holes, bugs and false premises in the design it proposes — and whether its task checklist can actually be executed into its spec. The plan-side counterpart of /code-review; design goes to /refactor-review and efficiency to /perf-review. Reports findings rated by severity and edits nothing. Manual only; run it with /ai-review, optionally naming the plan files to review together.
argument-hint: [plan files; default this project's ralph/ plan, else the ~/.claude/plans/ plan file]
disable-model-invocation: true
---

# AI Review

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

`code-review` aimed at a design instead of a diff. The design is still free to change, so the findings worth reporting are the ones that would otherwise be discovered only once the code exists and the shape is expensive to move. Whether a construct should exist, and how it is shaped, belongs to `/refactor-review`. What it costs to run belongs to `/perf-review`. Report either here only when it falls out of a defect.

## Scope

Review the plan files named below as one design. A design splits across spec and task checklist, and its contradictions live in the seam between them. When none are named, the plan is `ralph/PRD.md` + `ralph/PROGRESS.md` in the current project, or the `~/.claude/plans/` plan file where there is no `ralph/` directory.

Plan files: $ARGUMENTS

## Read the code first

A design flaw is rarely visible in the plan alone; it shows up as a mismatch with what already exists. Having read the plan in full, read what it plugs into: the types it extends, the callers it changes, the utilities next to what it proposes to write. Delegate that reading to an `Explore` agent when the surface is wide.

Invoke the **`ai-plan`** skill, and whichever of `ai-plan/references/ralph.md` or `ai-plan/references/dev-flow.md` matches the plan's shape, for the conventions the plan is judged against.

## Hunt — the design

- **Holes**: a case the design is silent on where the silence is a real gap. Look at error and failure paths, an unavailable dependency, empty and boundary inputs, concurrency, lifecycle and teardown, and migrating data that already exists.
- **Bugs**: the specified behavior cannot produce the claimed result. Examples: an invariant the stated flow breaks, a signature or type that cannot express a required case, an ordering that races or deadlocks, state that goes stale with no path to invalidate it.
- **False premises**: the design rests on code that does not exist, or that already differs from how the plan describes it.

When a hole's fix would need a decision about a capability, classify it per `~/.claude/skills/common/intent-questions.md`.

## Hunt — plan mechanics

Check the plan against the `ai-plan` conventions loaded above. Report a violation only where it changes what gets built:
- a task an agent cannot execute without guessing
- a spec item no task implements
- a contradiction between spec and checklist

`/ai-compact` owns wording, redundancy, and `## Log` hygiene, so never report a compaction nit here.

## Rating

Rate every finding per `~/.claude/skills/common/rating.md` (impact × exposure → severity).

Severity does not decide what gets reported. A Low finding still has to be one that would otherwise surface only once the code exists.

## Verify, then report and stop

Check each candidate against the code and drop what you cannot point at. Fewer substantiated findings beat coverage, and a design objection with no concrete consequence is noise.

Report three sections in order: **Design** and **Plan mechanics**, each ordered by severity with ties broken by impact, then **Intent questions** per `~/.claude/skills/common/intent-questions.md`. Per rated finding, give:
- the severity and the two ratings behind it
- the `file:line` in the plan
- one sentence stating the flaw
- the concrete consequence: what breaks, or what the implementing agent guesses wrong

Say so plainly when a section is empty.

```
## Design
CRITICAL  impact severe · exposure high
  ralph/PRD.md:42 — <flaw>. <consequence>.

## Plan mechanics
HIGH      impact moderate · exposure high
  ralph/PROGRESS.md:17 — <flaw>. <consequence>.
```

Every report carries each finding in full, including a re-rating or a re-issue after clarification. Never compress one to a label or a pointer at an earlier message.

Then edit nothing. Wait for the user to name which findings to fix.
