# Task conventions

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

What a task in a block's checklist pins, and how large it is. Read when drafting, reviewing, compacting or implementing a checklist. `references/layout.md` gives the task format.

## Tasks

Structure the checklist as phases of features, each feature a working unit including any required tests.

- Every PRD item the block implements is implemented by some task, and every task traces back to a PRD item. Deferred items get no task; a task touching a surface a deferred item shapes must leave that item buildable without reworking the task's output. Neither the PRD nor the checklist restates what the other owns.
- Pin per task: exact file paths and the signatures or symbols within them, plus existing utilities to reuse with their paths. The implementing agent cannot ask a follow-up question, so anything left unstated is guessed silently. Exception: a decision the existing code already settles unambiguously need not be pinned.
- Name the command or test that proves each task done. It must fail while the task is unimplemented, or it proves nothing.
- Mark an ordering dependency only where one really exists.
- Include steps for setting up infra shared by related tasks (e.g. test helpers for tasks that implement similar API methods).
- Merge tasks that are each too small for their own agents, related or not; Task sizing sets the floor and the ceiling. One command must still prove the merged task (parametrize similar test cases, pair boilerplate with the code that uses it).
- A fact several tasks need is stated once in the block's `## Rules`, or in `PROGRESS.md`'s `## Rules` when several blocks need it, not per task.

## Task sizing

Every task is executed by agents starting from nothing: each reads the plan and the code the task touches before writing a line, and everything it then does has to fit in that one context. Size is therefore bounded at both ends — large enough to be worth the startup it pays for, small enough to finish inside one window.

One task is one implementing agent, one reviewing agent, one `/code-review` and one commit in each repo it changes. Three forces set the size, and only the middle of that range satisfies all three.

- **Floor — the restart.** Each agent starts cold and re-reads the PRD, the block file, and the code the task touches before writing a line. It pays that whatever the task's size, so a task that adds one struct field spends its whole context arriving. Merge it into the task that uses the field.
- **Floor — the review.** The review is the only read the code gets before an unattended commit, and a diff with no caller and no test gives it nothing to judge against. A task must produce a change whose correctness is decidable from the diff.
- **Ceiling — the arc.** The first agent implements, formats and tests; the second reviews, fixes every finding, re-tests, ticks and commits, all in one context that also has to hold the diff and the code around it. A task spanning many modules fills that window before the review-and-fix half, which is where the quality comes from.

Calibrate to a working commit: one to three source files and a test file. Several behaviors in one commit is fine; a behavior you cannot name is not. Measure a task's footprint from the code it touches, not from its own file list. A task that changes two repos is reviewed and committed once in each, so it counts double against the ceiling.

- **Split over the ceiling.** An over-ceiling task splits into parts that are each above the floor and each carry their own proof. Renumber, then repoint every task-id reference within the block file; nothing outside it cites one. Since every part stays above the floor, merge-by-budget below never undoes a split.

- **Merge by budget, not by topic.** Tasks each under the floor share one checkbox, as many as fit under the ceiling, even when unrelated: the cost being managed is the cold start and the review, and neither cares whether the halves are topically linked. Keep the merged diff reviewable as separable units, so pair work that shares a skill and a test style (pure functions with hand-built tests, serde types with parse tests, a verbatim port), and keep apart tasks that each spend their context reading a large foreign API: the ceiling, not the floor, binds there. A merged checkbox lists each constituent task as its own sub-bullet with its files, behavior and proof, so the seams stay visible and each unit is reviewed on its own terms.

Below the floor for a whole plan, skip ralph: a change smaller than one task pays two cold starts and a review for nothing, so make it inline.
