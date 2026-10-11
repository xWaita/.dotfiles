---
name: perf-review
description: Review a plan or code for efficiency — compute (complexity, repeated work, vectorization, contention, parallelism), memory (materialization, copies, peak footprint, unbounded growth) and storage/I-O (formats, compression codecs, row-group/batch/file sizing, layout, round trips) — judged against the workload's scale and cost, including the library defaults nobody chose. Targets plan files or a branch, PR/MR, paths or commit range. Reports quantified findings rated by severity and edits nothing unless given --fix. Manual only; run it with /perf-review, optionally naming the target.
argument-hint: "[--fix] [plan files | branch | PR/MR number | paths | commit range]"
disable-model-invocation: true
---

# Perf Review

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

Arguments: $ARGUMENTS

The efficiency lens: time, memory, storage and money. Correctness belongs to `/ai-review` and `/code-review`, and design belongs to `/refactor-review`. Report those only when they fall out of a perf finding. Efficiency choices are cheapest to change in a plan, before any data exists in the chosen shape. Changing them in code is cheaper than after the data accumulates.

## Target

Resolve the target as `~/.claude/skills/refactor-review/SKILL.md` § Target does. Read what the target plugs into, and its recorded design intent, as that skill's "Read wider than the target" does: a cost is often set by a caller's loop or a reader's access pattern, not by the code that pays it. For a language's idioms, also invoke the matching language skill (`python`, `rust`).

## Establish the workload first

Every finding is judged against a workload, so pin these down before hunting:
- data volume and growth
- the hot paths and how often they run
- read/write ratio and access pattern: full scan vs point lookup, which columns or fields are read
- latency or throughput targets, and the memory ceiling
- retention, and where the bytes live and what they cost per unit

Take these from the plan or code, or infer them from evident scale (a catalog in object storage, a per-request handler, a nightly batch). When the right choice turns on a figure the target does not give, ask for that figure as an intent question; never guess it.

## Inventory every decision, including the unstated ones

Most efficiency defects are not written anywhere. They are library defaults nobody chose. Every omitted parameter on a serialization, storage, I/O, allocation or concurrency call is a decision. Look up its actual default in the installed library version (its source or its docs, never memory) and judge it against the workload. Read `references/checklist.md` while building the inventory; it lists the knobs per domain.

## Hunt

- **Compute**: algorithmic complexity on hot paths; repeated work (recomputation, loop-invariant work inside a loop, N+1 queries or calls); interpreter-level loops where vectorized, columnar or native operations do the job; parse and serialization overhead on hot paths; lock contention and serialized critical sections; under- or over-parallelism for the work's shape (CPU-bound vs I/O-bound); blocking I/O on async paths.
- **Memory**: materializing a whole dataset where streaming or chunking works; peak footprint vs steady state; copies and conversions between representations; data structure choice, layout and locality; per-item object overhead at scale; unbounded caches, buffers, queues or accumulators.
- **Storage and I/O**: format; compression codec and level; chunk granularity (row group, file, batch, page, multipart part; the small-files problem); layout for the read pattern (partitioning, sort order, statistics, dictionary encoding); round trips and batching; connection pooling; caching; storage class and lifecycle.

Only the stated or evident workload counts, never a hypothetical one. Prefer changing a parameter over adding a mechanism, and leave cold paths alone. Classify each candidate per `~/.claude/skills/common/intent-questions.md`. Format, codec and layout changes to data that already exists usually carry a migration cost, and so do path or extension changes.

## Quantify, rate and verify

- Every finding carries an estimate with the assumption it rests on: complexity × n, ratio × volume → bytes or $/yr, latency, or peak memory. Drop a finding you cannot estimate.
- On a code target, measure when the claim is non-obvious or a benchmark or test harness exists: a micro-benchmark, a profile, a peak-memory run. Reasoned compute claims are often wrong.
- Rate per `~/.claude/skills/common/rating.md`, where efficiency exposure is the share of data volume or hot-path work that passes through the choice.
- Check each finding against the code or the library source, and drop what you cannot point at.

## Report

Two sections: **Findings** ordered by severity, ties broken by impact, then **Intent questions** per `~/.claude/skills/common/intent-questions.md`. Per finding, give:
- the severity and the two ratings behind it
- the `file:line`, naming the call even when the parameter is omitted
- the current choice, explicit or defaulted
- the alternative
- the estimate

Say so plainly when a section is empty.

```
## Findings
HIGH      impact moderate · exposure high
  src/catalog.py:41 — Parquet written with the default codec (snappy). zstd. ~1.5–2× smaller on this column mix → ~X TB less, ~$Y/yr at the stated volume.
```

Then edit nothing and wait for the user to name which findings to apply.

### With `--fix`

Instead of waiting, apply every finding rated Medium or above and every Low that is an easy win (small, local, adding no new surface). Skip other Lows and the intent questions. Run the formatter and tests when the target has them, and re-measure what you measured before. Then report as above, marking each finding applied or not, with the measured or estimated delta. Leave the changes uncommitted, because the caller owns the commit. On a plan target, the fixes are edits to the plan files under the `ai-plan` conventions: a fix rewrites the text it replaces rather than adding beside it, and pins the chosen value so the implementing agent does not fall back on a default.
