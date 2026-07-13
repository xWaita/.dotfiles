---
name: md-compact
description: Tighten a markdown document in place without losing information — reorganize structure, cut redundancy, and simplify sentences that got convoluted across many edits. Use when the user says "compact / tighten / condense / trim / clean up / de-cruft this markdown / doc / README / notes / PRD", when a .md file has grown bloated or repetitive from iterative edits, or before committing docs. For AI-planning files (PRD.md, PROGRESS.md, ralph/…) it auto-layers the ai-planning conventions.
allowed-tools: [Read, Edit, Bash, Glob, Grep]
---

<!-- Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured. -->

Tighten the target markdown in place. **Compaction ≠ summarization: remove redundancy and disorder, never information.** Every fact in the original survives — it just lands in the right place, stated once, clearly. If no target is given, ask which file or infer it from the current conversation/diff.

## Three passes, macro → micro

Run in order: reorganizing first colocates related content, which then exposes the duplication and tangling the later passes remove. Finish with one reconciling read-through.

### 1. Structure — document vs. itself

Actively hunt for reorganization opportunities; don't just tidy what's already there.
- Colocate scattered related content, giving each fact exactly one home — which also removes the pull to restate it elsewhere.
- Order sections and bullets by a logical principle: general→specific, prerequisite→dependent, priority, or chronology where it fits.
- Right-size the heading hierarchy — split an overloaded section, merge thin ones, promote/demote levels.
- Enforce parallel structure across sibling sections and list items.
- Surface implicit structure: turn a wall of bullets into grouped subsections.

### 2. Redundancy — content vs. content

- Cut what a source of truth already carries — code, `git log`, another doc. State it once in the authoritative place and reference it.
- Dedup statements repeated across sections; collapse redundant headings and nesting.
- Prose → bullets or tables for a list of facts; keep prose where narrative or rationale carries the meaning.
- Merge trivially-split sections and list items.
- Drop historical/changelog cruft — "previously…", done TODOs, superseded notes. Describe the current state only.

### 3. Sentence clarity — a sentence vs. itself

The guard against many-edits entropy: a sentence that grew tangled across edits even though it duplicates nothing.
- Read each explanation as if writing it fresh today — "would I phrase it this convolutedly from scratch?" If not, rewrite it.
- Cut stacked hedges/qualifiers, bolted-on clauses, nested parentheticals and asides, and qualifiers that no longer match the current text.
- One idea per sentence; cut dead connective tissue. Preserve meaning exactly.
- Smell tests: 3+ clauses, multiple hedges, or nested parentheticals in one sentence.

## Always

- Edit in place; do not add new content or invent claims.
- Never alter fenced code, literal blocks, or front-matter semantics.
- **Link/anchor safety:** the structure pass renames and reorders headings — preserve heading anchors and any links that reference them. Grep the repo for a heading's slug before renaming it.
- **Match terseness to audience:** AI-consumed docs (PRD.md, PROGRESS.md) → maximally terse; human READMEs and guides → keep readability and onboarding flow.

## AI-planning files

When the target is `PRD.md`, `PROGRESS.md`, or anything under `ralph/`, also invoke the `ai-planning` skill and apply its PRD/PROGRESS conventions on top of the passes above. A full ralph audit is bundled as `/ralph-compact`.

## Report

After editing, print a short summary grouped by pass — what you moved, merged, cut, and rewrote, and why — so the change is easy to eyeball. Flag anything you were unsure about rather than dropping it silently.
