---
description: Audit ralph/PRD.md and ralph/PROGRESS.md in this project and tighten them against the AI planning rules
allowed-tools: [Read, Edit, Bash, Glob, Grep]
---

Read `ralph/PRD.md` and `ralph/PROGRESS.md` in the current project. Identify content that violates the rules below — restated/historical text in PRD, Log entries that duplicate `git log --stat` or the code, prose that could be a bullet, trivial sibling tasks that should merge — and apply edits in place. Do not add new content; only compact.

If there are any opportunities to re-organize sections, paragraphs, or information to make the PRD more structured or consistent or read better, do it.

## AI planning rules (from ~/CLAUDE.md)

```!
sed -n '/^# AI planning/,$p' ~/CLAUDE.md
```

## Ralph workflow + Progress Template (from ~/ralph/RULES.md)

```!
cat ~/ralph/RULES.md
```
