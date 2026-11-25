# Ralph progress: draft

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

Read `step.md` beside this file first. `blockPath` is the checklist file of the block named `block`. It holds an `Implements:` line and no tasks yet; you write its tasks, and the rounds after you review and compact them. `blockPath` is the only file you own.

1. Report `shaBefore`.
2. Read the PRD sections `Implements:` names, then the code they spec against: a task pins paths, symbols and utilities that must exist, and only the code shows which do. Delegate wide reading to one `Explore` agent rather than reading every file yourself.
3. Write the block's `## Tasks`, and a `## Rules` section where several tasks share a fact, to the conventions `step.md` names. Coverage of the block's PRD items matters most: the review rounds correct guesses, wording and sizing, but a PRD item the draft leaves out is found only by a walk you are best placed to do now.
4. Stay inside the block. Work under another block's `Implements:` is that block's. When an item of yours cannot be built without code another block writes and the diagram has no edge from that block to yours, report it in `planIssues`; never add the missing work to your own checklist.
5. Commit `blockPath` per `step.md` with a message such as `progress: draft cart block`. Report `shaAfter` and the number of top-level tasks written.
