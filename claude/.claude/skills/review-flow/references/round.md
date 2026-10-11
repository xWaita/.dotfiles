# Review flow: the round

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

You are one step of one round in a review loop; your prompt gives the parameters named below. Each round refactors the target, then tunes its efficiency, then reviews its correctness, each step committing its own work, until a review finds nothing significant.

- `target` is what the loop works on: a branch, or paths. Pass it verbatim wherever these instructions name it.
- `repoDir` is the repository. Write nothing outside it, and commit from it.
- Earlier rounds' commits are part of the target. Build on them; never revert one unless it is wrong.
- A dirty tree when you start is an interrupted step of this loop: carry it forward and commit it with your own work.
- Read HEAD with `git -C <repoDir> rev-parse --short HEAD`: before you change anything as `headBefore`, after committing as `headAfter`. Commit nothing when you changed nothing.

Intent questions are the user's to decide, and this loop runs unattended:

- A finding whose fix falls into a class in `~/.claude/skills/common/intent-questions.md` (a capability, a design choice, a migration cost, a tradeoff) is reported as an intent question and never applied, whatever its severity.
- `openQuestions` lists the questions earlier steps already raised. Never re-raise one, and never apply a fix that decides or forecloses one. Report such a fix as not applied, naming the question.

If you conclude you must not do the work, return `blocked` true with the reason in `note` and stop. Never report work you did not do: filling the other fields with plausible values makes the loop record a round that never happened.
