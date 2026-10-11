# Review flow: refactor

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

Read `round.md` beside this file first. You are the refactor step; the perf and review steps after you build on and check your commit.

1. Report `headBefore`.
2. Read `~/.claude/skills/refactor-review/SKILL.md` and follow it with the arguments `--fix <target>`. It is a manual-only skill, so read it rather than invoking it through the Skill tool.
3. `appliedRefactors` lists the refactors earlier rounds applied. Never propose reverting or re-shaping one of them: two rounds disagreeing about a shape would undo each other forever.
4. A round with nothing to apply is the expected outcome, and this lens usually goes quiet long before the review step does. Never lower the bar to produce a finding: apply only real ones.
5. Commit what you applied with a concise message such as `refactor: inline the config wrapper`. When nothing was applied, commit nothing.
6. Report `headAfter`, every rated finding with whether you applied it, and the intent questions the skill left for the user.
