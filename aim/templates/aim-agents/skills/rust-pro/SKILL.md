---
name: rust-pro
description: Covers production Rust on the 2024 edition -- ownership and lifetimes, async with Tokio, the trait and type system, performance work, and safe handling of unsafe and FFI. It leans on current ecosystem crates (axum, tower, sqlx, serde, thiserror) and idiomatic error handling. Use it when building Rust services or libraries, resolving borrow-checker and async design problems, or optimizing systems code without giving up safety.
---

# Modern Rust

Guidance for building correct, fast Rust on the 2024 edition. The throughline is using the compiler to prove properties at build time, then optimizing what is left -- safety and performance are not in tension when the type system carries the weight.

## How to approach a Rust task

1. Pin down the real constraints first: latency and throughput targets, safety requirements, and which runtime (if any) the system can adopt.
2. Decide the concurrency model and the crate ecosystem before writing much code -- async runtime, web framework, data layer.
3. Build with tests and lints wired in from the start.
4. Profile only after it works, then optimize the hot paths the data points to.

This skill suits services, libraries, and systems tooling, and is most valuable for ownership/lifetime puzzles, async architecture, and safety-preserving optimization. It is overkill when you just need a quick dynamic script or only touch basic syntax, and it does not apply where Rust cannot enter the stack.

## Language features worth mastering

The modern, long-stable surface area is large. The pieces that pay off most often:

- Const generics and improved inference for expressing size and shape at the type level.
- Generic associated types (GATs) and richer trait bounds for abstractions that were previously impossible.
- Pattern matching with destructuring and guards as a primary control-flow tool.
- Const evaluation for moving work to compile time.
- Both flavors of macro -- declarative `macro_rules!` and procedural/derive -- for cutting boilerplate.
- The module and visibility system for clean API surfaces.
- `Result`, `Option`, and custom error types as the backbone of error handling.

## Ownership and memory

This is where Rust earns its guarantees, so internalize it:

- Ownership, borrowing, and move semantics -- the model the borrow checker enforces.
- Shared ownership via `Rc`/`Arc`, with `Weak` to break cycles.
- The smart-pointer toolbox: `Box` for heap allocation, `RefCell` for interior mutability, `Mutex`/`RwLock` for shared mutable state across threads.
- Zero-cost abstractions and deliberate memory layout.
- RAII -- tie resource cleanup to scope via `Drop`.
- Phantom types and zero-sized types to encode invariants at no runtime cost.
- Custom allocators and pooling when the default allocator is the bottleneck.

Memory safety comes without a garbage collector; the cost is paid in thinking up front, not in runtime pauses.

## Async and concurrency

For I/O-bound and concurrent work, build on Tokio:

- `async`/`await` over the Tokio runtime as the foundation.
- Streams and async iteration for processing data as it arrives.
- The channel family -- `mpsc`, `broadcast`, `watch` -- chosen by fan-out and ownership needs.
- The web/services stack: axum on tower on hyper.
- `select!` for racing tasks and structured concurrency for managing them.
- Backpressure and flow control so producers cannot overwhelm consumers.
- Async trait objects and dynamic dispatch where monomorphization is not viable.

Keep CPU-bound work off the async executor -- offload it to `spawn_blocking` or a dedicated thread pool so the reactor stays responsive.

## Traits and the type system

Type-level design is how Rust stays both flexible and safe:

- Trait implementations, bounds, and associated types -- including GATs for higher-order abstractions.
- The newtype pattern to navigate the orphan rule and add semantics to existing types.
- Marker traits and phantom types to make illegal states unrepresentable.
- Derive macros, including custom ones, to generate trait impls.
- A deliberate choice between static dispatch (monomorphization, faster, larger binary) and dynamic dispatch (`dyn`, smaller, indirected).

## Performance and systems programming

When speed is the requirement:

- Build on zero-cost abstractions and let the compiler optimize aggressively.
- Use portable SIMD for data-parallel kernels.
- Reach for memory mapping and low-level I/O when buffered I/O is the limit.
- Apply lock-free techniques and atomics where lock contention dominates.
- Design cache-friendly data structures -- layout often beats algorithmic cleverness.
- Profile with `perf`, Valgrind, and `cargo flamegraph` before changing anything.
- For embedded or distribution, tune binary size and cross-compile to the target.

## Web services and data

A typical production service draws from:

- Frameworks: axum (the common default), with warp or actix-web as alternatives.
- HTTP/2 and HTTP/3 via hyper, plus WebSockets for real-time channels.
- Middleware and authentication layered through tower.
- Data access with sqlx (compile-time-checked queries) or diesel.
- serde for serialization, with custom formats when needed.
- async-graphql for GraphQL and tonic for gRPC.

## Error handling

Make failure explicit and informative:

- Define library error types with `thiserror`; use `anyhow` for application-level, context-rich propagation.
- Convert errors across boundaries with `From`, preserving context as they bubble up.
- Lean on `Result`/`Option` combinators rather than manual branching.
- Reserve `panic!` for truly unrecoverable states; degrade gracefully otherwise.
- Emit structured, logged errors and test the failure paths, not just the happy path.

## Testing and quality

- Unit tests in-module with the built-in framework; integration tests under `tests/`.
- Property-based testing via `proptest` or `quickcheck` to probe invariants.
- Mocking with `mockall` where collaborators must be faked.
- Benchmarks with `criterion` for statistically sound measurements.
- Doctests so examples stay correct, and coverage via `tarpaulin`.
- Run it all in CI on every change.

## Unsafe and FFI

When you must drop below safe Rust:

- Wrap every `unsafe` block in a safe abstraction and document the invariants it upholds.
- Bridge to C through FFI; generate bindings with `bindgen` rather than by hand.
- Be precise about pointer arithmetic and raw-pointer handling.
- Keep `unsafe` regions as small and as auditable as possible.

## Tooling

- Cargo workspaces and feature flags to organize multi-crate projects.
- Cross-compilation and target configuration for non-host platforms.
- Clippy (tune the lint set to the project) and rustfmt for consistency.
- The cargo extension family: `audit`, `deny`, `outdated`, `edit`.
- Disciplined dependency and version management; publish with hosted docs.

## Working principles

Lean on the type system for compile-time correctness, and keep safety and speed together rather than trading one away. Handle errors explicitly through `Result`, write thorough tests including property-based ones, follow community idioms, and document the safety reasoning behind any `unsafe`. Optimize against measurements, favor functional patterns where they read well, and track the language and ecosystem as they evolve.

## The kinds of problems this fits

- A high-throughput async web service with rigorous error handling.
- A lock-free concurrent data structure built on atomics.
- Tightening an existing routine for memory use and cache locality.
- A safe wrapper over a C library via FFI.
- A streaming data processor with proper backpressure.
- A plugin system with dynamic loading that stays type-safe.
- A custom allocator for a specialized workload.
- Untangling lifetime errors in dense generic code.
