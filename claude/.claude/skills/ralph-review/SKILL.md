---
name: ralph-review
description: Review the design a plan proposes — holes, bugs, structural smells, and refactors that would improve it — and whether PROGRESS.md can actually be executed into the PRD.md spec. Reports ranked findings and edits nothing. Manual only; run it with /ralph-review, optionally naming the plan files to review together.
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

The primary pass, ranked by what costs most to discover late.

- **Holes** — a case the design is silent on where the silence is a real gap: error and failure paths, an unavailable dependency, empty and boundary inputs, concurrency, lifecycle and teardown, migrating data that already exists.
- **Bugs** — the specified behavior cannot produce the claimed result: an invariant the stated flow breaks, a signature or type that cannot express a required case, an ordering that races or deadlocks, state that goes stale with no path to invalidate it.
- **Smells in the proposed structure** — a module owning two responsibilities; an invariant enforced by every caller instead of by the type that owns the data; a flag parameter selecting behavior; a layer reaching past its neighbor; an abstraction with exactly one implementation; a shape where one foreseeable requirement change means editing many modules.
- **Refactors that would improve it** — including to existing code: the plan bolts onto a structure that should be changed first, or specifies new code where a repo utility already does the job. Name the utility and its path.
- **Over-engineering** — spec surface for hypothetical future cases. Recommend the simpler design and say what it gives up.
- **False premises** — the design rests on code that does not exist, or that already differs from how the plan describes it.

## Hunt — plan mechanics

Check the plan against the `ralph-plan` conventions loaded above. Report a violation only where it changes what gets built: a task an agent cannot execute without guessing, a PRD spec item no task implements, a contradiction between the two files. `/ralph-compact` owns wording, redundancy, and `## Log` hygiene — never report a compaction nit here.

## Verify, then report and stop

Check each candidate against the code and drop what you cannot point at. Fewer substantiated findings beat coverage, and a design objection with no concrete consequence is noise.

Report two sections, design first, each ranked most-severe first. Per finding: the `file:line` in the plan, one sentence stating the flaw, and the concrete consequence — what breaks, what the implementing agent guesses wrong, or what the code looks like in six months if it ships this way. For a smell or a refactor, name the alternative rather than only the objection. Say so plainly when a section is empty.

Then edit nothing. Wait for the user to name which findings to fix.
