# Applying review findings

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

The report is final: do not add, drop, re-rate, or reword any finding from here on. Apply the findings to the plan files. Invoke the `ai-plan` skill and follow its conventions.

For each finding:

- **Critical, High, Medium:** resolve the finding with the best design for the plan as a whole, judged by the `ai-plan` design philosophy — the simplest design serving today's real requirements. The finding's alternative is one candidate, not the answer. Restructure or rewrite the affected section when that yields a better design than patching the flawed text; a fix that removes surface beats one that adds it.
- **Low:** apply it only when it is an easy win — a correction, a deletion, or a re-pointed reference that adds no new spec. A fix whose net effect removes spec is an easy win however many sections it touches: easy is what the plan gains, not the size of the edit. Otherwise mark it `declined` with the reason "not an easy win".
- When the chosen fix makes other plan text redundant or wrong, update that text in the same edit, so the plan stays one consistent design. A fix that settles an open question or replaces a design rewrites the text that stated it — never a new bullet beside it, which leaves the old claim live.
- If a fix would reverse or contradict an applied F# in the ledger or another fix in this batch — including a finding that calls an earlier fix over-engineered — do not apply it. Mark it `conflict` and name the F#; the user decides.
- A fix that would remove or narrow a capability — something the system can do for its user, not merely how the spec delivers it — is not applied, whatever the finding proposed: mark it `conflict` naming the capability, since only the user knows whether it is a requirement.
- A fix that needs a file other than the plan files is `declined` with that reason.

Do not commit. Return every finding from the report, with its reported ratings unchanged, plus its status and, when applied, one sentence stating what the plan now says.
