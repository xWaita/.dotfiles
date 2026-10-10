# Rating findings

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

Rate every finding on two axes, then read its severity off the matrix. **Impact** is what one encounter costs; **exposure** is how much meets it. An unrecoverable consequence on a rarely-reached path and a moderate one on the hot path can land at the same severity.

**Impact** — the cost of a single encounter. The top level is split off by recoverability, which is why its row does not fall with exposure.

- *unrecoverable* — data loss or corruption, a security hole. Nothing can be repaired afterwards, so a rare path is only a delay.
- *severe* — recoverable but system-wide: an outage, a deadlock or unbounded resource growth, a severe performance regression.
- *moderate* — a wrong result, an unhandled failure, a shape where one foreseeable change edits many modules and the alternative edits one, or a construct whose removal deletes substantially more spec or code than it adds or that earlier rounds patched repeatedly.
- *minor* — nothing breaks; a simpler or cheaper alternative exists.

**Exposure** — how much meets it, read per finding kind. Judge it from the specified flow or the code, not from guesses about traffic.

- defect (hole, bug, false premise) — the share of normal operation that reaches the path.
- structure (smell, refactor, over-engineering) — how much code sits on the shape, and how likely the requirement change that punishes it actually arrives.
- plan mechanics — how likely the implementing agent guesses wrong. A spec item no task implements is *high*: a certainty, not a risk.

**Severity** — derived, so two reviewers rating the same finding land in the same place.

| impact ↓ / exposure → | high     | medium   | low      |
| --------------------- | -------- | -------- | -------- |
| *unrecoverable*       | Critical | Critical | Critical |
| *severe*              | Critical | High     | Medium   |
| *moderate*            | High     | Medium   | Low      |
| *minor*               | Medium   | Low      | Low      |
