# Rust Async & Concurrency

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

Read when the crate uses tokio/async-std, threads, or locks. tokio is assumed; the rules transfer.

## Runtime

- Never call `Runtime::block_on`, `Handle::block_on`, or `futures::executor::block_on` from inside a runtime thread — it deadlocks the worker. Use `.await`, or `tokio::task::block_in_place` as a last resort on the multi-thread runtime.
- Blocking work — `std::fs`, `std::net`, `std::thread::sleep`, CPU loops over a few hundred microseconds — goes through `tokio::task::spawn_blocking`, `tokio::fs`, or rayon. A blocked worker stalls every task on it.
- Do not spawn a task per tiny operation; spawn per unit of concurrency (connection, job). Spawned futures must be `Send + 'static`; `tokio::task::LocalSet` for `!Send` work.

## Locks

- `std::sync::Mutex`/`RwLock` by default, also inside async code — the critical section is short and never awaits, and std locks are cheaper.
- `tokio::sync::Mutex` only when a guard must be held across an `.await` (e.g. a connection that is used sequentially by many tasks). Prefer redesigning so it does not: take what you need out of the lock, drop the guard, then await.
- Never hold a std guard across `.await`: the future is `!Send`, and a worker that parks while holding the lock deadlocks the runtime. Clippy `await_holding_lock` catches it.
- `RwLock` only when reads are measured to dominate; writer starvation and larger guards make it slower than `Mutex` for mixed loads.
- Handle poisoning one way per crate: `.lock().unwrap_or_else(PoisonError::into_inner)` when the data cannot be corrupted by a panic mid-critical-section, otherwise propagate.
- Prefer a single owner task plus channels over `Arc<Mutex<State>>` shared by many tasks: no lock ordering, no poisoning, natural backpressure.

## Structured concurrency

- `JoinSet` over loose `tokio::spawn` handles: every task is joined, errors surface, and dropping the set aborts stragglers.
- `JoinError` means panic or cancellation; propagate it, do not `unwrap` it.
- Cancellation: `tokio_util::sync::CancellationToken` passed down, checked with `select!` or `cancelled()`; shutdown drains in-flight work then drops the token.
- Every network operation is wrapped in `tokio::time::timeout`; a missing timeout is a hang waiting to happen.
- Graceful shutdown order: stop accepting, cancel token, join with a deadline, then exit.

## Cancel safety

- `tokio::select!` drops every losing future. A future that has consumed input or made partial progress loses it unless the operation is cancel-safe.
- Cancel-safe: `mpsc::Receiver::recv`, `TcpListener::accept`, `AsyncReadExt::read`, `tokio::time::sleep`, `Notify::notified`. Not cancel-safe: `AsyncReadExt::read_exact`, `AsyncBufReadExt::read_line`, `AsyncWriteExt::write_all`, most framed `.next()` implementations that buffer. Check the method's "Cancel safety" doc section when unsure.
- Around a non-cancel-safe op inside `select!`: spawn it and select on the `JoinHandle`, or keep the partial state in a struct outside the future.
- `select!` in a loop with a `biased;` clause when one branch (shutdown) must win ties.

## Channels

- `mpsc::channel(n)` bounded by default; `unbounded_channel` only for control messages with a known small volume.
- `oneshot` for request/response; `watch` for latest-value config; `broadcast` for fan-out with lagging-receiver semantics you have read and accepted.
- Close the sender to end the stream; receivers see `None`. Do not send a sentinel.
- Backpressure is the design: when `send().await` blocks, the producer slows. Do not "fix" it with a bigger buffer.

## Traits & futures

- `async fn` in traits is native (1.75+). For a trait that must be object-safe (`dyn`), either `#[trait_variant::make(Send)]`, or return `Pin<Box<dyn Future<Output = T> + Send + '_>>` — `async_trait` only when that boilerplate is measured as unacceptable.
- `Send` errors from a spawned future almost always mean a `!Send` value (guard, `Rc`, `RefCell`, raw pointer) lives across an `.await`; scope it into a block that ends before the await.
- Streams: `futures::Stream` + `StreamExt`; `tokio_stream::wrappers` to adapt channels; `try_for_each_concurrent`/`buffer_unordered(n)` for bounded parallel IO, never an unbounded `join_all` over user-sized input.

## Threads (no runtime)

- `std::thread::scope` for fork-join over borrowed data; no `Arc` needed.
- rayon `par_iter` for data parallelism; do not hand-roll a thread pool.
- Atomics: `Ordering::SeqCst` unless a comment justifies `Acquire`/`Release`; `Relaxed` only for counters nobody synchronizes on.
- `parking_lot` locks only when contention is measured; std locks are adequate and need no dependency.

Async tests: see the `testing` skill's `references/rust.md`.
