# Block conventions

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

When a plan is cut into blocks, how blocks depend on each other, and how their branches fork and land. Read when cutting or checking a plan's blocks, and by the main session before a run. `references/layout.md` gives the `PROGRESS.md` format.

## Cutting

A block buys isolation: its own worktrees and branch, so it runs while other blocks run. It costs worktrees, a merge, and under `land: split` its own final review and MR.

- Default to one block. Cut a second only when it can proceed independently of the first and holds enough tasks to pay for its worktrees and branch: several, never one or two.
- Cut for isolation, not organisation. Work that is merely a different topic stays in one block, where task order already sequences it.
- A repository boundary is a common cut, not a required one. A change tightly coupled across two repos is one block spanning both, with one worktree per repo.
- A block holding two independent halves, each large enough to run alone, is two blocks.
- Two blocks so coupled that one cannot be reviewed or proven without the other's unmerged code are one block.
- Where work cannot be isolated, do not force a block.

## Edges

- `a --> b` in the dependency diagram means b builds on code a produces. Keep edges minimal: every edge serialises two blocks.
- An edge must name a real dependency: b reads, calls or extends something a writes. Shared subject matter is not a dependency.
- **Disjoint files.** Two blocks with no path between them in the diagram may run at the same time, so in every repo they share they must write disjoint files. When they would write the same file, add an edge or merge the blocks.
- An edge between blocks in different repos means the dependent needs code that is unmerged in another repo. The dependent block's `## Rules` must say how it sees that code (for example a path dependency on the dependency's worktree). When there is no way, the plan sets `blocking`.

## Landing

A **deliverable** is a branch that becomes one MR/PR. `land` sets what the deliverables are.

Whenever a block finishes, the repo's `check` (`references/layout.md` § PROGRESS.md) runs on the tip its dependents fork from, before any of them starts. Disjoint files keep two blocks from conflicting, not from breaking each other.

### `land: combined` (default)

One deliverable per repo: the `{plan}` branch.

- In each repo it changes, a block forks from the tip of the `{plan}` branch when it starts, and is merged back with `--no-ff` when it finishes. A dependent therefore always forks from a tip that holds its dependencies.
- The `{plan}` branch forks from `base`. A one-block plan works on it directly, with no block branch.
- A merge conflict means two unordered blocks wrote the same file, which Disjoint files forbids: abort the merge, stop, and report it.
- A repo's deliverable is complete when every block with a worktree in that repo is done. Final review and the MR happen then, once per repo, over the combined change.

### `land: split`

Every block branch is a deliverable.

- In each repo, a block forks from `base`, or from the tip of its unmerged dependency in that repo, which stacks it. With several such dependencies it forks from the first and merges the rest in; a conflict there blocks the block and is reported.
- Each block branch gets its own final review and MR as soon as the block is done. A stacked block's MR targets the branch it is stacked on when that is a single unmerged dependency, else `base`.

## Blocking

`blocking: true` makes a dependency a start condition: a block starts only once the deliverables it depends on are merged into `base`. It is for plans whose blocks must not build on unmerged code. Independent blocks keep running, and a run ends when everything left waits on a merge.

- Under `split`, every edge is gated: b starts when a is `merged`.
- Under `combined`, an edge is gated only when a changes a repo that b has no worktree in. Otherwise b already forks from a `{plan}` tip holding a's work, in a deliverable both blocks share.
- Under `combined`, a gated block waits on a whole repo's deliverable, which needs every block in that repo done. When one of those blocks in turn depends on the waiting block, nothing can ever start. A run refuses such a plan and says to use `split`.
