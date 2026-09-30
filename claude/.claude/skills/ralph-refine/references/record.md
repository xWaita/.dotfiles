# Compacting and recording a round

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

Your prompt gives the parameters named below, then the FIXES, LEDGER and MSG blocks between `<<<NAME` and `NAME>>>` markers. Run every git command from the working directory with repo-relative paths: a worktree-isolated session refuses `git -C <dir>`, whose target it cannot verify before the command runs.

1. When FIXES is non-empty, read `~/.claude/skills/ai-compact/SKILL.md` and follow it for `files`. Compaction must preserve the meaning of every fix in FIXES. Do not touch the ledger while compacting. When FIXES is empty, the round applied nothing: do not edit the plan files.
2. Append to the ledger at `ledgerPath`, keeping every line already in it. If it does not exist yet, create it, starting with `# Refine ledger — <date +%F> — <file basenames joined by " + ">` and a blank line. Then append:
   - a blank line, then the header `## Round <round> · <basename> <before>→<after> lines, …`, with one span per plan file. `<before>` comes from `git show HEAD:<path> | wc -l` and `<after>` from `wc -l`. `scripts/report.py` parses this format.
   - the LEDGER block verbatim. The blank line goes before the header, not after the block, so the ledger ends at its last entry and rounds stay one blank line apart.
3. Run `git add --` on `files` and `ledgerPath`, then commit only those paths with `git commit -F - -- <those paths>`. Feed the message on stdin through a quoted heredoc and write no message file. The message is the MSG block verbatim, followed, when compaction ran, by one final line `Compact: <one sentence on what compaction changed>`.

Return the short sha of the new commit.
