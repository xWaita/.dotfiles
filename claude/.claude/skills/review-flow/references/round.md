# Review flow: the round

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

You are one step of one round in a review loop: each round refactors the target, tunes its efficiency, compacts it when it is a plan, then reviews its correctness, until a review finds nothing significant. Read `~/.claude/skills/common/flow-step.md` first.

- `target` is what the loop works on: a branch, a commit range ending at `HEAD`, or paths. Pass it verbatim wherever these instructions name it.
- `repoDir` is the repository. Write nothing outside it, and commit from it.
- Earlier rounds' commits are part of the target. Build on them; never revert one unless it is wrong.
- A finding whose fix falls into a class in `~/.claude/skills/common/intent-questions.md` (a capability, a design choice, a migration cost, a tradeoff) follows that file's unattended-loop rules.
