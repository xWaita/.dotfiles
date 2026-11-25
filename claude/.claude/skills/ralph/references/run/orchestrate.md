# Ralph run: orchestrate

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

The main session's instructions for `/ralph run`: start one block workflow per runnable block, land each block as it finishes, then review and publish each deliverable.

`/ralph run` is the user's request to commit in the block worktrees, to commit plan files of a versioned plan, and to push and open MRs as the plan's settings say.

## Contents

1. Resolve
2. Validate
3. Preconditions
4. Schedule
5. When a block returns
6. Deliverables
7. Report

## 1. Resolve

- The plan directory comes from `SKILL.md` § Plan resolution. With `PRD.md` but no `PROGRESS.md`, point at `/ralph create progress` and stop. Never create, move or archive a plan directory here; a finished plan stays put and a rerun against it is a no-op. Convert a pre-block `PROGRESS.md` first, per `references/layout.md` § Other shapes.
- Read `references/layout.md` and `references/blocks.md`, then `PROGRESS.md`. Read nothing else yourself — not the PRD, not the code, not the block files beyond what a step below names. The agents read those in their own contexts.
- Settings are `PROGRESS.md`'s frontmatter, with `layout.md`'s defaults for absent keys. The request may add, in prose:
  - **Which blocks** to run. Default: every block.
  - **A one-off override** of a frontmatter key ("sequentially", "skip the MR this time", "review at medium"). It applies to this run only; never write it back. `land` is structural and cannot be overridden.
  - **A limit** ("stop after two tasks"): `maxTasks` for each block workflow. Default 100, a backstop against a checklist that never empties, not a target.
- State the resolved settings in one line before starting anything, so a misread request is visible: the blocks, the parallel cap, `land`, `blocking`, review effort, final review, MR, task limit.

## 2. Validate

Refuse the run, naming the row, when:

- the diagram has a cycle, or names a block with no row in `## Blocks`;
- a block has no `## Worktrees` row or no file under `blocks/`;
- a `## Worktrees` row names a repo with no `## Repos` row, or a `## Repos` path is not a git repository, or its `base` is not a branch there;
- under `land: combined`, a `## Repos` row lacks its `branch` or `worktree`;
- `blocking` is set under `land: combined` and the plan deadlocks per `blocks.md` § Blocking: say to use `land: split`;
- a block named in the request depends on a block that is neither done nor selected.

On a rerun, first move blocks from `done` to `merged`: a block is merged when every deliverable holding its work is merged. Decide per deliverable by its MR's state (`gh pr view <branch> --json state`, `glab mr view <branch>`); with no MR, by `git -C <path> fetch origin <base>` and `git merge-base --is-ancestor <branch> origin/<base>`; failing both, ask the user.

## 3. Preconditions

Stop and tell the user when any fails:

- The session can commit without a prompt per tool call (auto or bypass mode, or allow rules); otherwise the run stalls on a permission prompt.
- The plan directory, every repo path and `~/worktrees` are readable and writable from this session. Add what is outside the working directory with `/add-dir`, or the agents are permission-blocked.
- Each selected block's existing worktrees are clean, unless the block is `running`: that is an interrupted block, which its implement agent resumes. A dirty worktree of a `todo` block holds someone's edits: ask.
- A `running` block that this session did not start may be live in another session, and a second workflow in the same worktrees corrupts both. Resume it only when `find <worktree> <block file> -mmin -15 -not -path '*/.git/*' -print -quit` prints nothing for each of its worktrees; otherwise ask whether another session is running it.
- Under `land: combined`, each existing `{plan}` worktree is clean.
- A versioned plan directory holds no uncommitted edits except `PROGRESS.md` and the files of `running` blocks. Otherwise ask whether they are the user's.
- A plan that sits inside a block worktree has exactly one block and one repo (`layout.md`).

## 4. Schedule

Repeat until nothing is runnable and no block workflow is live.

1. A block is **runnable** when it is selected, its status is `todo` or it is `running` with no live workflow in this session, and every block it depends on is satisfied. A dependency is satisfied when it is `done` or `merged`; where `blocking` gates the edge (`blocks.md` § Blocking), only when it is `merged`.
2. Start runnable blocks until `parallel` are live (0 means no cap). For each:
   - Create its missing branches and worktrees per `blocks.md` § Landing. Resolve `~` to absolute paths.
     ```
     git -C <repo path> fetch origin <base>                    # only when the repo has a remote
     # land: combined, once per repo — the {plan} branch:
     git -C <repo path> worktree add --no-track -b <plan> <plan worktree> origin/<base>
     # land: combined — a block, forked from the {plan} tip:
     git -C <repo path> worktree add -b <plan>-<block> <block worktree> <plan>
     # land: split — a block, forked from base or from the unmerged dependency it stacks on:
     git -C <repo path> worktree add --no-track -b <plan>-<block> <block worktree> <origin/<base> | dependency branch>
     git -C <block worktree> merge --no-ff <another unmerged dependency's branch>
     ```
     - `--no-track` keeps a later push from targeting `base`. With no remote, fork from the local `<base>`.
     - A branch that already exists is a rerun: `git worktree add <worktree> <branch>` when only the worktree is missing, and nothing when both exist.
     - A one-block plan under `combined` has no block branch: its worktree is the `{plan}` worktree.
     - Note what each deliverable forked from; § 6 needs it.
   - Set its status to `running` in `PROGRESS.md`.
   - Start its workflow. Workflow rejects a `scriptPath` outside the working directory, so read `scripts/run.js` from this skill's directory once and pass its text as `script`, with `args`:
     ```json
     {"prdPath": "<plan dir>/PRD.md", "progressPath": "<plan dir>/PROGRESS.md", "blockPath": "<plan dir>/blocks/<block>.md", "worktrees": [{"repo": "api", "path": "/home/me/worktrees/api/checkout-cart"}], "review": "high", "maxTasks": 100}
     ```
     All paths absolute. `worktrees` holds the block's `## Worktrees` rows. The call's result names the file the script was saved to: pass that as `scriptPath`, in place of `script`, for every later start in this session.
