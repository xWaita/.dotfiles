# Review flow: refactor

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

Read `round.md` beside this file first. You are the refactor step; the review step after you checks your commit.

1. Report `headBefore`.
2. Read `~/.claude/skills/refactor/SKILL.md` and follow it with the arguments `--fix <target>`. It is a manual-only skill, so read it rather than invoking it through the Skill tool.
3. `appliedRefactors` lists the refactors earlier rounds applied. Never propose reverting or re-shaping one of them: two rounds disagreeing about a shape would undo each other forever.
4. Commit what you applied with a concise message such as `refactor: inline the config wrapper`. A round with nothing to apply is normal; commit nothing then.
5. Report `headAfter`, every rated finding with whether you applied it, and the intent questions the skill left for the user.
