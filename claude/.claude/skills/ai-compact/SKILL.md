---
name: ai-compact
description: Audit this project's plan documents and tighten them against the ai-plan conventions
argument-hint: [plan files; default this project's ralph/ plan, else the ~/.claude/plans/ plan file]
allowed-tools: [Read, Edit, Bash, Glob, Grep]
disable-model-invocation: true
---

<!-- Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured. -->

Tighten plan documents in place: the plan files named below, or when none are named, `ralph/PRD.md` + `ralph/PROGRESS.md` in this project, else the `~/.claude/plans/` plan file.

Plan files: $ARGUMENTS

Invoke the **`md-compact`** skill for the three compaction passes (structure → redundancy → sentence clarity), and the **`ai-plan`** skill plus whichever of `ai-plan/references/ralph.md` or `ai-plan/references/dev-flow.md` matches the plan's shape, for the conventions to compact against — a concise current-state-only spec, sibling tasks merged to the size that shape calibrates, and `## Log` entries kept only for facts a future session can't recover from the spec + code at the current commit.
