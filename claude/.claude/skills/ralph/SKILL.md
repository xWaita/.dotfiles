---
name: ralph
description: Plan and run development as ralph loops — a PRD.md spec, a PROGRESS.md index of blocks forming a dependency DAG, and one task checklist per block under blocks/, each block implemented in its own worktrees by fresh-context agents with a review before every commit. Holds the plan conventions (the spec/implementation split, cutting blocks, task decomposition and sizing) and the workflows that refine and run a plan. Trigger when working with PRD.md, PROGRESS.md, a blocks/ checklist, a plan under ~/.claude/ralph/ or ~/.claude/plans/, "ralph", or when planning or scoping an AI-agent project. Run /ralph followed by new, change, refine plan, create progress, refine progress, run, status, review or compact, in free text.
argument-hint: "[new | change | refine plan | create progress | refine progress | run | status | review | compact] [plan] [details]"
---

# Ralph

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

Arguments: $ARGUMENTS

A ralph plan is a spec plus blocks of tasks. Each task is implemented by one fresh agent and reviewed, fixed and committed by a second; blocks run in parallel in their own worktrees; a main session schedules them. Invoke the **`ai-md`** skill: plan documents have no reader but an agent.

A verb below acts only when the user typed `/ralph …` or asked for that verb in their own words. Loaded any other way — because a plan file was touched, or from another skill — this skill is conventions only: read the references the work needs, start no workflow, and commit nothing.

## Principles

- **State lives in files, never in a session.** Every agent starts cold and reads the plan, so any run resumes by rerunning it, and a usage limit costs nothing but time.
- **The plan must be self-sufficient.** The implementing agent cannot ask a question; whatever is unstated is guessed silently.
- **Spec and implementation are separate documents.** The PRD states the target state and its invariants; block files state order and steps. Neither restates the other, and the PRD holds no history.
- **One task is one context, one commit, one review.** Its size is bounded below by the cold start and by what a review can judge, and above by fitting the work and its review-and-fix in one window each.
- **Proof before tick.** Each task names a command that fails before it and passes after. Each repo names a `check`, its whole test suite, which must pass on every tip that blocks fork from or that is published.
- **No agent grades its own work.** Code and plans are both reviewed by an agent that did not write them, and every commit is reviewed before it lands.
- **Review points are fixed by the workflow, not chosen in the moment.** That is what makes unattended commits acceptable at any task size.
- **Unattended loops never decide intent.** A fix that drops a capability, replaces a chosen design, costs a migration or trades one cost for another is reported as a question.
- **Loops converge, they do not perfect.** A loop stops when a round fixes nothing fresh at Medium or above; caps are backstops, not targets.
- **Blocks exist for isolation, not organisation.** A block earns its worktrees by being independent and large enough.
- **One writer per file.** It removes every merge problem inside the plan directory.
- **One home per setting.** A setting is a frontmatter key of `PROGRESS.md`; a request overrides it for one run and never writes it back. There are no command-line flags.
- **The main session orchestrates and stays small.** It schedules, merges, gates and reports; agents read the PRD and the code.
- **Plans are ephemeral.** Durable knowledge moves into code, CLAUDE.md and skills; nothing durable cites a plan directory.
- **One loop shape for every size.** A small adhoc change is one block of a few tasks; a programme is many blocks. Scale by composing blocks, never by adding workflow variants. Below one task, skip ralph and make the change inline.

## Conventions

Read the reference a piece of work needs before doing it; never work from memory of one.

| Reference | Holds | Read when |
|---|---|---|
| `references/layout.md` | the plan directory, the `PROGRESS.md` and block file formats, write ownership, Log rules | touching any plan file |
| `references/prd.md` | what a PRD holds, design philosophy | writing, changing or reviewing a PRD |
| `references/blocks.md` | when to cut a block, edges, disjoint files, how branches fork and land, `blocking` | cutting or checking blocks; before a run |
| `references/tasks.md` | what a task pins, task sizing, split and merge | writing, reviewing or implementing a checklist |

Review points, each by an agent that did not write the work:

| Point | Reviewer |
|---|---|
| PRD | `review-flow` on the plan (`refine plan`) |
| Block structure | the cut check of `refine progress` |
| Block checklists | the per-block rounds of `refine progress` |
| Every task | a fresh agent: `/code-review` and the `testing` check, before the commit |
| Every deliverable | `review-flow` over its whole diff |

## Plan resolution

The plan directory is, in order: a path the request names; `~/.claude/ralph/<name>/` when the request names a plan by name; the plan this conversation is already working on; otherwise ask, listing the directories under `~/.claude/ralph/` and any plan directory in the working directory. Never search deeper or guess between two candidates.

## Verbs

The request is free text. Its first words usually name the verb; otherwise route on what it asks for, and ask only when two verbs fit equally.

| Verb | What it does |
|---|---|
| `new <description>` | Write a `PRD.md` for the change |
| `change <what>` | Edit the PRD's design, or blocks and tasks, by hand |
| `refine plan` | Review loop over the plan: refactor → perf → compact → correctness, until converged |
| `create progress` | Cut the PRD into blocks and draft each block's checklist |
| `refine progress` | Check the cut and review, fix and compact every block's checklist, until converged |
| `run` | Implement: one workflow per runnable block, landing each as it finishes |
| `status` | Show where the plan stands |
| `review` / `compact` | One pass of the plan correctness review, or of plan compaction |

The usual order is `new`, `refine plan`, `refine progress`, `run`.

### new

- The plan directory is `~/.claude/ralph/<slug>/`, with a short kebab-case slug of the change, unless the user names a directory. It becomes the plan name and the branch name.
- Read the code being specced against before writing.
- Establish the committed target state from the request, existing plans and project docs. When the change is the first slice of something larger whose later slices are unstated, ask for them before writing the PRD.
- Write `PRD.md` per `references/prd.md`. Write no `PROGRESS.md`: `create progress` does.

### change

- Read the plan first, then edit it per the references above. A PRD edit replaces the text it supersedes.
- Never edit a ticked task, or the file of a block that a workflow is running.
- After a PRD change to a plan that has blocks, say that `refine progress` re-checks the cut and the checklists against it.

### refine plan

Read `~/.claude/skills/review-flow/SKILL.md` and follow it with the plan directory as its target.

### create progress, refine progress

Read `references/progress/orchestrate.md` and follow it.

### run

Read `references/run/orchestrate.md` and follow it.

### status

Read `PROGRESS.md` and count ticked and unticked boxes per block file. Show the blocks table with those counts, the dependency diagram, which blocks are runnable now, and what each other block waits on (a dependency, or a merge under `blocking`). Change nothing.

### review, compact

- `review`: read `references/review.md` and follow it on the plan. It reports and edits nothing.
- `compact`: read `references/compact.md` and follow it on the plan. It edits in place and commits nothing.
- Both also take a single plan file under `~/.claude/plans/`.
