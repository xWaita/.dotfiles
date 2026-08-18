# Global guidelines

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

## Mandatory Skill Activation Sequence

Step 1 - EVALUATE (first thing in your response):
For each skill in <available_skills>, state: [skill-name] - YES/NO - [reason]
There is no MAYBE. If the task might reach the skill — at any later step, for any part of the work — that is a YES. Reserve NO for skills the task cannot reach at all.

Step 2 - ACTIVATE (immediately after Step 1, before any other tool call):
IF any skill is YES → Use the Skill(skill-name) tool for EVERY one of them NOW, in this same response.
IF none → State "No skills needed" and proceed.

Never defer an activation to the step that needs it. Nothing fires at that step, so the skill is simply forgotten; loading it up front costs one tool call and it is there when you arrive.

CRITICAL: You MUST call Skill() in Step 2. Do NOT skip to implementation.
The evaluation (Step 1) is WORTHLESS unless you ACTIVATE (Step 2) the skills.

## Documentation

- Optional documentation — comments, docstring bodies, prose about the code — exists only where it improves a future reader's understanding: a contract, gotcha, rationale, tuning range, or methodology the code itself cannot show. Never restate the code, and state what does earn its place as briefly as it can be stated.
- Generic documentation — commit messages, PR descriptions, summaries — is very concise: what changed, plus the why when it isn't evident from the change.
- Don't remove an existing comment unless it is stale.

## Code

- Don't keep backwards compatibility for changes unless requested.
- Always import at top level.

## Python

- Inline a single-use assignment into its following `if` test with the walrus operator (`:=`) when it fits on one line.
- For an existence or validity check, add a predicate method to the type that owns the data rather than wrapping a getter in `try/except`.

### Google-style docstrings

- Every public function, class, and module gets a one-line docstring. Beyond that line, write only the non-obvious; never restate the definition or the implementation.
- Skip `Attributes` when they are obvious. When field semantics are non-obvious, document all fields, briefly. No Args/Returns that paraphrase the signature.
