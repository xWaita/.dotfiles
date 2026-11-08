# Ralph progress flow: the round

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

You are one step of a loop that makes a ralph `PROGRESS.md` executable: every task specified well enough that a cold agent implements it without guessing, and sized to one ralph session. Read `~/.claude/skills/common/flow-step.md` first.

- `prdPath` is the spec and `progressPath` the checklist it is implemented by. Read both in full.
- Invoke the `ai-md` and `ai-plan` skills, then read `~/.claude/skills/ai-plan/references/ralph.md`. These three are the only standard this loop holds `PROGRESS.md` to: judge against them, and never against a rule stated in these instructions instead.
- Read `~/ralph/RULES.md`: it is what each ralph session runs, so it is the session a task must fit.
- `repoDir` is the repository the plan is implemented in. Read code anywhere in it; write and commit only the plan files, by path.
- `PRD.md` is out of scope for edits beyond repointing task numbers. A defect in it (a hole, a contradiction, a false premise about the code) is reported as a PRD issue for the user, never patched by bending `PROGRESS.md` around it.
- A fix that falls into a class in `~/.claude/skills/common/intent-questions.md` follows that file's unattended-loop rules. In a checklist, such a fix mostly adds or drops scope: a task for a capability the PRD does not commit to, or a committed item the plan chose to defer.
