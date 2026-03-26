# Rust Review Criteria

Comprehensive knowledge base for the rust-review agent. Apply all relevant
criteria when reviewing Rust code.

## Review Philosophy

- **Correctness over cleverness.** Clear, correct code beats clever code.
- **Leverage the type system.** Rust's type system prevents entire classes
  of bugs — prefer compile-time guarantees over runtime checks.
- **Zero-cost abstractions.** Idiomatic Rust uses abstractions that compile
  away. Prefer iterators over manual loops, `?` over manual matching.
- **Constructive feedback.** Frame issues as improvements, not criticisms.

## Error Handling

### Critical Rules

- **Never ignore errors silently.** Every `Result` should be handled with
  `?`, `match`, `map_err`, or an explicit `let _ =` with a comment.
- **Use `?` for propagation.** The `?` operator is idiomatic for error
  propagation in functions returning `Result`.
- **Add context to errors.** Use `map_err`, `with_context` (anyhow), or
  custom error variants (thiserror) to add context.
- **Handle errors once.** Don't log and propagate — do one or the other.

### Error Type Strategy

Choose ONE strategy per crate and use it consistently:

- **`thiserror`** — for libraries. Define structured error enums with
  `#[derive(thiserror::Error)]`.
- **`anyhow`** — for applications. Use `anyhow::Result` with `.context()`.
- **`std::io::Error`** — for I/O-heavy code. Use `.map_err()` for context.
- **`Box<dyn Error>`** — avoid in new code. Use `thiserror` or `anyhow`.

### Patterns

```rust
// GOOD: propagate with context
fn read_config(path: &Path) -> Result<Config> {
    let content = fs::read_to_string(path)
        .with_context(|| format!("failed to read {}", path.display()))?;
    toml::from_str(&content).context("invalid config format")
}

// BAD: unwrap in library code
fn read_config(path: &Path) -> Config {
    let content = fs::read_to_string(path).unwrap();
    toml::from_str(&content).unwrap()
}
```

### Acceptable `let _ =` Patterns

These are NOT bugs — leave them alone:

