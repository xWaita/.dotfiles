# Git

- Never put "Co-Authored-By" lines in commit messages.

# Python guidelines

## General

- Don't keep backwards compatibility for changes unless requested.
- Always import at top level.

## Follow Google-style docstsrings

- Every public function, class, and module gets at least a one-line docstring. Add more only when there's something non-obvious to say (contract, gotcha, rationale, tuning range, methodology), but always keep it brief. No docstrings that simply restate the class/module definition or the function implementation.
- If `Attributes` are obvious we do not need to document. If there are non-obvious field semantics, document *all* fields but keep them brief. No Args/Returns that paraphrase the signature.

## Comments

- No comments unless explaining an obscure choice. Don't remove existing comments unless stale.


# AI planning

## PRD.md files

- Keep concise. It will be interpreted by an AI agent for planning and for generating PROGRESS.md files.
- Describe the current state only; do not reference what was previously planned.

## PROGRESS.md files

- When creating todo checklists for project plans, structure in terms of phases of features that are optimised for AI task-driven development, where each feature represents a working commit including any required tests.
- Onclude steps for setting up infra for related tasks, i.e. test helpers for tasks that implement similar API methods.
- Merge trivial tasks that don't require much context and can be verified together (e.g. boilerplate files, struct definitions with the code that uses them, tightly coupled modules, similar test cases into one parametrized task).
