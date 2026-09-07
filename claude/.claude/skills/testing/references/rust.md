# Rust Test Conventions

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

- Integration tests in `tests/` exercise the public API only, one file per feature area; a helper shared across them lives in `tests/common/mod.rs`.
- Doctests on public entry points are the third tier: they prove the documented contract compiles and holds. Keep them short; move edge cases to unit tests.
- `unwrap`/`expect` are fine in tests. Return `Result<(), E>` from a test only when `?` makes it clearer; a panic gives the better failure message.
- `#[should_panic(expected = "substring")]` always with `expected`; a bare `should_panic` passes on any panic.
- Invariants: `proptest` with a `proptest!` block and shrinking; round-trip (`parse(format(x)) == x`) and idempotency are the usual targets.
- Snapshots: `insta` (`assert_snapshot!`, `assert_debug_snapshot!`) for large structured output; review with `cargo insta review`, commit `.snap` files.
- Compile-fail for type-level or macro APIs: `trybuild` under `tests/ui/`.
- Async: `#[tokio::test]`, `start_paused = true` whenever timers are involved so tests never sleep on wall time. `tokio::io::duplex` and `tokio_test::io::Builder` script IO without sockets. Assert behaviour under cancellation: drop the future or fire the token mid-operation and check state is consistent.
- Merge near-identical tests into one that loops over `[(input, expected), ...]` with the case in the assert message, or use `rstest` `#[case]` when the project already depends on it.
- `#[ignore = "reason"]` only with the reason; run them in CI with `--include-ignored` where feasible.
- `cargo nextest run` when installed: per-test processes, so a panic or hang isolates; `cargo test` otherwise. Both plus `--doc` for doctests.
