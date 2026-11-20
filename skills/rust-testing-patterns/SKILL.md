---
name: rust-testing-patterns
description: "Rust testing patterns — unit and integration tests, parameterized tests with rstest and test-case, error testing, async tests, mocking, test helpers, filesystem tests, property-based testing, and doc tests. Use when writing Rust tests or raising coverage on a module. Also loaded by the rust-tests agent as its knowledge base."
---
# Rust Testing Patterns

House rules for writing idiomatic Rust tests. Topic detail lives in
`references/`; the index below says when to read each file.

## Read-When Index

Each file sits under this skill's base directory. Read one only when its
condition matches the work in front of you.

| File                                         | Read when                                                                          |
| -------------------------------------------- | ---------------------------------------------------------------------------------- |
| `references/parameterized.md`                | You need more than basic `#[rstest]` cases: fixtures, value lists, files, templates, or `test-case` |
| `references/async-mocking.md`                | The module is async, or a dependency sits behind a trait and needs a hand-written mock |
| `references/property-snapshot.md`            | A parser or serializer needs round-trip fuzzing, or output is large structured text |
| `references/coverage.md`                     | Choosing or running a coverage tool, setting targets, excluding I/O glue, or mutation testing |
| `references/refactoring-for-testability.md`  | Writing a "Refactoring Recommendations" report section, or using `mockall` or testcontainers |

## Testing Philosophy

- **Test behavior, not implementation.** Assert what a function returns or
  does, not how it does it.
- **One reason to fail per test.** Do not test unrelated behaviors in a
  single test.
- **Mostly unit tests.** Inline unit tests carry the load; integration tests
  in `tests/` are for true cross-module workflows.

## Unit Tests

Unit tests live in a `#[cfg(test)] mod tests` block at the bottom of the
source file:

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn add_negative_numbers() {
        assert_eq!(add(-1, -2), -3);
    }
}
```

- `use super::*` brings the parent module's items into scope, including
  private ones. Testing private functions this way is intentional and
  idiomatic.
- Unit tests also see `pub(crate)` and `pub(super)` items, but not private
  items of other modules.
- `#[cfg(test)]` keeps test code out of non-test builds.

## Parameterized Tests

Two or more cases for the same function use `rstest` (or `test-case`). Each
`#[case]` becomes its own test in `cargo test` output, so every case runs and
reports even when one fails. Add `rstest` to `[dev-dependencies]` if missing.

```rust
use rstest::rstest;

#[rstest]
#[case("30s", Duration::from_secs(30))]
#[case("5m", Duration::from_secs(300))]
fn parse_duration_valid(#[case] input: &str, #[case] expected: Duration) {
    assert_eq!(parse_duration(input).unwrap(), expected);
}
```

Do not write loop-based table tests (iterating over a `Vec<Case>`). Loop
cases are invisible in `cargo test` output, and the first failing case stops
the rest. A single case is a plain `#[test]`. Cases that need different
setup or assertions per case are separate tests.

## Integration Tests

Use sparingly. Testing one module's public functions is a unit test; put it
inline. When a `tests/` file is warranted:

- Each file in `tests/` compiles as a separate crate and sees only `pub`
  items.
- Shared helpers go in `tests/common/mod.rs`, not `tests/common.rs` (which
  would compile as its own test crate).

## Error Testing

### Result-Returning Tests

Tests can return `Result<(), E>` and use `?` instead of `.unwrap()` chains:

```rust
#[test]
fn parse_and_transform() -> Result<(), Box<dyn std::error::Error>> {
    let val = parse("42")?;
    let transformed = transform(val)?;
    assert_eq!(transformed, expected);
    Ok(())
}
```

Do not combine `#[should_panic]` with a `Result` return type; the compiler
rejects it.

### Assert the Error Variant

`assert!(result.is_err())` alone proves little. Assert the variant, and the
message when it matters:

```rust
#[test]
fn parse_empty_returns_empty_error() {
    assert_matches!(parse(""), Err(ParseError::Empty));
}

#[test]
fn parse_invalid_returns_format_error() {
    let err = parse("!!!").unwrap_err();
    assert!(matches!(err, ParseError::InvalidFormat { .. }));
    assert!(err.to_string().contains("invalid format"));
}

#[test]
fn not_found_error_kind() {
    assert!(lookup("missing").is_err_and(|e| e.kind() == ErrorKind::NotFound));
}
```

