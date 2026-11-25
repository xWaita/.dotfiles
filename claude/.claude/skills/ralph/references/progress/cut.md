# Ralph progress: cut

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

Read `step.md` beside this file first. You own the block structure: `progressPath`, and which block each task sits in. No other agent of this loop runs while you do, so you may edit any block file under `blocksDir`. The files you own, for `shaBefore` and `shaAfter`, are `progressPath` and `blocksDir`.

When `draft` is true, `progressPath` does not exist and you write it (Draft). Otherwise you check the structure that exists (Check). Either way, finish with Report.

## Draft

1. Read `prdPath` in full, then enough of the code to see where the work lands. Delegate wide reading to one `Explore` agent.
2. Find the repositories the plan changes: the PRD names them; `repoHint` is the main session's guess when it does not. `base` is each repo's default branch unless the PRD says otherwise. `check` is the command that runs the repo's whole test suite, taken from its `CLAUDE.md`, CI configuration or build files; leave it empty only when the repo has none.
3. Cut the work into blocks per `blocks.md`. One block is the default and the common answer.
4. Write `progressPath` in `layout.md`'s format, with every frontmatter key present. `settings` holds the values the user asked for; every other key takes its default. Set every block's status to `todo`.
5. For each block, write `blocksDir/<block>.md` holding its title, its `Implements:` line and empty `## Tasks` and `## Log` sections. A draft agent per block writes the tasks, working only from that line, so name the PRD sections precisely; when two blocks share a section, say which items of it each one takes.
6. Commit per `step.md` with a message such as `progress: cut into blocks`.

## Check

1. Read every block file. A block whose status is `running`, `done` or `merged` is frozen: never edit its file, move a task into or out of it, or change its rows or edges.
2. Judge the structure against `blocks.md` and `layout.md`. Look for:
   - **cut** — a block too thin to earn its worktrees; two blocks so coupled they are one; a block holding independent halves each large enough to run in parallel.
   - **edge** — a dependency the diagram lacks, or an edge naming no real dependency.
   - **isolation** — two blocks with no path between them writing the same file. Compare their tasks' `Files:` lists, and the PRD where a block has no tasks yet.
   - **coverage** — an in-scope PRD item no block's `Implements:` covers, or one that two blocks cover.
   - **worktree** — a `Repos` or `Worktrees` row missing, wrong against the repositories on disk, or not following the naming in `layout.md`; a `check` that is empty while the repo has a test suite, or that does not run from the repo root.
3. `planIssues` lists defects the per-block agents found and could not fix. Those located in `progressPath` are yours: treat each as a candidate finding. Leave those in the PRD for the user.
4. Check each finding against the plan and the code; drop what you cannot point at. Rate each per `~/.claude/skills/common/rating.md`, as plan mechanics. `ledger` lists every finding earlier passes returned; mark one `fresh` false when the ledger already holds it, however reworded.
5. Fix every real finding, whatever its severity: move tasks between block files, renumbering both files per `tasks.md`; add or remove edges; merge or split blocks; correct rows. A moved task keeps its spec word for word. Never bend the cut to make a finding go away: when two cuts are equally sound, keep the existing one. A fix in an intent-question class per `step.md` gets outcome `question`.
6. Commit per `step.md` with a concise message such as `progress: merge docs into api block`.

## Report

- `shaBefore` and `shaAfter` per `step.md`, the first read before you changed anything.
- `blocks`: one entry per block in `progressPath`, with its status, its count of top-level tasks, its count of unticked ones, and `changed` true when this pass created it or changed its file's tasks. Each changed block gets a review round next.
- Every finding with its outcome, the intent questions, and `prdIssues`: defects in the PRD that stop the plan from being cut.
- `resolvedIssues`: the entries of `planIssues` you fixed, copied verbatim.
