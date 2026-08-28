---
name: ai-md
description: How to write Markdown whose reader is a model rather than a person — what to cut, and what a model needs stated explicitly. Trigger when authoring or editing any Markdown doc (SKILL.md, PRD.md, PROGRESS.md, CLAUDE.md, README, notes), and as the shared base layer under the writing-skills, md-compact, and ralph-plan skills.
user-invocable: false
---

# Writing Markdown for an AI Reader

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

The reader is a model, not a person: it reads every token instead of skimming for the gist, and it pays for every token it reads. There is no second audience — this applies to READMEs and guides too. This skill owns phrasing; `md-compact` owns document structure, and each caller sets its own terseness budget.

## Cut — habits that only serve a human reader

- Onboarding ramp: intros that restate the title, Overview/TL;DR sections previewing what the sections below already say. A TOC in a long reference is not a preview — it lets a model read one section instead of the file.
- Superseded history: "previously we planned…", done TODOs, entries annotated obsolete rather than deleted. A model reads every statement as a live claim, and nothing in the file marks which one won — so a dead plan competes with the current one. Keep the rationale for a decision; cut the narration of what it replaced.
- Definitions of standard terminology. The model has the prior; define only project-local terms, and terms this project uses against their usual meaning.
- Emphasis standing in for a reason — bold, caps, shouted MUST. A reason generalizes to the cases the rule didn't anticipate; volume doesn't. Bold as a lead-in label on a bullet is structure, not emphasis; it stays.

## Keep — what a model needs said

- One term per concept. Synonym drift reads as a distinction that isn't there: nothing tells a model that "caller" and "client" are the same thing except your consistency.
- Normative statement first, rationale after it. Leading with the why forces the reader to hold an unattached justification until the instruction arrives.
- Contracts in words — state the rule *and* its exceptions. A model does not infer an exception from layout or from what you left out; it generalizes past it or invents one.
- Resolved references. "It", "this", "the above" break when a doc is reordered or read one section at a time — name the thing.
- Examples that pin down an exact format, contract, or edge case: a worked example is few-shot conditioning and often beats the rule stated in prose. Cut examples that only build intuition for what the rule already says.
