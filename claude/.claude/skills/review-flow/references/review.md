# Review flow: review and commit

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

Read `round.md` beside this file first. You are the review step, and you decide whether the loop runs another round.

1. Report `headBefore`.
2. Run the correctness lens that matches the target, and wait for its findings before step 3:
   - Plan files (a `PRD.md`, or a directory holding one): read `~/.claude/skills/ai-review/SKILL.md` and follow it on those files. It is a manual-only skill, so read it rather than invoking it through the Skill tool.
   - Anything else: run the `code-review` skill with the arguments `high <target>` per `~/.claude/skills/common/code-review-fork.md`.
3. On a code target, invoke the `testing` skill through the Skill tool and check the tests covering the target against it — `code-review` does not. Each mismatch is a finding like the lens's: a missing test for a high-signal risk the target introduces, a low-signal or brittle test to delete, a mock inside the system rather than at its boundary. Skip this on a plan.
4. Judge each finding against the target and the code it plugs into. Fix every real one, whatever its severity; decline a false positive with a one-line reason. This loop commits unattended, so never defer a real finding. The exception is a fix that falls into an intent-question class per `round.md`: report it as an intent question instead. On a plan, also report ai-review's own intent questions.
5. Rate each finding per `~/.claude/skills/common/rating.md`. ai-review rates its own findings; keep its ratings.
6. `ledger` lists every finding the review step returned in earlier rounds. Mark a finding `fresh` false when the ledger already holds it, however reworded — a re-report must not keep the loop alive.
7. When the target has a formatter and tests, run them over what you changed.
8. Commit with a concise message such as `review: guard empty batch in sync`. Report `headAfter`.
9. Report the intent questions.
10. Report `continue` true when any fresh finding rated Medium or above was fixed, else false. Low findings are fixed but never extend the run: the review returns a new sample every run, so a large target always has a Low tail, and only the Medium+ count actually falls round over round.
