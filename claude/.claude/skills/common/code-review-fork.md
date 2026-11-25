# Driving code-review from an agent

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

How a workflow agent runs the `code-review` skill and gets its findings back. The caller supplies the effort level and the target, and decides what to do with the findings.

1. Make a tag no other review shares: `review-$(date +%s%N)`.
2. Invoke `code-review` through the Skill tool with the arguments `<effort> <target> [<tag>]`. Name the effort level explicitly, since an omitted level reuses whatever was typed last. Do not pass `--fix`; fixing, formatting and testing stay with the caller.
   - The skill runs in a fork, which starts in the session's working directory, not in a directory you changed into. It reviews that directory's diff unless the target says otherwise.
   - To review a worktree, make the target `the uncommitted diff of the git worktree at <absolute path> (git -C <absolute path> diff HEAD)`. For commits, make it `<range> in the git worktree at <absolute path> (git -C <absolute path> diff <range>)`.
3. The Skill call's result carries no findings: the fork's own instructions demand one StructuredOutput call, which takes your schema instead, and the fork writes no findings text before it, even when asked to. Run `python3 scripts/await-review.py --tag <tag>` (relative to this file) with a 600000 ms Bash timeout. It waits for the fork to finish and prints `agent: <id>` as its first line; ignore the rest. It exits 124 on its own timeout or 2 before the fork's transcript exists; run it again until it exits 0.
4. SendMessage the fork by that id (load the tool with ToolSearch `select:SendMessage` when it is deferred): `Reply with your findings as a JSON array of {file, line, summary, failure_scenario}, or [] when there are none.` Then run `python3 scripts/await-review.py <id>` the same way. It prints the fork's reply: the array, possibly followed by prose.
5. Other agents may be running their own reviews at the same time. Reach your fork only through your tag and the id the script printed: never by the name `code-review`, which is not addressable, and never by picking a transcript by recency. Never wait on `ReportFindings`, which the fork does not call.
6. Once the script has printed the reply, you are done with the fork: never message it again. The same reply may also reach you, and the main session, as an agent message, possibly after you have moved on. It is a duplicate: do not answer it or act on it.
