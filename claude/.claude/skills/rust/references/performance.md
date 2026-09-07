# Rust Performance

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

Read before optimizing. Every rule below is a default; a profile overrides it.

## Measure

- Benchmarks: `divan` (simplest) or `criterion` (statistics, history) under `benches/`, run with `cargo bench`. A one-off `Instant::now()` timing in a `--release` build is fine for a first signal, never for a conclusion.
- Profiles: `cargo flamegraph` (needs `perf`/`dtrace`), `samply`, or `perf record` on a `--release` build with `debug = 1` so frames have symbols. Debug builds are overflow-checked and 10–100× slower, so their profile is not representative.
- Codegen: `cargo asm` / `cargo show-asm` to confirm a hot loop vectorized or a bounds check disappeared.
- Allocation counts: `dhat` or `heaptrack`; a surprising allocation count is the most common finding.

## Allocation

- Build strings with `write!(buf, ...)` (`std::fmt::Write`) into one `String`, not `format!` per piece and `+`.
- Reuse buffers across iterations: `buf.clear()` keeps capacity. Hoist the buffer out of the loop, or pass `&mut Vec` into the fn that fills it.
- Immutable, long-lived data: `Box<[T]>`, `Box<str>`, `Arc<str>`, `Arc<[T]>` — one word smaller than `Vec`/`String` and shareable without copying.
- `SmallVec`, `ArrayVec`, `Bytes`, arena allocators: only after a profile shows the allocation; each has a cost when the guess is wrong.

## Iteration

- `chunks_exact`/`windows` over manual index math: the `_exact` variants let the compiler drop bounds checks and vectorize.
- `sort_unstable`, `sort_unstable_by_key`, `select_nth_unstable` unless equal elements must keep order. `sort_by_cached_key` when the key is expensive.

## Layout & types

- `#[inline]` only on tiny functions called across crate boundaries in a hot path — generic functions inline already, and LTO handles the rest. `#[inline(always)]` needs a benchmark that proves it. `#[cold]` on error-constructing paths.
- Prefer `u32`/`usize` indexes over pointers or `Rc` for graph-like data (arena + index).

## Hashing

- `std::collections::HashMap` uses SipHash: DoS-resistant, slow for small keys. `rustc_hash::FxHashMap` or `ahash` when the keys are not attacker-controlled; `FxHashMap` for integer keys.

## IO

- Wrap files and sockets in `BufReader`/`BufWriter`; unbuffered `read`/`write` calls are one syscall each.
- Lock `stdout` once (`let mut out = std::io::stdout().lock();`) and `writeln!` to it; `println!` locks per call.

## Build profiles

```toml
[profile.release]
lto = "fat"
codegen-units = 1
panic = "abort"      # omit when the binary must catch_unwind or is a library used by one that does
debug = 1            # symbols for profiling; strip before shipping if size matters

[profile.dev.package."*"]
opt-level = 3        # optimized dependencies keep debug builds usable
```

- `RUSTFLAGS="-C target-cpu=native"` only for binaries that run where they were built; it breaks portability.
- `opt-level = "s"`/`"z"` and `strip = true` for size-constrained targets.
- `cargo build --timings` when compile time is the problem; the fix is usually fewer generic instantiations or fewer features enabled on heavy deps.
