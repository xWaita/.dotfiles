---
name: ralph-progress-flow
description: Make a ralph plan's PROGRESS.md well-specified and well-sized for implementing its PRD.md, as a dynamic workflow. When PROGRESS.md is missing, an agent first drafts it from PRD.md and the code. Each round is one agent: it reviews every task and the whole checklist against the PRD, the code and the ai-plan ralph conventions (guesses, false premises, proofs, coverage, order, sizing), fixes what it finds and commits, then compacts PROGRESS.md with /ai-compact and commits, until a round fixes no fresh Medium-or-higher finding and merges no tasks. Run it before /ralph-flow or /ralph. Attended: watch it in /workflows. Manual only; run it with /ralph-progress-flow from inside the repo, naming the directory holding PRD.md and PROGRESS.md when it is not ./ralph/, optionally --rounds N.
argument-hint: "[plan dir] [--rounds N]"
disable-model-invocation: true
---

# Ralph Progress Flow

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

Arguments: $ARGUMENTS

Invoking this skill is the user's request to commit: the draft is one commit, and each round commits its review fixes and its compaction separately. It edits `PROGRESS.md`, plus task-number references in `PRD.md`; it never touches code or the spec itself — spec defects come back as PRD issues, for `/review-flow` on the plan or the user.

## 1. Resolve the plan

- The plan directory is the argument, else `./ralph/` of the working directory. `PRD.md` must sit directly inside it; when it does not, name the path you looked for and stop. Never search deeper or fall back to another directory.
- `PROGRESS.md` is `<plan dir>/PROGRESS.md`. `draft` is true when it does not exist.
- `repoDir` is `git rev-parse --show-toplevel` of the working directory: the code the tasks are checked against. When it fails, the working directory is outside a git repo: say so and stop.
- `PROGRESS.md`'s path, existing or not, must sit inside `repoDir` and `git check-ignore -q <path>` must fail (not ignored): every step commits. Otherwise say so and stop.
- `--rounds N` caps rounds, default 50 — a backstop against churn, not a target.

Read nothing else yourself — not the PRD, not the code. Every agent that needs them reads them in its own context, which keeps this session's small.

## 2. Preconditions

Stop and tell the user when any fails:

- `git status --porcelain -- <plan dir>` is empty. Otherwise ask whether the edits are the user's (the first commit would absorb them) or an interrupted run of this loop — "interrupted" means proceed. The rest of the tree may be dirty: commits name the plan files by path.
- The session can commit without a prompt per tool call (auto or bypass mode, or allow rules); otherwise the run stalls on a permission prompt.

## 3. Run the loop

Workflow rejects a `scriptPath` outside the working directory, so read `scripts/ralph-progress-flow.js` from this skill's directory and pass its text as `script`, with `args`:

```json
{"prdPath": "<plan dir>/PRD.md", "progressPath": "<plan dir>/PROGRESS.md", "repoDir": "<repo root>", "draft": false, "maxRounds": 50}
```

All paths absolute.

- **Draft**, once, only when `draft` is true: an agent writes `PROGRESS.md` from the PRD and the code.
- Then each round is one agent, in one context so the plan and rules are read once:
  - **Review**: every unticked task read as the ralph session that will implement it, plus what only the whole checklist shows. Fixes every real finding, splits over-ceiling tasks, commits.
  - **Compact**, in round 1 and whenever the review fixed something: `/ai-compact` on `PROGRESS.md` — wording, redundancy, merging under-floor tasks — then commits. A round that merged tasks always gets one more review, since a merge writes a new task spec.

Compaction merges only under-floor tasks and the review splits only over-ceiling ones, so the two cannot undo each other's task shapes. Agent instructions are `references/draft.md` and `references/review.md`, both built on `references/round.md`; edit those to change agent behavior. The standard they enforce is `ai-plan`'s Tasks section, `ai-plan/references/ralph.md` and `~/ralph/RULES.md`; edit those to change what "well-specified" and "well-sized" mean.

The loop stops on the first of:

- `converged` — a review fixed no fresh Medium-or-higher finding and its compaction merged no tasks. Fresh means not in the script's ledger of earlier rounds' findings, however reworded. Lows are fixed but never extend the run: each review samples a new batch, and only the Medium+ count falls round over round.
- `nothing to plan` — no unticked task remains.
- `cap` — `maxRounds` reached.
- `blocked` — an agent declined the work, or reported edits without committing them.

## 4. On return

The run returns `{stopReason, rounds, intentQuestions, prdIssues, flagged}`. Report the stop reason, then one line per round: review fixed and declined, fresh Medium+ count, compaction edits, short sha.

- `converged` — the plan is ready for `/ralph-flow` once the PRD issues and intent questions below are settled; with none, it is ready now.
- `cap` — rerun if the per-round Medium+ count was still falling; if flat, the review is churning on something only the user can settle, usually a PRD issue.
- `blocked: …` — relay the agent's reason.

Then list, deduplicated, what the loop left for the user:

- **PRD issues**: spec defects that blocked a task from being specified. Fix them (or run `/review-flow` on the plan) and rerun.
- **Intent questions**: scope the loop would not add or drop on its own.
- **Flagged**: passages compaction was unsure about and kept.

If the workflow errors instead, an agent failed after the runtime's retries; the error names the step. Leave the plan files alone and rerun: the next step carries their uncommitted edits forward.
