# Ralph progress: orchestrate

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

The main session's instructions for `/ralph create progress` and `/ralph refine progress`: make a plan's `PROGRESS.md` and block files well-cut, well-specified and well-sized for implementing its `PRD.md`.

On a versioned plan this is the user's request to commit: the cut, each draft, and each round's review fixes and compaction are separate commits of plan files, by path. It edits `PROGRESS.md` and the block files only. It never touches code or the PRD: spec defects come back as plan issues, for `/ralph refine plan` or the user.

## 1. Resolve

- The plan directory comes from `SKILL.md` § Plan resolution. `PRD.md` must sit directly inside it; when it does not, name the path you looked for and stop.
- `draft` is true when `PROGRESS.md` does not exist. A pre-block `PROGRESS.md` is converted first, per `references/layout.md` § Other shapes.
- `versioned` is whether `git -C <plan dir> rev-parse --is-inside-work-tree` succeeds. When it does, `git check-ignore -q <plan dir>` must fail (not ignored), or nothing could be committed: say so and stop.
- Which verb:
  - `create progress`: `maxRounds` 0. The loop cuts and drafts, with no review rounds, so the user can edit by hand first. When `PROGRESS.md` already exists, say so, point at `refine progress` and stop.
  - `refine progress`: `maxRounds` 50, or the number of rounds the request names. The cap is a backstop against churn, not a target.
- `blocks` is the blocks the request names, else empty. Named blocks get their rounds only and the cut is left alone; each must already have tasks.
- `settings` is whatever the request says about `PROGRESS.md`'s frontmatter keys ("split", "no MRs", "at most two at a time"), as `key: value` pairs, used only when drafting. `repoHint` is the repository the request names, else `git rev-parse --show-toplevel` of the working directory, else empty.

Read nothing else yourself — not the PRD, not the code. Every agent that needs them reads them in its own context, which keeps this session's small.

## 2. Preconditions

Stop and tell the user when any fails:

- No block workflow of `/ralph run` is live on this plan. Blocks marked `running`, `done` or `merged` are left untouched; a named block must be none of these unless its run was interrupted.
- The plan directory is readable and writable from this session. Outside the working directory, add it with `/add-dir`.
- Versioned: `git status --porcelain -- <plan dir>` is empty. Otherwise ask whether the edits are the user's (the first commit would absorb them) or an interrupted run of this loop — "interrupted" means proceed. The rest of that tree may be dirty: commits name the plan files by path.
- Versioned: the session can commit without a prompt per tool call (auto or bypass mode, or allow rules); otherwise the run stalls on a permission prompt.

## 3. Run the loop

Workflow rejects a `scriptPath` outside the working directory, so read `scripts/progress.js` from this skill's directory and pass its text as `script`, with `args`:

```json
{"prdPath": "<plan dir>/PRD.md", "progressPath": "<plan dir>/PROGRESS.md", "blocksDir": "<plan dir>/blocks", "versioned": false, "draft": false, "blocks": [], "maxRounds": 50, "repoHint": "", "settings": ""}
```

All paths absolute.

- **Cut**, one agent with the plan to itself: on a draft it writes `PROGRESS.md` and an empty file per block; otherwise it checks the block structure and fixes it, moving tasks between blocks where needed.
- **Draft**, one agent per block that has no tasks: writes the block's checklist from the PRD and the code.
- **Round**, one agent per block, all blocks in parallel: reviews every unticked task and the whole checklist, fixes, then compacts. A block repeats rounds until one fixes no fresh Medium-or-higher finding and merges no tasks.
- Then the cut runs again, on whatever the rounds changed, and only the blocks it changes get further rounds. The loop ends when a cut fixes nothing significant and no block file changed after it.

Agent instructions are `references/progress/cut.md`, `draft.md` and `round.md`, all built on `references/progress/step.md` and `~/.claude/skills/common/flow-step.md`; edit those to change agent behavior. The standard they enforce is `ai-md`, `references/layout.md`, `references/blocks.md` and `references/tasks.md`; edit those to change what "well-cut", "well-specified" and "well-sized" mean.

## 4. On return

The run returns `{stopReason, passes, blocks, intentQuestions, planIssues, flagged}`. Report the stop reason; one line per cut pass (fixed and declined findings, fresh Medium+ count, blocks sent to rounds); then per block its own stop reason and one line per round (review fixed and declined, fresh Medium+ count, compaction edits, short sha).

- `drafted` — `create progress` is done. The plan can be edited by hand, then refined.
- `converged` — the plan is ready for `/ralph run` once the plan issues and intent questions below are settled; with none, it is ready now.
- `cap` — a block hit its round cap, or the cut and the rounds kept changing each other's work. Rerun if the per-round Medium+ counts were still falling; if flat, the loop is churning on something only the user can settle, usually a plan issue.
- `blocked: …` — relay the agent's reason.

Then list, deduplicated, what the loop left for the user:

- **Plan issues**: defects in the PRD that blocked a task from being specified or a block from being cut. Fix them (or run `/ralph refine plan`) and rerun.
- **Intent questions**: scope the loop would not add or drop on its own.
- **Flagged**: passages compaction was unsure about and kept.

If the workflow errors instead, or its stop reason is `blocked` on a step that `failed`, an agent died. The usual cause is a usage limit that Claude Code did not wait out; it waits only in an interactive terminal session (Claude Code workflows doc, "When a run hits your usage limit").

- Leave the plan files alone and relaunch once. When the failure notice carries a `<recovery>` call (`scriptPath` plus `resumeFromRunId`), use it: it replays the finished steps and keeps the ledgers. Otherwise run the loop again from § 3. Either way the relaunched step carries the unfinished edits forward.
- Report a second failure at the same step instead of relaunching again.
