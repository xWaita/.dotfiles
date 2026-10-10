---
name: review-flow
description: Run a refactor-then-review loop as a dynamic workflow over a branch, PR/MR or paths — each round one agent applies /refactor --fix and commits, a second runs /code-review high, fixes every real finding and commits, until a review turns up no fresh Medium-or-higher finding. Attended: watch it in /workflows. Manual only; run it with /review-flow from inside the repo, optionally naming the target and --rounds N.
argument-hint: "[branch | PR/MR number | paths] [--rounds N]"
disable-model-invocation: true
---

# Review Flow

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

Arguments: $ARGUMENTS

Invoking this skill is the user's request to commit: each round's refactor and review are one commit each.

## 1. Resolve a stable target

Both steps take the same explicit `target`, and it must still mean the same code after the loop's own commits land:

- A branch: itself; it must be checked out.
- A PR number (`gh pr view <n> --json headRefName`) or MR number (`glab mr view <n>`): its head branch, which must be checked out. Never pass the number on: code-review on a PR reviews the remote diff, which never sees this loop's unpushed commits.
- Paths: as given.
- No target: the current branch. If that is the default branch, ask for a branch or paths and stop — "the uncommitted diff" is empty after the first commit.

`repoDir` is `git rev-parse --show-toplevel`. `--rounds N` caps rounds, default 5.

## 2. Preconditions

Stop and tell the user when any fails:

- The working directory is inside a git repo.
- `git status --porcelain` is empty. Otherwise ask whether it is the user's own edits (the first commit would absorb them) or an interrupted run of this loop — "interrupted" means proceed.
- No other loop that commits, such as `/ralph-flow`, runs against the repo. A clean tree does not prove that — ask.
- The session can commit without a prompt per tool call (auto or bypass mode, or allow rules); otherwise the run stalls on a permission prompt.

## 3. Run the loop

Workflow rejects a `scriptPath` outside the working directory, so read `scripts/review-flow.js` from this skill's directory and pass its text as `script`, with `args`:

```json
{"target": "<resolved target>", "repoDir": "<absolute repo root>", "maxRounds": 5}
```

Each round is two fresh agents — refactor, then review — so no agent grades its own diff, and every refactor commit is reviewed in its own round. Their instructions are `references/refactor.md` and `references/review.md`, both built on `references/round.md`; edit those to change agent behavior. The script only sequences the agents, keeps the ledgers of review findings and applied refactors, and checks what they report.

The stop signal is the review's: a round ends the loop when its review fixed no fresh Medium-or-higher finding. "Until no findings" would never converge — code-review samples a new batch every run and each round's fixes are new code — while the Medium+ count falls round over round.

## 4. On return

The run returns `{stopReason, rounds, intentQuestions}`; every round in `rounds` is committed. Report the stop reason, then one line per round: refactors applied, review fixed/declined, fresh Medium+ count, short shas.

- `converged` — the last review found nothing fresh at Medium or above.
- `cap` — rerun `/review-flow` if the per-round Medium+ count was still falling; if it was flat, the reviewer is churning and another run will not help.
- `blocked: …` — relay the agent's reason.

Then list the intent questions and the refactor findings left below the floor (`rounds[].belowFloor`, deduplicated) for the user to choose from — the loop applied neither.

If the workflow errors instead, an agent failed after the runtime's retries; the error names the round and step. Leave the tree alone and rerun.
