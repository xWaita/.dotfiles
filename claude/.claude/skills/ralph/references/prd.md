# PRD conventions

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

What `PRD.md` holds and the design philosophy a plan is judged against. Read when writing, changing or reviewing a PRD.

## PRD.md

- A PRD's normative units are signatures, behaviors, and invariants; budget rationale at one sentence per invariant.
- Separate spec from implementation: the PRD is architecture and spec only. Implementation order and steps go in the block files.
- State the current target only. The PRD holds no history: a changed decision replaces the text it supersedes.
- Spec the target state, not the first slice: the PRD covers every committed feature (see Design philosophy), including those this plan does not build, so the design accommodates them instead of hardening a shape later work must tear up. Mark each deferred item `Deferred:` inline, next to the surface it shapes; spec only what today's design depends on (data shapes, public signatures, invariants, extension points), never its internals. A deferred item is a constraint on this plan's design, never work for it.
- When the design stores, moves or computes over data at scale, state the workload: volume and growth, hot paths, access pattern, retention, latency and memory targets. Pin each efficiency-relevant value the design depends on (format, codec, chunk or batch size, streaming vs loading); an unstated value ships as the library default.
- Name every repository the plan changes, by path, where the PRD first mentions it. The block cut reads the repositories from there.
- Upstream PRDs must not reference downstream/sibling packages whose tech choices are still open. The upstream describes its own public surface generically; the downstream PRD references the upstream.
- Never cite a block name or a task id. Blocks cite PRD sections, never the reverse, so re-cutting or renumbering leaves the PRD untouched.
- Plan directories are ephemeral — never cite one from durable artifacts (skills, package CLAUDE.md, code comments). Durable knowledge a plan produced belongs in those artifacts directly; point at reference implementations in code instead.

## Design philosophy

- Design for the committed target state; add no surface for hypothetical cases. A feature is committed when the user has stated the intent to build it (this request, an existing plan or roadmap, project docs); anything else is hypothetical. Between designs that serve the committed state equally, recommend the simpler.
