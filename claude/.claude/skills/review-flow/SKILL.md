---
name: review-flow
description: Run a refactor → perf → correctness review loop as a dynamic workflow over code (a branch, PR/MR, commit range or paths) or a plan (a ralph plan directory or plan files). Each round, separate agents apply /refactor-review --fix, apply /perf-review --fix, compact a plan as /ralph compact does, then run /code-review high on code or the /ralph review lens on a plan and fix every real finding, each committing its own work, until the correctness review turns up no fresh Medium-or-higher finding. Attended: watch it in /workflows. Manual only; run it with /review-flow from inside the repo, optionally naming the target and --rounds N.
argument-hint: "[branch | PR/MR number | commit range | paths | plan dir | free-form description] [--rounds N]"
disable-model-invocation: true
---

# Review Flow

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

Arguments: $ARGUMENTS

Invoking this skill is the user's request to commit: each round's refactor, perf, compact and review steps are one commit each. The exception is an unversioned plan, which is edited in place and never committed.

## 1. Resolve a stable target

Every step takes the same explicit `target`, and it must still mean the same code after the loop's own commits land. The argument is free-form: resolve whatever the user wrote ("last commit", "the last 3 commits", "since abc123", "the auth module") from git and the repo into one of the forms below. Ask only when two forms fit equally well, never because the wording matches none of them.

- A branch: itself; it must be checked out in `repoDir`.
- A commit range ("last commit", "since X"): `<base-sha>..HEAD`, with the base pinned to a full sha now — `HEAD~1` would drift as the loop commits. The end stays `HEAD`, so the loop's own commits fall inside the range.
- A PR number (`gh pr view <n> --json headRefName`) or MR number (`glab mr view <n>`): its head branch, which must be checked out. Never pass the number on: code-review on a PR reviews the remote diff, which never sees this loop's unpushed commits.
- Paths: as given. A plan is a paths target: a ralph plan directory (`PRD.md`, plus `PROGRESS.md` and `blocks/` when they exist; see `ralph/references/layout.md`), or the plan files themselves. A plan inside a git work tree is versioned and its edits are committed. A plan outside one, such as `~/.claude/ralph/<plan>/`, is unversioned: `versioned` is false, and its edits are made in place with no commits.
- No target: the current branch. If that is the default branch, ask for a branch or paths and stop — "the uncommitted diff" is empty after the first commit.

`repoDir` is where the target lives and where the loop commits:

- the directory a caller passes, such as a deliverable's worktree from `/ralph run`;
- else `git rev-parse --show-toplevel` of a versioned plan's directory, for a plan target;
- else the plan directory itself, for an unversioned plan;
- else `git rev-parse --show-toplevel` of the working directory.

`repoDir` need not be the session's working directory: resolve the target there, and give every git command `-C <repoDir>`.

`--rounds N` caps rounds, default 100.

## 2. Preconditions

Stop and tell the user when any fails:

- `repoDir` is inside a git work tree, unless the target is an unversioned plan, which skips this check and the next.
- `git -C <repoDir> status --porcelain` is empty. Otherwise ask whether it is the user's own edits (the first commit would absorb them) or an interrupted run of this loop — "interrupted" means proceed.
- The session can commit without a prompt per tool call (auto or bypass mode, or allow rules); otherwise the run stalls on a permission prompt.

## 3. Run the loop

Workflow rejects a `scriptPath` outside the working directory, so read `scripts/review-flow.js` from this skill's directory and pass its text as `script`, with `args`:

```json
{"target": "<resolved target>", "repoDir": "<absolute repoDir>", "plan": false, "versioned": true, "maxRounds": 100}
```

`plan` is true when the target is plan files or a plan directory. `versioned` is false only for an unversioned plan.

Each round runs these steps in order, each a fresh agent committing its own work, so no agent grades its own diff and every commit is reviewed for correctness in its own round:

- **Refactor**, then **perf**: each applies real Medium+ findings and easy-win Lows, and commits nothing when there is nothing real. Expect both to go quiet well before the review does. They still run every round, because one round's correctness fixes can need refactoring or tuning in the next.
- **Compact**, on a plan only: compacts the plan files per `ralph/references/compact.md`, because every fix leaves text beside what it replaced and an uncompacted plan bloats round over round. It runs before the review so a cut that loses a fact gets caught.
- **Review**: the plan correctness lens, `ralph/references/review.md`, on a plan; on anything else, `/code-review high` plus a check of the target's tests against the `testing` skill.

Each step's instructions are `references/<step>.md` (`refactor`, `perf`, `compact`, `review`), all built on `references/round.md`; edit those to change agent behavior. The script only sequences the agents, keeps the ledgers of review findings and applied refactors and perf changes, and checks what they report.

The stop signal is the review's: a round ends the loop when its review fixed no fresh Medium-or-higher finding. "Until no findings" would never converge — the review samples a new batch every run and each round's fixes are new code — while the Medium+ count falls round over round.

## 4. On return

The run returns `{stopReason, rounds, intentQuestions, flagged}`; every round in `rounds` is committed, or on an unversioned plan written in place. Report the stop reason, then one line per round: refactors applied, perf changes applied with their estimates, compaction edits on a plan, review fixed/declined, fresh Medium+ count, short shas.

- `converged` — the last review found nothing fresh at Medium or above.
- `cap` — rerun `/review-flow` if the per-round Medium+ count was still falling; if it was flat, the reviewer is churning and another run will not help.
- `blocked: …` — relay the agent's reason.

Then list, deduplicated, what the loop left for the user to choose from:

- The intent questions from every step: capabilities, design choices, migration costs and tradeoffs.
- The refactor and perf findings left below the floor (`rounds[].belowFloor`), which the loop did not apply.
- On a plan, the `flagged` passages the compact step kept rather than risk losing a fact.

If the workflow errors instead, an agent died; the error names the round and step. The usual cause is a usage limit that Claude Code did not wait out; it waits only in an interactive terminal session (Claude Code workflows doc, "When a run hits your usage limit").

- Leave the tree alone and relaunch once. When the failure notice carries a `<recovery>` call (`scriptPath` plus `resumeFromRunId`), use it: it replays the finished steps and keeps the ledgers. Otherwise run the loop again from § 3. Either way the relaunched step carries the dirty tree forward.
- Report a second failure at the same step instead of relaunching again.
