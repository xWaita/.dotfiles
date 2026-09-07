# Rust Toolchain, Cargo & Edition Notes

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

Read when creating a crate, editing `Cargo.toml`, choosing dependencies, or fixing clippy.

## Cargo.toml

```toml
[package]
name = "example"
version = "0.1.0"
edition = "2024"
rust-version = "1.85"       # MSRV; CI builds on it

[lints.rust]
unsafe_op_in_unsafe_fn = "warn"
missing_docs = "warn"        # libraries only

[lints.clippy]
pedantic = { level = "warn", priority = -1 }
module_name_repetitions = "allow"
must_use_candidate = "allow"
unwrap_used = "warn"          # libraries; binaries usually leave it off
```

- `[lints]` in `Cargo.toml` replaces `#![warn(...)]` at the crate root; in a workspace put them under `[workspace.lints]` and set `lints.workspace = true` in each member.
- Workspaces: `[workspace.dependencies]` pins each version once; members use `dep.workspace = true`. `resolver = "3"` is the edition-2024 default.
- Features are additive and named after what they enable (`serde`, `tokio`), never `no-std` (use `std` default feature instead). An optional dependency is exposed as `dep:name` so its name is not an implicit feature.
- Keep the dependency count low: check `cargo tree -d` for duplicates and `cargo tree -e features` before adding a heavy crate for one function.
- `src/bin/*.rs` for several binaries; `[[bin]] required-features` when one needs a feature.
- `build.rs` only for codegen or linking; never for network access.

## Clippy policy

- `cargo clippy --all-targets --all-features -- -D warnings` is the bar; `pedantic` on, with a short allow list in `[lints]` for the noisy ones the project rejects.
- High-value lints beyond default: `await_holding_lock`, `large_enum_variant`, `result_large_err`, `needless_pass_by_value`, `redundant_clone`, `missing_errors_doc`, `missing_panics_doc`, `cast_possible_truncation`, `cast_sign_loss`, `undocumented_unsafe_blocks`.

## Std over crates

Reach for std first; these used to need a crate:

| Need | Std (version) |
|---|---|
| Lazy global | `OnceLock`, `LazyLock` (1.80) — not `lazy_static`, `once_cell` |
| Channels | `std::sync::mpsc` — `crossbeam-channel` only for `select!` or a cloneable receiver |
| Scoped threads | `std::thread::scope` (1.63) |
| Chained conditions | `if let Some(x) = a && x > 0 { }` let-chains (1.88, edition 2024) |
| Async fn in trait | native (1.75) — not `async_trait` |

## Recommended crates by need

- Serialization: `serde` + `serde_json`/`toml`; `#[serde(deny_unknown_fields)]` on config structs.
- Errors: `thiserror` (library), `anyhow` (binary); `miette` when rich diagnostics are the product.
- Async: `tokio` with explicit features, `tokio-util` (codecs, `CancellationToken`), `futures` for `Stream`.
- Observability: `tracing` + `tracing-subscriber` (`EnvFilter`); `log` only when a dependency forces it, bridged via `tracing-log`.
- CLI: `clap` derive; `--help` text from doc comments.
- Parallel: `rayon`. Bytes: `bytes`. Ordered map: `indexmap`. Time: `jiff` or `time` (`chrono` when the ecosystem demands it).
- Testing: `proptest` (invariants), `insta` (snapshots), `trybuild` (compile-fail), `divan`/`criterion` (benches), `tokio-test`.
- Supply chain: `cargo deny check` (licenses, advisories, duplicates), `cargo audit`; run both in CI.

## Edition 2024 gotchas

- Return-position `impl Trait` captures every in-scope lifetime and type parameter. Narrow with `impl Trait + use<'a>` (or `use<>` for none) when a borrowed `self` must not pin the return to `&self`'s lifetime.
- `unsafe extern "C" { ... }` is required; each item inside is `safe fn` or `unsafe fn`. `#[no_mangle]` and `#[export_name]` become `#[unsafe(no_mangle)]`.
- `unsafe_op_in_unsafe_fn` warns by default: an `unsafe fn` body needs inner `unsafe {}` blocks with their own `// SAFETY:`.
- Temporaries in a block's tail expression drop before the block's locals (was after). Code that relied on a `MutexGuard` temporary living to the end of the enclosing statement may now compile where it previously errored, or drop earlier than intended — bind the guard to a `let` when its lifetime matters.
- `if let` scrutinee temporaries drop before the `else` branch runs; a `RefCell::borrow()` in the scrutinee no longer conflicts with a `borrow_mut` in `else`.
- `gen` is reserved; identifiers named `gen` become `r#gen`.
- The never type `!` falls back to `!` rather than `()` in some generic positions; `unreachable!()` inside closures that return a generic type may need an annotation.
- Macro fragment `expr` now matches `const {}` and `_`; `expr_2021` keeps the old matching.
- `Box<[T]>` implements `IntoIterator` by value; `boxed_slice.into_iter()` yields `T`, not `&T`.
- `cargo fix --edition` handles the mechanical migrations; review the diff, it is conservative.
