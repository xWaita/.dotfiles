---
name: ai-review
description: Review the design a plan proposes — holes, bugs, structural smells, and refactors that would improve it — and whether its task checklist can actually be executed into its spec. Reports findings rated by severity and edits nothing. Manual only; run it with /ai-review, optionally naming the plan files to review together.
argument-hint: [plan files; default this project's ralph/ plan, else the ~/.claude/plans/ plan file]
disable-model-invocation: true
---

# AI Review

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

`code-review` aimed at a design instead of a diff. The design is still free to change, so the findings worth reporting are the ones that would otherwise be discovered once the code exists and the shape is expensive to move — or never discovered at all: surface with no requirement behind it ships, works, and is maintained forever.

## Scope

Review the plan files named below as one design — a design splits across spec and task checklist, and its contradictions live in the seam. When none are named, the plan is `ralph/PRD.md` + `ralph/PROGRESS.md` in the current project, or the `~/.claude/plans/` plan file where there is no `ralph/` directory.

Plan files: $ARGUMENTS

## Read the code first

A design flaw is rarely visible in the plan alone; it shows up as a mismatch with what already exists. Having read the plan in full, read what it plugs into — the types it extends, the callers it changes, the utilities sitting next to what it proposes to write. Delegate that reading to an `Explore` agent when the surface is wide.

Invoke the **`ai-plan`** skill, and whichever of `ai-plan/references/ralph.md` or `ai-plan/references/dev-flow.md` matches the plan's shape, for the design philosophy the plan is judged against: the simplest design serving today's actual needs, structure added only when a real requirement forces it.

When a review history exists — a ledger of earlier rounds — count its findings per construct before hunting. A construct patched in several rounds goes through the necessity pass first: repeated fixes indict the construct, not its details.

## Hunt — necessity

The first pass. A hole inside a construct that should not exist is fixed by deleting the construct, not by patching the hole, so judge existence before correctness.

Start from the whole: sketch the simplest design that meets the stated requirements — a repo utility, a stdlib or library feature, a far smaller shape — and diff the plan against it. Per-construct deletion never finds "this subsystem could be one function". Each surplus in the diff is a candidate below.

Then list every construct the spec introduces — type, field, parameter, flag, mode, option, validation rule, special case — and name its consumers: the requirement, flow or other construct that reads it. Each pattern below yields a candidate, not yet a finding:

- **No consumer**, or only a test, a log line or a report count: remove it.
- **One consumer of a general construct** — a product, a registry, a strategy, a mode switch, an optional path: specialise it to that consumer.
- **Two mechanisms serving one purpose**: keep the one that serves it better.
- **Stored derived state** — a value kept that could be computed from its source: compute it, and the invalidation problem goes with it.
- **Pass-through layer** — a wrapper, adapter or service that forwards without adding behavior: call through.
- **Justified only by another construct**: judge the root, and list the cascade its removal deletes. A removal makes more constructs vestigial; re-run this pass over what it leaves.

Then classify each candidate by what its removal loses:

- **A mechanism only** — how the spec delivers its capabilities, every one of them kept: a rated finding.
- **A capability** — something the system can do for its user, however few use it today: an intent question, never a rated finding, even when the plan declares nothing about it. Only the user knows whether it is a requirement, and a plan's silence is no evidence: compaction cuts rationale. State the capability, its consumers today, and what keeping it costs — the spec it carries, the earlier rounds that patched it — so the user can weigh it. Once the user drops it, the mechanisms that served only it are rated follow-ons.

## Hunt — the design

The defect pass.

- **Holes** — a case the design is silent on where the silence is a real gap: error and failure paths, an unavailable dependency, empty and boundary inputs, concurrency, lifecycle and teardown, migrating data that already exists.
- **Bugs** — the specified behavior cannot produce the claimed result: an invariant the stated flow breaks, a signature or type that cannot express a required case, an ordering that races or deadlocks, state that goes stale with no path to invalidate it.
- **Smells in the proposed structure** — a module owning two responsibilities; an invariant enforced by every caller instead of by the type that owns the data; a flag parameter selecting behavior; a layer reaching past its neighbor; a shape where one foreseeable requirement change means editing many modules.
- **Refactors that would improve it** — including to existing code: the plan bolts onto a structure that should be changed first, or specifies new code where a repo utility already does the job. Name the utility and its path.
- **Over-engineering** — spec surface for hypothetical future cases; recommend the simpler design and say what it gives up. Classify it as in *Hunt — necessity*. Surface the plan declares in scope as a deliberate decision (a scope line, a section stating the choice) is always an intent question: the user already weighed it.
- **False premises** — the design rests on code that does not exist, or that already differs from how the plan describes it.

## Hunt — plan mechanics

Check the plan against the `ai-plan` conventions loaded above. Report a violation only where it changes what gets built: a task an agent cannot execute without guessing, a spec item no task implements, a contradiction between spec and checklist. `/ai-compact` owns wording, redundancy, and `## Log` hygiene — never report a compaction nit here.

## Rating

Rate every finding on two axes, then read its severity off the matrix. **Impact** is what one encounter costs; **exposure** is how much meets it. An unrecoverable consequence on a rarely-reached path and a moderate one on the hot path can land at the same severity.

**Impact** — the cost of a single encounter. The top level is split off by recoverability, which is why its row does not fall with exposure.

- *unrecoverable* — data loss or corruption, a security hole. Nothing can be repaired afterwards, so a rare path is only a delay.
- *severe* — recoverable but system-wide: an outage, a deadlock or unbounded resource growth, a severe performance regression.
- *moderate* — a wrong result, an unhandled failure, a shape where one foreseeable change edits many modules and the alternative edits one, or a construct whose removal deletes substantially more spec than it adds or that earlier rounds patched repeatedly.
- *minor* — nothing breaks; a simpler or cheaper alternative exists.

**Exposure** — how much meets it, read per finding kind. Judge it from the flow the plan specifies, not from guesses about traffic.

- defect (hole, bug, false premise) — the share of normal operation that reaches the path.
- structure (smell, refactor, over-engineering) — how much code sits on the shape, and how likely the requirement change that punishes it actually arrives.
- plan mechanics — how likely the implementing agent guesses wrong. A spec item no task implements is *high*: a certainty, not a risk.

**Severity** — derived, so two reviewers rating the same finding land in the same place.

| impact ↓ / exposure → | high     | medium   | low      |
| --------------------- | -------- | -------- | -------- |
| *unrecoverable*       | Critical | Critical | Critical |
| *severe*              | Critical | High     | Medium   |
| *moderate*            | High     | Medium   | Low      |
| *minor*               | Medium   | Low      | Low      |

Severity does not decide what gets reported: a Low finding still has to be one that would otherwise surface only once the code exists, or surface the code would carry with no requirement behind it.

## Verify, then report and stop

Check each candidate against the code and drop what you cannot point at. Fewer substantiated findings beat coverage, and a design objection with no concrete consequence is noise. A necessity finding points at the construct's definition and its consumer list; its consequence is the spec its removal deletes and the defect findings living inside it.

Report three sections in order: **Design** and **Plan mechanics**, each ordered by severity with ties broken by impact, then **Intent questions**, unrated so a "fix all" reply never cuts a capability. Per rated finding: the severity and the two ratings behind it, the `file:line` in the plan, one sentence stating the flaw, and the concrete consequence — what breaks, what the implementing agent guesses wrong, or what the code looks like in six months if it ships this way. For a smell or a refactor, name the alternative rather than only the objection. Say so plainly when a section is empty.

```
## Design
CRITICAL  impact severe · exposure high
  ralph/PRD.md:42 — <flaw>. <consequence>.
MEDIUM    impact severe · exposure low
  ralph/PRD.md:8 — <flaw>. <consequence>.

## Plan mechanics
HIGH      impact moderate · exposure high
  ralph/PROGRESS.md:17 — <flaw>. <consequence>.

## Intent questions
- ralph/PRD.md:30 — keep <capability>? Consumers: <…>. Cost: <spec it carries, rounds that patched it>.
```

Every report carries each finding in full, including a re-rating or a re-issue after clarification — never compress one to a label or a pointer at an earlier message.

Then edit nothing. Wait for the user to name which findings to fix.