3. Wait for a workflow's completion notice; never poll. Then do § 5 for that block and return to step 1.

Each task is two fresh agents — implement, then review+commit — so no agent grades its own diff. Their instructions are `references/run/implement.md` and `references/run/review-commit.md`, both built on `references/run/step.md`; edit those to change agent behavior. The script only sequences the agents and checks what they report.

While blocks run, review forks deliver their findings to this session as agent messages. They are copies of what the block agents already read: ignore them, and never act on or answer one.

Never hand-finish a task in this session: every commit must pass review by an agent that did not write it.

## 5. When a block returns

The workflow returns `{stopReason, block, tasks}`; every task in `tasks` is committed.

- `complete` — no unchecked box remains. In order:
  1. **Land.** Under `land: combined`, in each repo the block changed: `git -C <plan worktree> merge --no-ff <plan>-<block>`. On a conflict, `git merge --abort`, leave the block `running`, and report it: two unordered blocks wrote the same file, which the cut must fix. A one-block plan has nothing to merge. Under `land: split` there is no merge.
  2. **Check.** In each repo the block changed, run the repo's `check` from the root of the tip the block's dependents fork from: the `{plan}` worktree under `combined`, the block's worktree under `split`. Each task's proof ran that task's tests only, so this is the first run of the whole suite on the merged code. An empty `check` skips this step; say so in the report.
     - Send the output to a file and read only the tail of a failure. Run it in the background when it may outlast the Bash timeout, and merge nothing else into that worktree until it returns.
     - On a failure, never fix it in this session. Under `combined` with a block branch, bring the block's worktree up to the merged tip: `git -C <block worktree> merge --ff-only <plan>`. Append one unticked task to the block file: make `<check>` pass without weakening a test, with the failing tests and the tail of the output as its Spec and the `check` as its Proof. Start the block's workflow again; when it completes, land and check again.
     - When the check fails a second time, leave the block `running` and report it. Its dependents do not start.
  3. **Fold the Log.** Read the block file's `## Log`. Where an entry records a divergence from the PRD, edit `PRD.md` to describe what was built, as current state.
  4. Under `land: split`, do § 6 for the block's deliverables now, before its dependents fork from them.
  5. Set its status to `done`. On a versioned plan, commit the plan files by path: `git -C <plan dir> add -- <plan dir>` then `git -C <plan dir> commit -m "plan: <block> done" -- <plan dir>`. A plan inside its own block worktree was already committed with each task; commit what remains the same way.
  6. Under `land: combined`, do § 6 for each repo whose deliverable is now complete.
- `cap` — boxes remain. The block stays `running`; rerunning `/ralph run` resumes it.
- `blocked: …` — the block stays `running`. Relay the agent's reason.
- The workflow errors instead: an agent died, and the error names the task. The usual cause is a usage limit that Claude Code did not wait out; it waits only in an interactive terminal session (Claude Code workflows doc, "When a run hits your usage limit").
  - Leave the worktrees alone and start the block's workflow again, as a fresh run and never with `resumeFromRunId`. The next implement agent resolves whatever the dead agent left (a dirty tree, a ticked box with no commit, a commit never reported); a replayed review step does not.
  - When it errors again with no new commit in the block's worktrees since the previous error, leave the block `running` and report it. Rerunning `/ralph run` continues it.

A block that did not complete starts none of its dependents. Blocks that do not depend on it keep running.

## 6. Deliverables

A deliverable is complete when its block is (`split`), or when every block with a worktree in its repo is done (`combined`). For each complete deliverable, in its worktree:

1. **Final review**, when `final-review` is true and the deliverable has commits. Its range starts at the fork point: `git -C <worktree> merge-base <what it forked from> HEAD`, pinned to a full sha. Read `~/.claude/skills/review-flow/SKILL.md` and follow it with the target `<sha>..HEAD` and `repoDir` set to the deliverable's worktree. Deliverables in different worktrees may be reviewed at the same time.
2. **Check again**, when the final review committed anything: run the repo's `check` in the deliverable's worktree. On a failure, do not publish; report it with the tail of the output.
3. **Publish**, when `mr` is true and the repo has a remote; with no remote, skip it and say so.
   - `git -C <worktree> push -u origin <branch>`.
   - Open a draft MR/PR with the tool matching the remote's host: `gh pr create --draft --base <target> --head <branch>`, or `glab mr create --draft --target-branch <target> --source-branch <branch>`. When one is already open for the branch, the push updated it.
   - `<target>` is the repo's `base`. Under `split`, a block stacked on a single unmerged dependency targets that dependency's branch.
   - Title and body follow the `git` skill and the repo's conventions: what the deliverable changes, from the plan title and the summaries of the blocks it holds. Never cite the plan directory.

## 7. Report

When nothing is runnable and no workflow is live, report:

- per block: its status, the workflow's stop reason, and one line per task (id, title, short shas, findings fixed of found);
- per deliverable: branch, worktree, the `check` result, final-review stop reason with what it left for the user, and the MR/PR link;
- what waits, and on what: a block behind an incomplete dependency, or behind a merge under `blocking`. After the user merges, `/ralph run` continues;
- under `combined`, the merged blocks' worktrees and branches, which are left in place. Removing them is the user's call.

When every block is `done` or `merged`, check whether the plan's or the repos' docs (a `CLAUDE.md` beside the plan or at a repo root) call for archiving a finished plan. If they do, name that step in the report: it falls to this session, not to the loop.
