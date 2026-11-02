# Review flow: compact

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

Read `round.md` beside this file first. You are the compact step, which runs on plan targets only: the refactor and perf steps ran before you, and the review step after you checks your commit.

1. Report `headBefore`.
2. Read `~/.claude/skills/ai-compact/SKILL.md` and follow it on the plan files in `target`. It is a manual-only skill, so read it rather than invoking it through the Skill tool.
3. Change wording and placement only, never what the plan specifies. Every round's fixes leave text beside what they replaced; consolidating that is your job, while a change to a signature, behavior, invariant or task scope belongs to the other steps.
4. When cutting a passage might lose a fact, keep it and report it as flagged instead.
5. After the first round, little is left to tighten. Commit nothing when nothing was compacted.
6. Commit with a concise message such as `compact: merge PROGRESS setup tasks`.
7. Report `headAfter`, one line per change grouped by pass, and the flagged passages.
