# Intent questions

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

Shared by the review skills. Before rating a finding, classify it by what its fix loses or changes:

- **A mechanism only**: how the target delivers its capabilities, with every capability kept. Rate it as a finding.
- **A capability**: something the system can do for its user, however few use it today. This is an intent question, never a rated finding, even when the target declares nothing about it. Only the user knows whether it is a requirement, and silence is no evidence, because compaction cuts rationale. Once the user drops the capability, the mechanisms that served only it become rated follow-ons.
- **A design choice**: the fix replaces an approach the user chose, not just how that approach is implemented. Examples are merging services, swapping a library or storage engine, and redrawing module boundaries. Look for the choice wherever it is recorded: the plan or PRD behind the code, the PR/MR description, docs or ADRs, comments, scope lines in the target. This is an intent question even when every capability is kept, because the user already weighed it.
- **A migration cost**: the fix's cost lands outside the change itself. Examples:
  - existing data, or an on-disk or wire format other readers use
  - a public API, signature or CLI change with callers outside the target
  - a schema migration
  - renamed config or env keys
  - persisted state or cache formats
  - deploy ordering, or coordination with other services or repos

  This is an intent question, and it states the migration.
- **A tradeoff only the user can weigh**: cost vs latency, memory vs speed. This is an intent question.

When unsure which class a fix falls in, ask. Review fixes may be applied unattended: a needless question costs the user one reply, while a wrongly applied redesign costs a revert.

Per intent question, state what is at stake, its consumers today, what keeping it costs (the spec or code it carries, and the earlier rounds that patched it), and any migration (what moves, and who must change), so the user can weigh it. Report intent questions unrated, in their own section, so a "fix all" reply never applies one.

```
## Intent questions
- ralph/PRD.md:30 — keep <capability>? Consumers: <…>. Cost: <spec or code it carries, rounds that patched it>.
- src/store.py:12 — switch <chosen approach> to <alternative>? Consumers: <…>. Cost: <…>. Migration: <what moves, who must change>.
```
