---
name: ralph-refine
description: Harden a ralph plan unattended — loop /ai-review → fix → /ai-compact over a plan directory's PRD.md (and PROGRESS.md when it exists) until a review finds no Critical/High/Medium findings, committing each round and keeping a per-fix ledger that single fixes can be reverted from. Manual only; run it with /ralph-refine, naming the plan directory to harden one other than ralph/, optionally --rounds N.
argument-hint: "[plan dir] [--rounds N]"
disable-model-invocation: true
---

# Ralph Refine

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

Arguments: $ARGUMENTS

Invoking this skill is the user's request to commit: each round commits the plan files and the ledger.

## 1. Resolve the plan

- The plan directory is the argument, else `ralph/`; an archived or staged plan under `ralph/` qualifies too. It holds `PRD.md`, and `PROGRESS.md` once one exists, directly inside it; never search deeper or accept arbitrary files. No `PRD.md` is an error.
- Without `PROGRESS.md` the run is spec-only: the reviewer skips checklist mechanics.
- `--rounds N` caps rounds, default 50 — a backstop; the loop ends at the first review with no Critical/High/Medium. One round of a ~1000-line plan costs ~200k subagent tokens and ~30 minutes.
- The ledger is `REFINE.md` beside the PRD, committed every round because `ralph/RULES.md` reads an untracked file as interrupted work. An existing ledger means this run continues it — its numbering and its declined/applied history; the user deletes it to start fresh.

## 2. Preconditions

Stop and tell the user when either fails:

- The plan files are inside a git repo; plans outside git, such as `~/.claude/plans/` files, are out of scope.
- `git status --porcelain -- <plan files> <ledger>` is empty — otherwise round 1's commit absorbs the user's edits. Ask them to commit first.

## 3. Run the loop

Workflow rejects a `scriptPath` outside the working directory, so read `scripts/refine.js` from this skill's directory and pass its text as `script`. For an existing ledger, take the numbering from it:

```bash
grep -o '^## Round [0-9]*' <ledger> | tail -1               # firstRound is that + 1
grep -o 'F[0-9]*' <ledger> | tr -d F | sort -n | tail -1    # firstId is that + 1
```

`args`, with `firstRound` and `firstId` both 1 for a new ledger:

```json
{"files": ["<abs path>", "..."], "maxRounds": 50, "ledgerPath": "<abs path>/REFINE.md", "firstRound": 1, "firstId": 1}
```

Each round is two fresh agents: review+fix, then compact+record, which commits `plan: refine round N`. Their instructions are `references/review.md` (which hands off to `references/fix.md` once the report is written) and `references/record.md`; edit those to change agent behavior. The script only sequences the agents and renders the ledger entries and commit message.

## 4. On return

The run returns `{stopReason, intentQuestions}`, every round already committed to the ledger. `stopReason` is `converged` (no Critical/High/Medium), `stalled` (a round applied nothing, so another review would see the same text) or `cap`.

- Run `scripts/report.py <ledger>` and open with its table: severity mix, applied/declined, cumulative findings, plan growth, and the blocking trend that shows whether the loop converges.
- Then the stop reason, and from this run's `## Round` sections of the ledger (those from `firstRound` on) every applied fix, every declined and conflict finding, one line each; then the intent questions — the returned `intentQuestions` plus any `- Intent ·` line from those rounds the list lacks. Ask the user to decide the conflicts and intent questions.

If the workflow errors instead, an agent failed after the runtime's retries; every earlier round is committed. Name the failed round and list the `- Intent ·` lines from this run's committed rounds for the user to decide; if the tree is dirty, `git stash push -- <plan files> REFINE.md` returns to the last checkpoint. Rerun to continue.

## 5. Reverting a fix

When the user asks to revert `F<n>`: read its ledger row, find its round commit with `git log -1 --grep '^plan: refine round N$'` and `git show` it to see the original edit, then undo it by meaning against the current text — later compaction may have moved it, so `git revert` of the round is wrong. Mark the row `reverted` in the ledger and commit `plan: revert F<n>` with the plan files and ledger only.
