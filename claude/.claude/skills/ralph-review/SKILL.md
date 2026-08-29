---
name: ralph-review
description: Review the design a plan proposes — holes, bugs, structural smells, and refactors that would improve it — and whether PROGRESS.md can actually be executed into the PRD.md spec. Reports findings rated by severity and edits nothing. Manual only; run it with /ralph-review, optionally naming the plan files to review together.
argument-hint: [plan files; default ralph/PRD.md + ralph/PROGRESS.md]
disable-model-invocation: true
---

# Ralph Review

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

`code-review` aimed at a design instead of a diff. The design is still free to change, so the findings worth reporting are the ones that would otherwise be discovered once the code exists and the shape is expensive to move.

## Scope

Review the plan files named below as one design — a design splits across PRD and PROGRESS, and its contradictions live in the seam. When none are named, the plan is `ralph/PRD.md` + `ralph/PROGRESS.md` in the current project.

Plan files: $ARGUMENTS

## Read the code first

A design flaw is rarely visible in the plan alone; it shows up as a mismatch with what already exists. Having read the plan in full, read what it plugs into — the types it extends, the callers it changes, the utilities sitting next to what it proposes to write. Delegate that reading to an `Explore` agent when the surface is wide.

Invoke the **`ralph-plan`** skill for the design philosophy the plan is judged against: the simplest design serving today's actual needs, structure added only when a real requirement forces it.

## Hunt — the design

The primary pass.

- **Holes** — a case the design is silent on where the silence is a real gap: error and failure paths, an unavailable dependency, empty and boundary inputs, concurrency, lifecycle and teardown, migrating data that already exists.
- **Bugs** — the specified behavior cannot produce the claimed result: an invariant the stated flow breaks, a signature or type that cannot express a required case, an ordering that races or deadlocks, state that goes stale with no path to invalidate it.
- **Smells in the proposed structure** — a module owning two responsibilities; an invariant enforced by every caller instead of by the type that owns the data; a flag parameter selecting behavior; a layer reaching past its neighbor; an abstraction with exactly one implementation; a shape where one foreseeable requirement change means editing many modules.
- **Refactors that would improve it** — including to existing code: the plan bolts onto a structure that should be changed first, or specifies new code where a repo utility already does the job. Name the utility and its path.
- **Over-engineering** — spec surface for hypothetical future cases. Recommend the simpler design and say what it gives up.
- **False premises** — the design rests on code that does not exist, or that already differs from how the plan describes it.

## Hunt — plan mechanics

Check the plan against the `ralph-plan` conventions loaded above. Report a violation only where it changes what gets built: a task an agent cannot execute without guessing, a PRD spec item no task implements, a contradiction between the two files. `/ralph-compact` owns wording, redundancy, and `## Log` hygiene — never report a compaction nit here.

## Rating

Rate every finding on two axes, then read its severity off the matrix. **Impact** is what one encounter costs; **exposure** is how much meets it. An unrecoverable consequence on a rarely-reached path and a moderate one on the hot path can land at the same severity.

**Impact** — the cost of a single encounter. The top level is split off by recoverability, which is why its row does not fall with exposure.

- *unrecoverable* — data loss or corruption, a security hole. Nothing can be repaired afterwards, so a rare path is only a delay.
- *severe* — recoverable but system-wide: an outage, a deadlock or unbounded resource growth, a severe performance regression.
- *moderate* — a wrong result, an unhandled failure, or a shape where one foreseeable change edits many modules and the alternative edits one.
- *minor* — nothing breaks; a simpler or cheaper alternative exists.

**Exposure** — how much meets it, read per finding kind. Judge it from the flow the plan specifies, not from guesses about traffic.

- defect (hole, bug, false premise) — the share of normal operation that reaches the path.
- structure (smell, refactor, over-engineering) — how much code sits on the shape, and how likely the requirement change that punishes it actually arrives.
- plan mechanics — how likely the implementing agent guesses wrong. A PRD spec item no task implements is *high*: a certainty, not a risk.

**Severity** — derived, so two reviewers rating the same finding land in the same place.

| impact ↓ / exposure → | high     | medium   | low      |
| --------------------- | -------- | -------- | -------- |
| *unrecoverable*       | Critical | Critical | Critical |
| *severe*              | Critical | High     | Medium   |
| *moderate*            | High     | Medium   | Low      |
| *minor*               | Medium   | Low      | Low      |

Severity does not decide what gets reported: a Low finding still has to be one that would otherwise surface only once the code exists.

## Verify, then report and stop

Check each candidate against the code and drop what you cannot point at. Fewer substantiated findings beat coverage, and a design objection with no concrete consequence is noise.

Report two sections, design first, each ordered by severity and ties broken by impact. Per finding: the severity and the two ratings behind it, the `file:line` in the plan, one sentence stating the flaw, and the concrete consequence — what breaks, what the implementing agent guesses wrong, or what the code looks like in six months if it ships this way. For a smell or a refactor, name the alternative rather than only the objection. Say so plainly when a section is empty.

```
## Design
CRITICAL  impact severe · exposure high
  ralph/PRD.md:42 — <flaw>. <consequence>.
MEDIUM    impact severe · exposure low
  ralph/PRD.md:8 — <flaw>. <consequence>.
```

Then edit nothing. Wait for the user to name which findings to fix.
