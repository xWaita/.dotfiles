---
name: git
description: Git conventions for commits, amends, and pull requests. Trigger on any git operation — "commit", "push", "amend", "PR", "pull request", "rebase", "stash" — and whenever code or config files are created or edited: a commit usually follows, and these conventions must be loaded before that point, not at it.
user-invocable: false
---

# Git Conventions

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

- Never commit unless the user asked for one. Finishing a task is not an implicit request, and neither is a task whose subject is git-adjacent, such as editing `.gitignore`. Leave the work staged or unstaged and say it is ready to commit.
- Before the first commit in a repo, check `git config user.email` resolves to the user, not a machine default — a wrong author on a root commit can only be fixed by rewriting it.
- Never put "Co-Authored-By" lines in commit messages.
- One coherent piece of work is one commit. Splitting it by sub-topic — the fix and its test, the code and its doc, one review's findings by theme — is noise: the change-set is what a reader wants to see whole. Two commits need two subjects that are genuinely unrelated, not one subject viewed at two zoom levels. Mechanical sweeps over files the work did not otherwise touch (a formatter run, a rename) are the common real exception.
- Amend into an existing commit instead of adding one when `git branch -r --contains <sha>` is empty — nothing is published, so no history others hold is rewritten — and one subject still describes the combined change. Broadening that subject is fine; needing a second, unrelated clause means two commits, however related the work felt.
- Amending HEAD is `git commit --amend`. For an older commit: `git commit --fixup=<sha>` then `git rebase --autosquash <sha>~1`, which needs no interactive editor. To also replace the target's message, skip `--fixup` — it rejects `-m` and `-F` — and write the message yourself with `amend! <sha>` as its first line.
