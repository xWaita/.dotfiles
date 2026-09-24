---
name: python
description: Opinionated idiomatic Python (3.12+) — data access, dataclasses and typing syntax, exceptions, Google-style docstrings, logging, module layout, uv/ruff workflow. Trigger on any edit to `.py`, `pyproject.toml`, or `uv.lock`, on "python", "uv", "ruff", "pyproject", "dataclass", "pydantic", "type hint", "docstring", "mypy", "pyright", and when reviewing Python code.
---

# Python

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

Target Python 3.12+ unless `pyproject.toml` pins lower.

## Control flow & data access

- Inline a single-use assignment into its following `if` test with the walrus operator (`:=`) when it fits on one line.
- For an existence or validity check, add a predicate method to the type that owns the data rather than wrapping a getter in `try/except`.
- Fail loud: `d[k]` and `obj.attr` when the key must exist. `.get(k, default)` and `getattr(x, "a", None)` only when absence is a real case the caller handles — a default that hides a missing key turns a bug into wrong data.
- No defensive `isinstance` or `None` checks on values the annotations already constrain; trust the type hints.

## Types

- PEP 695 syntax: `type Alias = ...`, `def f[T](x: T)`, `class Box[T]`. `Self` for fluent returns, `typing.override` on overrides.
- Structured data is `@dataclass(slots=True)`; add `frozen=True` when value-like and `kw_only=True` past ~3 fields. Never a bare `dict` crossing a function boundary.
- Configuration is a pydantic model; `dataclass` is for records the program computes. Parsed settings, request/response bodies and hand-written in-repo spec tables are all configuration — staying internal is not an exception. Freeze with `ConfigDict(frozen=True)` unless something mutates it.
- A dict literal of settings is configuration with the model left out: keep the dict as a registry keyed by name, make each value a model.
- `StrEnum`/`IntEnum` over string constants; an enum over a `bool` parameter.

## Errors

- `except` has three legitimate purposes: recover, translate to a domain error at a boundary (`raise DomainError(...) from e`), or add context. Never log-and-reraise, never catch to return `None`; let it propagate.
- One base exception per package, subclasses only for cases callers branch on.

## Docstrings (Google style)

- Every public function, class, and module gets a one-line docstring.
- Skip `Attributes` when they are obvious. When field semantics are non-obvious, document all fields, briefly. No Args/Returns that paraphrase the signature.

## Logging

- `log = logging.getLogger(__name__)` at module level; lazy `%s` arguments, not f-strings; libraries never configure handlers.

## Layout

- No `utils.py`, `helpers.py`, or `common.py` grab-bags — name modules by the domain concept they hold.
- Module-private names take a leading underscore. `__all__` only in a module that is a curated re-export surface.
- `import datetime as dt` and qualify (`dt.datetime`, `dt.timedelta`, `dt.UTC`); never `from datetime import ...` — the bare name `datetime` is both the module and its class, so a qualified reference says which.
- Logic lives in importable modules; `__main__.py` or the entry point only parses args and calls it, so tests reach everything.

## Workflow

Before returning code:

```sh
uvx ruff format
uvx ruff check --fix
uv run pytest
```

- Fix lints instead of `# noqa`. A justified exception carries the reason on the same line.
- Tests follow the `testing` skill, which links its own Python conventions file (`python.md`).
