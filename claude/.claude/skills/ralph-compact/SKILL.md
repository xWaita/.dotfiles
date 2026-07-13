---
name: ralph-compact
description: Audit ralph/PRD.md and ralph/PROGRESS.md in this project and tighten them against the AI-planning rules
allowed-tools: [Read, Edit, Bash, Glob, Grep]
disable-model-invocation: true
---

<!-- Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured. -->

Tighten `ralph/PRD.md` and `ralph/PROGRESS.md` in the current project, in place, layering the ralph-specific rules below onto the general compaction method.

Invoke the **`md-compact`** skill for the three compaction passes (structure → redundancy → sentence clarity), and the **`ai-planning`** skill for the PRD/PROGRESS conventions to compact against — concise current-state-only PRD, merged trivial sibling tasks, and `## Log` entries kept only for facts a future session can't recover from the PRD + code at the current commit.

The ralph Progress Template below sharpens the `## Log` compaction with its exact format and skip/keep criteria:

```!
cat ~/ralph/RULES.md
```
