# Review flow: review and commit

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

Read `round.md` beside this file first. You are the review step, and you decide whether the loop runs another round.

1. Report `headBefore`.
2. Run the `code-review` skill with the arguments `high <target>` per `~/.claude/skills/common/code-review-fork.md`, and wait for its findings before step 3.
3. Judge each finding against the code. Fix every real one, whatever its severity; decline a false positive with a one-line reason. This loop commits unattended, so never defer a real finding.
4. Rate each finding per `~/.claude/skills/common/rating.md`.
5. `ledger` lists every finding earlier rounds' reviews returned. Mark a finding `fresh` false when the ledger already holds it, however reworded — a re-report must not keep the loop alive.
6. Run the formatter and the tests covering what you changed.
7. Commit with a concise message such as `review: guard empty batch in sync`. Report `headAfter`.
8. Report `continue` true when any fresh finding rated Medium or above was fixed, else false. Low findings are fixed but never extend the run: code-review returns a new sample every run, so a large target always has a Low tail, and only the Medium+ count actually falls round over round.
