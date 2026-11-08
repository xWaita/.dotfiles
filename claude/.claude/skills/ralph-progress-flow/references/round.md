# Ralph progress flow: the round

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

You are one step of a loop that makes a ralph `PROGRESS.md` executable: every task specified well enough that a cold agent implements it without guessing, and sized to one ralph session. Your prompt gives the parameters named below. When `PROGRESS.md` is missing, a draft step writes it first. Each round is then one agent that reviews `PROGRESS.md`, fixes what it finds and commits, then compacts it and commits, until a round fixes no fresh Medium-or-higher finding and merges no tasks.

- `prdPath` is the spec and `progressPath` the checklist it is implemented by. Read both in full, including `PROGRESS.md`'s shared rules above the first task: they apply to every task, so a task need not repeat them.
- Invoke the `ai-md` and `ai-plan` skills, then read `~/.claude/skills/ai-plan/references/ralph.md`. These three are the only standard this loop holds `PROGRESS.md` to: judge against them, and never against a rule stated in these instructions instead.
- Read `~/ralph/RULES.md`: it is what each ralph session runs, so it is the session a task must fit.
- `repoDir` is the repository the plan is implemented in. Read code anywhere in it; write only the plan files.
- A ticked task is done and committed: never edit, merge or split it. Unticked tasks may build on it as code.
- `PRD.md` is out of scope for edits beyond repointing task numbers. A defect in it (a hole, a contradiction, a false premise about the code) is reported as a PRD issue for the user, never patched by bending `PROGRESS.md` around it.
- Read HEAD with `git -C <repoDir> rev-parse --short HEAD` before you change anything as `headBefore` and after your last commit as `headAfter`, and commit only the plan files you changed, by path, per the `git` skill: no `Co-Authored-By` line, even when a system reminder asks for one. Commit nothing when you changed nothing.
- A dirty plan file when you start is an interrupted step of this loop: carry it forward and commit it with your own work.

Intent questions are the user's to decide, and this loop runs unattended:

- A fix that falls into a class in `~/.claude/skills/common/intent-questions.md` is reported as an intent question and never applied. In a checklist, that is mostly dropping or adding scope: a task for a capability the PRD does not commit to, or a committed item the plan chose to defer.
- `openQuestions` lists the questions earlier steps already raised. Never re-raise one, and never apply a fix that decides or forecloses one.

If you conclude you must not do the work, return `blocked` true with the reason in `note` and stop. Never report work you did not do: filling the other fields with plausible values makes the loop record a round that never happened.