### Panics

`#[should_panic(expected = "...")]` is for code whose contract is to panic
(index out of bounds, violated invariants). Give `expected` so an unrelated
panic cannot pass the test.

**Anti-pattern:** do not test error paths with `#[should_panic]` plus
`unwrap()`. If unrelated code panics before the `unwrap()`, the test passes
falsely. Assert on the `Err` variant instead.

## Helpers, Filesystem, and Doc Tests

- Assertion helpers get `#[track_caller]` so a failure points at the calling
  test line, not inside the helper.
- Filesystem tests use `tempfile::tempdir()`; the directory is removed when
  it drops.
- Code in `///` examples runs under `cargo test`. Hide boilerplate lines with
  a leading `#`. `cargo nextest` does not run doc tests, so run
  `cargo test --doc` separately when using nextest.

## Mocking Rules

- Prefer trait-based mocks: implement the existing trait on a small struct
  inside `mod tests`. See `references/async-mocking.md`.
- Mock external HTTP APIs, databases, and time. Use `tempfile` instead of
  mocking the filesystem.
- Do not mock internal functions of the same module, pure functions, or
  types that are cheap to construct.
- Concrete I/O types with no trait are a refactoring recommendation, not
  something a test can fix. See `references/refactoring-for-testability.md`.

## Coverage Exclusions

Exclude a function from coverage (`#[cfg(not(tarpaulin_include))]`) only when
its body is entirely I/O calls with no branches or error mapping. An `if`,
`match`, or `map_err` means there is testable logic; do not exclude it. Tool
commands and file-level exclusion are in `references/coverage.md`.

## What Not to Test

- Trivial getters: `fn name(&self) -> &str { &self.name }`
- Pure delegation: `fn log(&self, msg: &str) { self.inner.log(msg) }`
- `main()` function
- Third-party crate behavior
- Compiler guarantees (type safety, borrow checking)
- `Drop` implementations directly (test via the owning types)
- Generated code from derive macros

Worth testing even when small: constructors and builders (defaults, required
fields), `From`/`TryFrom` conversions (including the failing case), and
`Display` output for error types.

## Quick Reference

### Naming Conventions

- Unit test functions: `<function>_<behavior>` (NO `test_` prefix —
  `#[test]` already marks it. Clippy's `redundant_test_prefix` lint
  flags the prefix.)
  Examples: `parse_db_string_valid`, `spl_to_atomic_negative_clamped`
- Integration test files: `tests/<feature>.rs`
- Test helper module: `tests/common/mod.rs`
- Mock types: `Mock<TraitName>`

### Common Assertions

```rust
assert_eq!(actual, expected);              // Equality
assert_ne!(actual, unexpected);            // Inequality
assert!(condition);                        // Boolean
assert!(matches!(val, Pattern { .. }));    // Pattern matching
assert_matches!(val, Pattern { .. });      // Better — prints Debug on fail
assert!(result.is_ok());                   // Result OK
assert!(result.is_err());                  // Result Err
assert!(option.is_some());                // Option Some
assert!(option.is_none());                // Option None
```

Prefer `assert_matches!` over `assert!(matches!(...))` — the former prints
the debug representation of the actual value on failure; the latter only
says "assertion failed." Available via `use std::assert_matches::assert_matches`
(nightly) or the `assert_matches` crate (stable).

For large structs, `pretty_assertions::assert_eq` prints a diff on failure
(see `references/property-snapshot.md`).

### Float Comparisons

Use the `approx` crate for float comparisons — add it to
`[dev-dependencies]`. Do NOT use raw epsilon comparisons like
`assert!((a - b).abs() < 1e-9)` — hardcoded epsilons are arbitrary
and don't communicate intent.

```rust
use approx::assert_abs_diff_eq;

assert_abs_diff_eq!(actual, expected, epsilon = 0.01);
assert_relative_eq!(actual, expected, max_relative = 1e-6);
```

### Test Attributes

```rust
#[test]                                    // Basic test
#[test]
#[should_panic(expected = "msg")]          // Expected panic
#[test]
#[ignore]                                  // Skipped by default
#[tokio::test]                             // Async test (tokio)
#[tokio::test(flavor = "multi_thread")]    // Multi-threaded async
```
