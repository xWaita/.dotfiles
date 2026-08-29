---
name: git
description: Git conventions for commits, amends, and pull requests. Trigger on any git operation — "commit", "push", "amend", "PR", "pull request", "rebase", "stash" — and whenever code or config files are created or edited: a commit usually follows, and these conventions must be loaded before that point, not at it.
user-invocable: false
---

# Git Conventions

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

- Never put "Co-Authored-By" lines in commit messages.
- Amend into an existing commit instead of adding one when `git branch -r --contains <sha>` is empty — nothing is published, so no history others hold is rewritten — and one subject still describes the combined change. Broadening that subject is fine; needing a second, unrelated clause means two commits, however related the work felt.
- Amending HEAD is `git commit --amend`. For an older commit: `git commit --fixup=<sha>` then `git rebase --autosquash <sha>~1`, which needs no interactive editor. To also replace the target's message, skip `--fixup` — it rejects `-m` and `-F` — and write the message yourself with `amend! <sha>` as its first line.
