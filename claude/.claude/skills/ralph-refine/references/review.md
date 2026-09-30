# Reviewing a plan round

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

Your prompt gives the parameters named below.

1. Read `~/.claude/skills/ai-review/SKILL.md` and follow it as your instructions to review `files` as one design.
2. Rate every finding exactly as that skill's Rating section prescribes.
3. When `files` has no PROGRESS.md, the review is spec-only: skip plan-mechanics findings about the task checklist.
4. The ledger at `ledgerPath` is not part of the plan under review. When it exists, read it first as the record of earlier rounds: do not re-raise a declined finding or a recorded `Intent ·` question, and do not propose reversing an applied one, unless you cite a concrete consequence that its entry does not already address.
5. Write the complete report in your reply, numbering findings from `F<firstId>` upward in report order.
6. Only then read `fix.md` beside this file for the next step. Reading it earlier lets fixability shape the ratings, and the loop's stop signal depends on them.
