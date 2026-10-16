---
name: review-flow
description: Run a refactor → perf → correctness review loop as a dynamic workflow over code (a branch, PR/MR, commit range or paths) or a plan (a ralph plan directory or plan files) — each round one agent applies /refactor-review --fix and commits, a second applies /perf-review --fix and commits, a third runs /code-review high on code or /ai-review on a plan, fixes every real finding and commits, until the correctness review turns up no fresh Medium-or-higher finding. Attended: watch it in /workflows. Manual only; run it with /review-flow from inside the repo, optionally naming the target and --rounds N.
argument-hint: "[branch | PR/MR number | commit range | paths | plan dir | free-form description] [--rounds N]"
disable-model-invocation: true
---

# Review Flow

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

Arguments: $ARGUMENTS

Invoking this skill is the user's request to commit: each round's refactor, perf and review steps are one commit each.

## 1. Resolve a stable target

Every step takes the same explicit `target`, and it must still mean the same code after the loop's own commits land. The argument is free-form: resolve whatever the user wrote ("last commit", "the last 3 commits", "since abc123", "the auth module") from git and the repo into one of the forms below. Ask only when two forms fit equally well, never because the wording matches none of them.

- A branch: itself; it must be checked out.
- A commit range ("last commit", "since X"): `<base-sha>..HEAD`, with the base pinned to a full sha now — `HEAD~1` would drift as the loop commits. The end stays `HEAD`, so the loop's own commits fall inside the range.
- A PR number (`gh pr view <n> --json headRefName`) or MR number (`glab mr view <n>`): its head branch, which must be checked out. Never pass the number on: code-review on a PR reviews the remote diff, which never sees this loop's unpushed commits.
- Paths: as given. A plan is a paths target: a directory holding `PRD.md` (and `PROGRESS.md` when it exists), or the plan files themselves. The plan files must be inside the repo, so their edits can be committed.
- No target: the current branch. If that is the default branch, ask for a branch or paths and stop — "the uncommitted diff" is empty after the first commit.

`repoDir` is `git rev-parse --show-toplevel`. `--rounds N` caps rounds, default 100.

## 2. Preconditions

Stop and tell the user when any fails:

- The working directory is inside a git repo.
- `git status --porcelain` is empty. Otherwise ask whether it is the user's own edits (the first commit would absorb them) or an interrupted run of this loop — "interrupted" means proceed.
- The session can commit without a prompt per tool call (auto or bypass mode, or allow rules); otherwise the run stalls on a permission prompt.

## 3. Run the loop

Workflow rejects a `scriptPath` outside the working directory, so read `scripts/review-flow.js` from this skill's directory and pass its text as `script`, with `args`:

```json
{"target": "<resolved target>", "repoDir": "<absolute repo root>", "maxRounds": 100}
```

Each round is three fresh agents — refactor, perf, then review — so no agent grades its own diff, and every refactor and perf commit is reviewed for correctness in its own round. The only difference between targets is the review step's lens: `/ai-review` on a plan, `/code-review high` on anything else, where it also checks the target's tests against the `testing` skill. All three steps run every round, because one round's correctness fixes can need refactoring or tuning in the next. The refactor and perf steps never force a change: they apply real Medium+ findings and easy-win Lows, and commit nothing when there is nothing real. Expect them to go quiet well before the review step does. Their instructions are `references/refactor.md`, `references/perf.md` and `references/review.md`, all built on `references/round.md`; edit those to change agent behavior. The script only sequences the agents, keeps the ledgers of review findings and applied refactors and perf changes, and checks what they report.

The stop signal is the review's: a round ends the loop when its review fixed no fresh Medium-or-higher finding. "Until no findings" would never converge — the review samples a new batch every run and each round's fixes are new code — while the Medium+ count falls round over round.

## 4. On return

The run returns `{stopReason, rounds, intentQuestions}`; every round in `rounds` is committed. Report the stop reason, then one line per round: refactors applied, perf changes applied with their estimates, review fixed/declined, fresh Medium+ count, short shas.

- `converged` — the last review found nothing fresh at Medium or above.
- `cap` — rerun `/review-flow` if the per-round Medium+ count was still falling; if it was flat, the reviewer is churning and another run will not help.
- `blocked: …` — relay the agent's reason.

Then list the intent questions — deduplicated, from all three steps: capabilities, design choices, migration costs and tradeoffs the loop left undecided — and the refactor and perf findings left below the floor (`rounds[].belowFloor`, deduplicated) for the user to choose from — the loop applied neither. On a plan target, suggest `/ai-compact` on the plan files: a run's fixes accumulate text that no step compacts.

If the workflow errors instead, an agent failed after the runtime's retries; the error names the round and step. Leave the tree alone and rerun.
