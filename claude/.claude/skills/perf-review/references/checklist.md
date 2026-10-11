# Efficiency knobs per domain

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

Read while building the inventory. Each line is a decision to find in the target, explicit or defaulted, and judge against the workload. No line is a verdict. Look up the actual default in the installed version before judging it.

## In-process compute

- Hot loops: per-item work in the interpreter where a vectorized, columnar or native operation exists; per-item calls into a slower layer (an FFI hop, a query, a lock).
- Repeated work: the same parse, regex compile, lookup, connection or client built per item or per call instead of once.
- Complexity: a linear membership test inside a loop, a sort repeated per item, quadratic string or list building.
- Parallelism: CPU-bound work on threads under a global interpreter lock; I/O-bound work on too few workers; a pool sized without reference to cores or downstream limits; the oversubscription that nested pools create.
- Async: blocking calls on the event loop; awaiting sequentially what could be gathered.

## Memory

- Whole-file or whole-table reads where an iterator, batch reader or chunked scan works.
- Representation hops: dataframe ↔ arrow ↔ python objects, bytes ↔ str, a copy per transform stage.
- Columns or fields loaded but never used, where the reader supports projection.
- Per-object overhead at scale: a dict or object per row where a columnar or struct-of-arrays layout fits.
- Growth with no bound: caches without eviction, accumulators across a stream, queues without backpressure.

## Columnar files (Parquet and similar)

- Compression codec and level: the default often trades size for speed. Judge it against storage cost and read frequency.
- Row group size: too small inflates metadata and per-group overhead and defeats scans; too large defeats parallelism and raises writer memory.
- File size: many small files cost per-request and per-open overhead on object storage.
- Sort order and statistics, so filters prune row groups; dictionary encoding for low-cardinality columns; types (a string where an int, a timestamp or a categorical fits).
- Partitioning that matches the filter pattern, not so fine it produces small files.

## Raw and document serialization

- Text formats (JSON, CSV) stored uncompressed; a compressed or binary format where only machines read them.
- Codec choice for written blobs (gzip vs zstd and level); whether readers can stream-decompress.
- Per-record files where a batched or line-delimited container fits.

## Object storage

- Request count: per-object GETs/PUTs at small sizes, LIST over large prefixes, missing multipart for large objects.
- Storage class and lifecycle rules for data read rarely after write; retention of intermediates.
- Egress: data moved across regions or out of the cloud that could be processed in place.

## Databases

- N+1 queries; row-at-a-time inserts where a bulk or batched path exists.
- Missing indexes on filter and join keys, and indexes nobody reads that every write pays for.
- Fetching whole rows or tables where a projection or an aggregate in the query would do.
- Connection pooling; transaction scope around batch writes.

## Network and RPC

- Chatty protocols: one call per item where a batch endpoint exists.
- Client reuse, keep-alive, pooling; timeouts and retry backoff tuned to the dependency.
- Payload encoding and compression for large or frequent payloads.
