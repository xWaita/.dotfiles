# Python guidelines

## General

- Don't keep backwards compatibility for changes unless requested.
- Always import at top level.
- Inline a single-use assignment into its following `if` test with the walrus operator (`:=`) when it fits on one line.

## Follow Google-style docstsrings

- Every public function, class, and module gets at least a one-line docstring. Add more only when there's something non-obvious to say (contract, gotcha, rationale, tuning range, methodology), but always keep it brief. No docstrings that simply restate the class/module definition or the function implementation.
- If `Attributes` are obvious we do not need to document. If there are non-obvious field semantics, document *all* fields but keep them brief. No Args/Returns that paraphrase the signature.

## Comments

- No comments unless explaining an obscure choice. Don't remove existing comments unless stale.

## Mandatory Skill Activation Sequence

Step 1 - EVALUATE (do this in your response):
For each skill in <available_skills>, state: [skill-name] - YES/NO - [reason]

Step 2 - ACTIVATE (do this immediately after Step 1):
IF any skills are YES or MAYBE → Use Skill(skill-name) tool for EACH relevant skill NOW
IF no skills are YES or MAYBE → State "No skills needed" and proceed

CRITICAL: You MUST call Skill() tool in Step 2. Do NOT skip to implementation.
The evaluation (Step 1) is WORTHLESS unless you ACTIVATE (Step 2) the skills.
