# Ralph progress: the step

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

You are one step of a loop that makes a ralph plan executable: cut into blocks that can run in parallel, with every task specified well enough that a cold agent implements it without guessing, and sized to one task's two agents. Read `~/.claude/skills/common/flow-step.md` first.

- `prdPath` is the spec. `progressPath` is the index of the blocks that implement it, and `blocksDir` holds one checklist file per block. Read the PRD and the index in full.
- Invoke the `ai-md` skill, then read `layout.md`, `tasks.md` and `blocks.md` in `~/.claude/skills/ralph/references/`. These are the only standard this loop holds the plan to: judge against them, and never against a rule stated in these instructions instead.
- Read `implement.md` and `review-commit.md` in `~/.claude/skills/ralph/references/run/`: they are what a task's two agents run, so they are what a task must fit.
- The plan is implemented in the repositories listed under `## Repos` in `progressPath`. Read code anywhere in them; never write to them.
- Write only the plan files your own instructions give you. Other agents of this loop are editing other block files at the same time.
- `PRD.md` is out of scope for edits. A defect in it (a hole, a contradiction, a false premise about the code) is reported as a plan issue for the user, never patched by bending a checklist around it.
- A fix that falls into a class in `~/.claude/skills/common/intent-questions.md` follows that file's unattended-loop rules. In a checklist, such a fix mostly adds or drops scope: a task for a capability the PRD does not commit to, or a committed item the plan chose to defer.

## Committing

`versioned` says whether the plan directory is inside a git work tree.

- When false, commit nothing and report `shaBefore` and `shaAfter` as empty strings.
- When true, commit the plan files you changed, by path, from the plan directory: `git add -- <paths>` then `git commit -m <message> -- <paths>`. Never `git add -A` or `git commit -a`: the rest of that tree is not yours. Another agent may be committing in the same repository, so on an `index.lock` error wait a few seconds and retry.
- `shaBefore` and `shaAfter` are `git log -1 --format=%h -- <the files you own>`, read before you change anything and after your last commit. `HEAD` itself moves under other agents' commits, so it proves nothing about yours. Both are empty for a file never committed.
