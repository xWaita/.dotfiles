---
name: rust
description: Idiomatic, safe, performant Rust on the current edition — ownership and API shape, error handling, unsafe, async/tokio, performance, Cargo/clippy setup, edition-2024 gotchas. Trigger on any edit to `.rs`, `Cargo.toml`, or `Cargo.lock`, on "rust", "cargo", "clippy", "borrow checker", "lifetime", "tokio", "unsafe", "crate", "trait", and when reviewing, profiling, or benchmarking Rust code.
---

# Rust

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

Target the current stable edition (2024) unless `Cargo.toml` pins another. References, read on demand:

- `references/performance.md` — before optimizing, or when the user mentions perf, hot path, allocation, or benchmarks.
- `references/async.md` — when the crate depends on tokio/async-std or the code contains `async`, threads, or locks.
- `references/toolchain.md` — when creating a crate, editing `Cargo.toml`, choosing dependencies, or fixing clippy.

## Ownership

- Never `.clone()` to silence the borrow checker. Restructure: borrow for a shorter scope, split the struct so disjoint fields borrow independently, take `&mut` through a method, or move ownership. Clone only when the copy is semantically required or measured as cheap.
- Return `impl Iterator<Item = T> + '_` instead of collecting into a `Vec` the caller will iterate again.

## Types & API shape

- Newtype ids and units (`struct UserId(u64)`, `struct Meters(f64)`) so the compiler catches swapped arguments.
- Make illegal states unrepresentable: an enum instead of two `Option`s that must agree, an enum instead of a `bool` parameter, `NonZeroU32` when zero is invalid.
- `#[must_use]` on builders, constructors, and pure functions whose result is the whole point.
- `#[non_exhaustive]` on public enums and structs that will gain variants or fields.
- A derive on a public type is a semver promise — skip traits future fields could not satisfy; `PartialOrd`/`Ord` only when there is one natural order.
- `as` only for lossless widening. Narrowing goes through `TryFrom`; arithmetic that can overflow uses `checked_`/`saturating_`/`wrapping_` explicitly, because debug panics and release wraps.
- `pub` fields for plain data records; `fn field(&self)` plus `fn set_field(&mut self)` only where an invariant must hold.

## Errors & panics

- Libraries: one `thiserror` enum per module or crate, `#[from]`/`#[source]` for the chain, `#[non_exhaustive]`. Binaries: `anyhow`, `fn main() -> anyhow::Result<()>`, `.context("what was being attempted")` at every `?` that crosses a meaningful boundary.
- `unwrap`/`expect` only when infallible by construction. Write `expect("<the invariant>")` as the assumption that holds, e.g. `expect("regex is a valid literal")`, not as a failure description.
- Document `# Errors` and `# Panics` on any public fn that can do either.

## Unsafe

- Crates without unsafe get `#![forbid(unsafe_code)]`. Crates with it run `cargo +nightly miri test`.

## Layout & documentation

- Binaries: logic in `lib.rs`, `main.rs` only parses args and calls it, so tests reach everything.
- Modules: `foo.rs` alongside `foo/` for children, not `foo/mod.rs`.
- `pub(crate)` by default; a `pub` item is an API commitment. Re-export the public surface from `lib.rs`.
- `//!` crate-level doc with the one-paragraph purpose; `///` on every public item, linking types with intra-doc links (`` [`Type`] ``). Libraries set `#![warn(missing_docs)]`.
- Doc examples on public entry points and core types, not every fn.
- Logging via `tracing` with structured fields, never `println!`/`eprintln!` in libraries.

## Workflow

Before returning code:

```sh
cargo fmt
cargo clippy --all-targets --all-features -- -D warnings
cargo test            # or cargo nextest run
cargo doc --no-deps   # libraries: doctests and intra-doc links
```

- Fix lints instead of allowing them. When an exception is right, `#[expect(lint, reason = "...")]` — it errors when the lint stops firing, so it cannot go stale. `#[allow]` only in generated or macro-produced code.
- Tests follow the `testing` skill, which links its own Rust conventions file (`rust.md`).
