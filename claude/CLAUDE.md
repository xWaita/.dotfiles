# Global guidelines

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

## Repository layout

- `~/code/{repo}` — repositories we work on.
- `~/oss/{repo}` — open-source repositories cloned for reading, not for changes we push.
- `~/worktrees/{repo}/{branch}` — worktrees, for working on several branches at once.

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

- Optional documentation — comments, docstring bodies, prose about code — earns its place only by stopping a future editor from breaking something: a contract, invariant, gotcha, tuning range, or methodology. Judge that from the editor, not from yourself fresh out of the investigation that prompted the code. Never restate the code or the reasoning that produced it.
- At most 3 lines beyond the one-line docstring, and 3 per comment, each stated as tersely as the fact allows. Over budget means cut, not relocate. Document-scale material such as methodology sits at module or constant level, which the budget does not cap.
- State a fact once, at the mechanism it constrains: the same rationale at the constant, the function and the call site is three copies to keep in sync.
- Generic documentation — commit messages, PR descriptions, summaries — is very concise: what changed, plus the why when it isn't evident from the change. The incident and the alternatives rejected belong here if anywhere.
- Don't remove an existing comment unless it is stale.

## Code

- Don't keep backwards compatibility for changes unless requested.
- Always import at top level.

## Python

- Inline a single-use assignment into its following `if` test with the walrus operator (`:=`) when it fits on one line.
- For an existence or validity check, add a predicate method to the type that owns the data rather than wrapping a getter in `try/except`.

### Google-style docstrings

- Every public function, class, and module gets a one-line docstring.
- Skip `Attributes` when they are obvious. When field semantics are non-obvious, document all fields, briefly. No Args/Returns that paraphrase the signature.

