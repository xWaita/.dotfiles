# Ralph run: the step

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

You are one half of one task in a ralph block. Read `~/.claude/skills/common/flow-step.md` first.

- `blockPath` is your block: a checklist in priority order, highest at the top. Each unchecked box is implemented, reviewed and committed on its own. `prdPath` is the spec it implements. `progressPath` is the plan's index; its `## Rules` bind your block as the block's own `## Rules` do.
- Read `~/.claude/skills/ralph/references/layout.md` and `~/.claude/skills/ralph/references/tasks.md` for the plan's conventions: the block file's format, how a task is sized, and when a Log entry is warranted. Date Log entries with `date +%F`.
- `worktrees` lists the block's worktrees as `repo=path`. A task path or proof prefixed `repo:` belongs to that repo's worktree; with no prefix the block has one worktree.
- Your session started in another directory. Run every command against a worktree (`git -C <worktree> …`, or `cd` into it first), and read each worktree's `CLAUDE.md` before working in it, since it was not loaded for you.
- Write nothing outside the worktrees and `blockPath`. `prdPath`, `progressPath` and other blocks' files belong to other writers: when what was built diverges from the PRD, record it in the block's Log and the main session folds it into the PRD.
- Other blocks run at the same time in other worktrees of the same repositories. Never touch a worktree or branch that is not in `worktrees`, never switch a worktree's branch, and never push.
- Plan files that sit inside a worktree are committed with the code. Otherwise write them in place and leave them uncommitted; the main session commits them.
- `headBefore` and `headAfter` are the short `HEAD` of every worktree, in `worktrees` order, joined by spaces as `repo=sha`.