- Logging write failures (can't log a logging failure)
- Best-effort channel sends (`let _ = tx.send(msg)`)
- Resource cleanup in `Drop` implementations
- `let _ = remove_file(path)` in cleanup/teardown

### `unwrap()` / `expect()` Guidance

- **`?` operator:** The idiomatic default for all production code.
- **Tests and examples:** `unwrap()` is fine — test failures are expected.
- **Static guarantees:** `Regex::new("^[a-z]+$").unwrap()` is fine — the
  pattern is a compile-time constant.
- **Library code:** NEVER use bare `unwrap()`. Use `?`, `unwrap_or`,
  `unwrap_or_else`, or `unwrap_or_default`.
- **Binary entry points:** `expect("reason")` in `main()` is acceptable
  for irrecoverable startup errors.
- **`expect()` over `unwrap()` for intentional panics:** When panicking is
  the correct behavior, prefer `expect("reason")` over `unwrap()` — it
  documents the invariant. The message should explain WHY the value is
  guaranteed to be present, not just WHAT failed.

## Ownership and Borrowing

### Critical Rules

- **Prefer borrowing over cloning.** Clone only when you truly need
  independent ownership.
- **Use `&str` over `String` in function parameters** when the function
  doesn't need ownership.
- **Use `Cow<'_, str>`** when a function sometimes borrows and sometimes
  owns.
- **Avoid `Rc`/`Arc` unless needed.** Reach for them only when ownership
  is genuinely shared.

### Common Anti-Patterns

```rust
// BAD: unnecessary clone
fn process(data: String) { /* only reads data */ }
process(my_string.clone());

// GOOD: borrow instead
fn process(data: &str) { /* only reads data */ }
process(&my_string);

// BAD: unnecessary allocation
fn get_name(&self) -> String { self.name.clone() }

// GOOD: return reference
fn get_name(&self) -> &str { &self.name }
```

### Lifetime Guidelines

- Prefer elided lifetimes when the compiler can infer them.
- Name lifetimes descriptively when multiple are in play:
  `fn parse<'input, 'schema>(...)`
- Avoid `'static` unless genuinely needed (constants, leaked memory,
  thread spawns).

## Concurrency

### Critical Rules

- **Every `unsafe` block needs a `// SAFETY:` comment.**
- **Prefer `tokio::sync::Mutex` in async code** over `std::sync::Mutex`.
  Holding a `std::sync::MutexGuard` across an `.await` can deadlock.
- **Track `JoinHandle`s.** Don't fire-and-forget `tokio::spawn` — store
  the handle and await it or abort it on shutdown.
- **Use `Arc<Mutex<T>>` only when truly shared.** Often a channel or
  `tokio::sync::watch` is clearer.

### Patterns

```rust
// BAD: std Mutex in async
async fn update(&self) {
    let mut data = self.data.lock().unwrap();
    self.fetch().await; // DEADLOCK RISK
    *data = new_value;
}

// GOOD: tokio Mutex in async
async fn update(&self) {
    let mut data = self.data.lock().await;
    *data = self.fetch().await;
}

// BAD: fire-and-forget spawn
tokio::spawn(async { do_work().await });

// GOOD: tracked spawn
let handle = tokio::spawn(async { do_work().await });
// ...later...
handle.await??;
```

### Send + Sync

- Types used across thread boundaries must be `Send`.
- Types shared via `Arc` must be `Send + Sync`.
- If a type contains `Rc`, `Cell`, or raw pointers, it is NOT `Send`/`Sync`
  by default — document this.

## Data Management

### Slice and Collection Safety

- **Never index from external input without bounds checking.** Use `.get()`
  for fallible access.
- **Pre-allocate collections** when the size is known:
  `Vec::with_capacity(n)`, `HashMap::with_capacity(n)`.
- **Bound collection growth** from user input to prevent DoS.

### Resource Cleanup

- Implement `Drop` for types holding external resources.
- Use RAII patterns — acquire in `new()`, release in `drop()`.
- File handles, network connections, temp directories should all have
  deterministic cleanup.

### Zero Values and Default

- Implement `Default` for types with sensible defaults.
- Prefer `Option<T>` over sentinel values.
- Use `#[derive(Default)]` when all fields have Default.

## Trait Design

### Guidelines

- **Keep traits small and focused.** One responsibility per trait.
- **Prefer generics over trait objects** when possible — zero-cost dispatch.
- **Use `impl Trait` in return position** for opaque types.
- **Mark traits `#[non_exhaustive]`** when they may gain methods.

### Object Safety

A trait is object-safe if:

- No `Self: Sized` bound
- No associated constants or types
- No generic methods
- All methods take `&self`, `&mut self`, or `self: Box<Self>`

### Standard Trait Implementations

Implement these when appropriate:

- `Display` — for user-facing output
- `Debug` — for developer output (derive for most types)
- `Clone` — when values should be duplicable
- `PartialEq`/`Eq` — for equality comparison
- `Hash` — when used as map keys
- `From`/`Into` — for type conversions
- `Error` — for error types (with `Display` and `source()`)

## Code Structure

### Early Returns

```rust
// BAD: deep nesting
fn process(input: Option<&str>) -> Result<Output> {
    if let Some(val) = input {
        if !val.is_empty() {
            if val.starts_with("prefix") {
                // actual logic buried 3 levels deep
            }
        }
    }
}

// GOOD: early returns
fn process(input: Option<&str>) -> Result<Output> {
    let val = input.ok_or(Error::MissingInput)?;
    if val.is_empty() { return Err(Error::EmptyInput); }
    if !val.starts_with("prefix") { return Err(Error::BadPrefix); }
    // actual logic at top level
}
```

### Match Patterns

- **Prefer `match` over `if let` chains** when exhaustiveness matters.
- **Use `_` catch-all carefully** — it silently ignores new variants.
- **Prefer `matches!()` for simple boolean checks:**
  `matches!(val, Some(x) if x > 0)`

### If-Let Chains (Rust 2024+)

```rust
// Rust 2024 edition: if-let chains
if let Some(x) = a && let Some(y) = b && x > y {
    process(x, y);
}
```

## API Design

### Builder Pattern

Use builders for types with many optional fields:

```rust
let config = ConfigBuilder::new()
    .timeout(Duration::from_secs(30))
    .retries(3)
    .build()?;
```

### Newtype Pattern

Use newtypes for type-safe wrappers:

```rust
struct UserId(u64);
struct OrderId(u64);
// These are now distinct types — can't accidentally pass OrderId as UserId
```

### From/Into Conversions

```rust
impl From<UserId> for u64 {
    fn from(id: UserId) -> Self { id.0 }
}

// Accept anything convertible
fn process(id: impl Into<UserId>) {
    let id = id.into();
}
```

### #[must_use]

Add `#[must_use]` to:

- Functions returning `Result` (already implicit for `Result`)
- Functions returning new values that would be useless if discarded
- Builder methods that return a modified builder

## Performance

### Allocations

- **Avoid allocating in hot loops.** Pre-allocate buffers and reuse them.
- **Use `&str` / `&[u8]` over `String` / `Vec<u8>`** when ownership is
  not needed.
- **Use `Cow<'_, str>`** when a function sometimes needs to allocate and
  sometimes doesn't.

### Iterators

Iterators are zero-cost abstractions in Rust — prefer them over manual loops:

```rust
// GOOD: iterator chain (zero-cost)
let sum: u64 = items.iter()
    .filter(|x| x.is_valid())
    .map(|x| x.value())
    .sum();

// BAD: manual loop with mutation
let mut sum = 0u64;
for item in &items {
    if item.is_valid() {
        sum += item.value();
    }
}
```

### String Operations

- `format!()` allocates — avoid in hot paths.
- `write!()` to a `String`/buffer avoids repeated allocations.
- `push_str()` is faster than `format!("{}{}", a, b)` for simple concat.
- For building strings in loops: use `String::with_capacity()` + `push_str()`.

### Collect Patterns

```rust
// GOOD: collect with type annotation
let names: Vec<_> = items.iter().map(|x| x.name()).collect();

// GOOD: collect into Result
let results: Result<Vec<_>, _> = items.iter().map(fallible_op).collect();
```

## Module Organization

### Visibility

- Default to private. Only make items `pub` when needed.
- Use `pub(crate)` for crate-internal APIs.
- Use `pub(super)` for parent-module-only visibility.
- Re-export important types at the crate root for ergonomic imports.

### Module Structure

```
src/
├── lib.rs          # Crate root, public API re-exports
├── config.rs       # Configuration types
├── error.rs        # Error types (if using thiserror)
├── models/         # Data models
│   ├── mod.rs
│   └── user.rs
└── services/       # Business logic
    ├── mod.rs
    └── auth.rs
```

### Naming

- Modules: `snake_case`
- Types: `PascalCase`
- Functions/methods: `snake_case`
- Constants: `SCREAMING_SNAKE_CASE`
- Lifetimes: short lowercase (`'a`, `'ctx`)

## Security

### Input Validation

- Validate all external input at system boundaries.
- Use `TryFrom` for validated type conversions.
- Bound collection sizes from untrusted input.

### Unsafe Code

- **Every `unsafe` block MUST have a `// SAFETY:` comment.**
- **Enable `unsafe_op_in_unsafe_fn` lint** — requires explicit `unsafe`
  blocks even inside `unsafe fn`, making safety reasoning more granular.
  Add `#![deny(unsafe_op_in_unsafe_fn)]` at the crate root.
- Minimize the scope of `unsafe` blocks.
- Prefer safe abstractions over raw unsafe code.
- Document all invariants that the caller must maintain.
- **SAFETY comments must be correct, not just present.** Verify that
  the stated invariant actually holds, especially in concurrent contexts.

### SQL

- **Use parameterized queries.** Never concatenate user input into SQL.
- Use `sqlx`, `diesel`, or `sea-orm` — they enforce parameterization.

### Secrets

- Never hardcode secrets, API keys, or credentials.
- Use environment variables or secret management services.
- Never log secrets — implement custom `Debug`/`Display` that redacts.

### Cryptography

- Use `ring`, `rustls`, or `rcgen` — never roll your own.
- Use constant-time comparison for secrets.

### Supply Chain

- **`cargo deny`** — check licenses, advisories, sources, and duplicate
  dependencies. Subsumes `cargo audit` and adds license checking.
- **`cargo audit`** — check RustSec Advisory Database for known vulns.
- **`cargo machete`** — detect unused dependencies (heuristic, fast).

## Testing

### Coverage Expectations

- Unit tests: 70-80% line coverage
- Critical paths: 90%+ coverage
- Error paths: explicitly tested
- Edge cases: nil/empty/boundary values tested

### Test Quality

- Test behavior, not implementation.
- Use `#[test]` for unit tests in `#[cfg(test)]` modules.
- Use integration tests in `tests/` for cross-module behavior.
- Property-based testing with `proptest` or `quickcheck` for parsers and
  serializers.

### Common Test Patterns

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parse_valid_input() {
        let result = parse("valid");
        assert_eq!(result, Ok(Expected { ... }));
    }

    #[test]
    fn parse_empty_input_returns_error() {
        let result = parse("");
        assert!(matches!(result, Err(Error::EmptyInput)));
    }

    #[test]
    #[should_panic(expected = "invariant violated")]
    fn constructor_panics_on_invalid_state() {
        Widget::new(invalid_config);
    }
}
```

## Severity Classification

### CRITICAL

Issues that cause data loss, corruption, silent failures, security
vulnerabilities, or crashes in production:

- `unwrap()` on user input or network data
- Missing bounds checks on external input
- SQL injection via string concatenation
- Hardcoded secrets or credentials
- `unsafe` without safety invariant documentation
- Data races (missing `Send`/`Sync` bounds)
- Integer overflow/truncation on external data
- Path traversal via unsanitized user input

### HIGH

Significant reliability or maintainability issues:

- Inconsistent error handling across a module
- Missing error context (bare `?` without `map_err`/`context`)
- Resource leaks (missing `Drop` implementation)
- Fire-and-forget async tasks without `JoinHandle` tracking
- `std::sync::Mutex` in async code
- Missing `#[non_exhaustive]` on public enums
- Unbounded collection growth from user input

