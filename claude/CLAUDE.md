# Python guidelines

## General

- Don't keep backwards compatibility for changes unless requested.
- Always import at top level.

## Follow Google-style docstsrings

- Every public function, class, and module gets at least a one-line docstring. Add more only when there's something non-obvious to say (contract, gotcha, rationale, tuning range, methodology), but always keep it brief. No docstrings that simply restate the class/module definition or the function implementation.
- If `Attributes` are obvious we do not need to document. If there are non-obvious field semantics, document *all* fields but keep them brief. No Args/Returns that paraphrase the signature.

## Comments

- No comments unless explaining an obscure choice. Don't remove existing comments unless stale.
