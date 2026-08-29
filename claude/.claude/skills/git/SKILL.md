---
name: git
description: Git conventions for commits, amends, and pull requests. Trigger on any git operation — "commit", "push", "amend", "PR", "pull request", "rebase", "stash" — and whenever code or config files are created or edited: a commit usually follows, and these conventions must be loaded before that point, not at it.
user-invocable: false
---

# Git Conventions

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

- Never put "Co-Authored-By" lines in commit messages.
- Amend into HEAD instead of adding a commit when `git branch -r --contains HEAD` is empty — nothing is published, so no history others hold is rewritten — and HEAD's subject still describes the result with the new change folded in. Needing a different subject means two commits, however related the work felt.
- Only HEAD: a revision to an older unpushed commit is its own commit, since interactive rebase is unavailable here.