### MEDIUM

Best practice violations with real impact:

- Unnecessary `clone()` where borrowing suffices
- `as` casts that silently truncate
- Inconsistent logging (println! vs tracing/log)
- Dead code hidden behind `#[allow(dead_code)]`
- Missing `#[must_use]` on important functions
- Deep nesting (3+ levels) instead of early returns
- String formatting in hot loops

### LOW

Minor improvements:

- Suboptimal but correct iterator usage
- Missing `Default` implementation
- Verbose match that could use `matches!()`
- Non-idiomatic but correct code

### INFO

Suggestions for optimization or modernization:

- Performance tuning opportunities
- Newer Rust edition features that could simplify code
- Tooling recommendations

## Quick Reference Checklist

Before approving, check:

- [ ] All `Result` values are handled or explicitly discarded with comment
- [ ] No `unwrap()` in library/binary code on fallible operations
- [ ] All `unsafe` blocks have `// SAFETY:` comments
- [ ] Error types are consistent across the module
- [ ] No `std::sync::Mutex` in async code
- [ ] Collections from external input are bounded
- [ ] No hardcoded secrets or SQL concatenation
- [ ] Public enums use `#[non_exhaustive]` if they may grow
- [ ] Logging is consistent (not mixing println! with tracing/log)
- [ ] Integer conversions use `try_into()` not `as` for external data

## Common Anti-Patterns

| Anti-Pattern | Fix |
|---|---|
| `unwrap()` on network data | Use `?` with error context |
| `clone()` to satisfy borrow checker | Restructure to borrow |
| `String` parameter when `&str` suffices | Change to `&str` |
| Manual loop where iterator works | Use iterator chain |
| `as u32` on user input | Use `try_into()` |
| `println!` in library code | Use `log` or `tracing` |
| `std::sync::Mutex` in async | Use `tokio::sync::Mutex` |
| `Box<dyn Error>` as crate error type | Use `thiserror` or `anyhow` |
| Global mutable state with `lazy_static!` | Use `OnceLock` (1.70+) or `LazyLock` (1.80+) |
| `Rc` when `Arc` is needed for threads | Check Send requirements |
| Missing `unsafe_op_in_unsafe_fn` lint | Add `#![deny(unsafe_op_in_unsafe_fn)]` at crate root |
