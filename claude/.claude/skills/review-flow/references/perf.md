# Review flow: perf

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

Read `round.md` beside this file first. You are the perf step: the refactor step ran before you, and the review step after you checks your commit.

1. Report `headBefore`.
2. Read `~/.claude/skills/perf-review/SKILL.md` and follow it with the arguments `--fix <target>`. It is a manual-only skill, so read it rather than invoking it through the Skill tool.
3. `appliedPerf` lists the perf changes earlier rounds applied. Never propose reverting or re-tuning one of them unless a measurement shows it regressed. Two rounds disagreeing about a value would undo each other forever.
4. A round with nothing to apply is the expected outcome, and this lens usually goes quiet long before the review step does. Never lower the bar to produce a finding: apply only real ones.
5. Commit what you applied with a concise message such as `perf: write catalog parquet with zstd`. When nothing was applied, commit nothing.
6. Report `headAfter`. Report every rated finding with its estimate or measured delta and whether you applied it. Report the intent questions the skill left for the user.
