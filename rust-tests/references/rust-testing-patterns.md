# Rust Testing Patterns

Comprehensive reference for writing idiomatic Rust tests.

## Testing Philosophy

### Core Principles

- **Test behavior, not implementation.** Tests should verify what a function
  does, not how it does it internally.
- **F.I.R.S.T.** — Fast, Independent, Repeatable, Self-validating, Timely.
- **Test pyramid** — Many unit tests, fewer integration tests, minimal
  end-to-end tests.
- **Each test should have one reason to fail.** Avoid testing multiple
  unrelated behaviors in a single test.

### Test Organization

```
src/
├── lib.rs               # #[cfg(test)] mod tests at bottom
├── parser.rs            # #[cfg(test)] mod tests at bottom
└── ...
tests/
├── integration_test.rs  # Public API integration tests
└── ...
```

## Unit Tests

Unit tests live in `#[cfg(test)] mod tests` blocks within the source file:

```rust
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn add_positive_numbers() {
        assert_eq!(add(2, 3), 5);
    }

    #[test]
    fn add_negative_numbers() {
        assert_eq!(add(-1, -2), -3);
    }

    #[test]
    fn add_zero() {
        assert_eq!(add(0, 5), 5);
    }
}
```

### Key Rules

- **`use super::*`** to import from the parent module.
- **`#[cfg(test)]`** ensures test code is excluded from release builds.
- Unit tests can access `pub(crate)` and `pub(super)` items.
- Unit tests CANNOT access private items from other modules.

## Parameterized Tests with `rstest`

When testing 2+ cases for the same function, use `rstest` to generate
independent tests per case. Add `rstest` to `[dev-dependencies]` if not
present. Each `#[case]` becomes its own test in `cargo test` output,
giving granular reporting and allowing all cases to run even if one fails.

```rust
use rstest::rstest;

#[rstest]
#[case("30s", Duration::from_secs(30))]
#[case("5m", Duration::from_secs(300))]
fn parse_duration_valid(#[case] input: &str, #[case] expected: Duration) {
    assert_eq!(parse_duration(input).unwrap(), expected);
}

#[rstest]
#[case("abc")]
#[case("")]
fn parse_duration_invalid(#[case] input: &str) {
    assert!(parse_duration(input).is_err());
}
```

Do NOT use loop-based table tests (iterating over a `Vec<Case>`). Loop
cases are invisible to `cargo test` output and a failure in one case
stops remaining cases from running.

### When to Use `rstest`

- 2+ test cases for the same function
- Testing different input/output combinations
- Parameterized error cases

### When NOT to Use Parameterized Tests

- Single test case
- Tests requiring different setup/teardown per case
- Tests with complex assertions that vary per case

## Integration Tests

**Use sparingly.** Most tests should be inline `#[cfg(test)]` unit tests.
Only use `tests/` for true cross-module integration workflows (e.g.,
testing that parsing + correlation + reporting work together end-to-end).
Testing a single module's public functions is a unit test — put it inline.

Integration tests live in the `tests/` directory and test the public API:

```rust
// tests/api_test.rs
use my_crate::{Config, App};

#[test]
fn app_processes_valid_config() {
    let config = Config::builder()
        .timeout(30)
        .build()
        .unwrap();
    let app = App::new(config);
    let result = app.process("input");
    assert!(result.is_ok());
}
```

### Key Rules

- Each file in `tests/` is compiled as a separate crate.
- Can only access `pub` items from your crate.
- Use `tests/common/mod.rs` for shared test helpers (NOT `tests/common.rs`,
  which would be compiled as its own test crate).

## Error Testing

### Basic Error Test

```rust
#[test]
fn parse_invalid_returns_error() {
    let result = parse("invalid");
    assert!(result.is_err());
}
```

### Testing Error Variants

```rust
#[test]
fn parse_empty_returns_empty_error() {
    let result = parse("");
    assert!(matches!(result, Err(ParseError::Empty)));
}

#[test]
fn parse_invalid_returns_format_error() {
    let err = parse("!!!").unwrap_err();
    assert!(matches!(err, ParseError::InvalidFormat { .. }));
    assert!(err.to_string().contains("invalid format"));
}
```

### Testing Panics

```rust
#[test]
#[should_panic(expected = "index out of bounds")]
fn get_out_of_bounds_panics() {
    let items = vec![1, 2, 3];
    get_item(&items, 10);
}
```

## Async Tests

### With Tokio

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn fetch_returns_data() {
        let client = MockClient::new();
        let result = fetch_data(&client).await;
        assert!(result.is_ok());
    }

    #[tokio::test]
    async fn fetch_timeout_returns_error() {
        let client = MockClient::with_delay(Duration::from_secs(60));
        let result = fetch_data(&client).await;
        assert!(matches!(result, Err(FetchError::Timeout)));
    }
}
```

### Key Rules

- Check Cargo.toml for the async runtime (tokio, async-std, smol).
- Use `#[tokio::test]` for tokio-based code.
- Use `#[tokio::test(flavor = "multi_thread")]` when tests need
  multi-threaded runtime.

## Mocking

### Trait-Based Mocking

The preferred Rust approach — define a trait and implement it for tests:

```rust
// In source code
pub trait Repository {
    fn find_by_id(&self, id: u64) -> Result<User, Error>;
}

pub struct Service<R: Repository> {
    repo: R,
}

// In test code
#[cfg(test)]
mod tests {
    use super::*;

    struct MockRepo {
        users: HashMap<u64, User>,
    }

    impl Repository for MockRepo {
        fn find_by_id(&self, id: u64) -> Result<User, Error> {
            self.users.get(&id)
                .cloned()
                .ok_or(Error::NotFound)
        }
    }

    #[test]
    fn service_returns_user() {
        let mut users = HashMap::new();
        users.insert(1, User { name: "Alice".into() });
        let repo = MockRepo { users };
        let service = Service { repo };

        let user = service.get_user(1).unwrap();
        assert_eq!(user.name, "Alice");
    }
}
```

### When to Mock

- External HTTP APIs
- Database connections
- File system operations (or use `tempfile`)
- Time-dependent operations

### When NOT to Mock

- Internal functions in the same module
- Pure functions with no side effects
- Types that are cheap to construct

## Test Helpers

### Using `#[track_caller]`

```rust
#[cfg(test)]
mod tests {
    #[track_caller]
    fn assert_parses_to(input: &str, expected: &Output) {
        let result = parse(input).unwrap();
        assert_eq!(&result, expected);
    }

    #[test]
    fn parse_valid_inputs() {
        // If this fails, the error points HERE, not inside assert_parses_to
        assert_parses_to("input1", &expected1);
        assert_parses_to("input2", &expected2);
    }
}
```

### Shared Test Utilities

For integration tests, use `tests/common/mod.rs`:

```rust
// tests/common/mod.rs
pub fn setup_test_db() -> TestDb {
    // shared setup logic
}

// tests/api_test.rs
mod common;

#[test]
fn creates_user_in_db() {
    let db = common::setup_test_db();
    // ...
}
```

## Filesystem Tests

```rust
#[test]
fn write_and_read_config() {
    let dir = tempfile::tempdir().unwrap();
    let path = dir.path().join("config.toml");

    write_config(&path, &config).unwrap();
    let loaded = read_config(&path).unwrap();

    assert_eq!(loaded, config);
    // dir is automatically cleaned up when dropped
}
```

## Property-Based Testing

With `proptest`:

```rust
use proptest::prelude::*;

proptest! {
    #[test]
    fn parse_roundtrip(s in "[a-z]{1,10}") {
        let parsed = parse(&s).unwrap();
        let rendered = parsed.to_string();
        assert_eq!(rendered, s);
    }

    #[test]
    fn serialize_deserialize_roundtrip(val in any::<MyType>()) {
        let bytes = val.serialize();
        let decoded = MyType::deserialize(&bytes).unwrap();
        assert_eq!(decoded, val);
    }
}
```

**Commit the proptest regressions file.** Proptest records failing seeds
to a file (typically `proptest-regressions/`). Commit this to source
control so regressions are caught in CI.

## Coverage

### Tools

- **`cargo llvm-cov`** (preferred) — LLVM source-based instrumentation,
  most accurate. Supports line, region, and branch coverage. Cross-platform
  (Linux, macOS, Windows). Install: `cargo install cargo-llvm-cov`
- **`cargo tarpaulin`** (fallback) — Linux-focused, limited macOS support,
  no Windows. Primarily line coverage. Install: `cargo install cargo-tarpaulin`

Use `cargo llvm-cov` when available; fall back to tarpaulin for
Linux-only CI environments.

### Test Runners

- **`cargo nextest`** — up to 60% faster than `cargo test` in CI. Runs
  each test in its own process, provides better output and retry support.
  Install: `cargo install cargo-nextest`
- **Important:** `cargo nextest` does not run doctests. Run
  `cargo test --doc` separately when using nextest.
- Use `cargo nextest run` in CI for speed; use `cargo test` locally
  when you need doctests.

### Coverage Targets

| Code Type | Target |
|-----------|--------|
| Business logic | 80%+ |
| Error handling | 75%+ |
| Public API | 90%+ |
| Generated code | Skip |
| CLI glue code | 50%+ |

### What Coverage Doesn't Measure

- Code correctness (100% coverage ≠ bug-free)
- Edge case completeness
- Error message quality
- Performance characteristics

## Common Patterns

### Testing Display Implementation

```rust
#[test]
fn error_display() {
    let err = MyError::NotFound { id: 42 };
    assert_eq!(err.to_string(), "item 42 not found");
}
```

### Testing From/TryFrom

```rust
#[test]
fn user_from_row() {
    let row = DbRow { id: 1, name: "Alice".into() };
    let user: User = row.into();
    assert_eq!(user.id, 1);
    assert_eq!(user.name, "Alice");
}

#[test]
fn config_try_from_invalid() {
    let raw = RawConfig { timeout: -1 };
    let result = Config::try_from(raw);
    assert!(matches!(result, Err(ConfigError::InvalidTimeout)));
}
```

### Testing Builder Pattern

```rust
#[test]
fn builder_with_defaults() {
    let config = ConfigBuilder::new().build().unwrap();
    assert_eq!(config.timeout, Duration::from_secs(30));
    assert_eq!(config.retries, 3);
}

#[test]
fn builder_with_custom_values() {
    let config = ConfigBuilder::new()
        .timeout(Duration::from_secs(60))
        .retries(5)
        .build()
        .unwrap();
    assert_eq!(config.timeout, Duration::from_secs(60));
    assert_eq!(config.retries, 5);
}

#[test]
fn builder_missing_required_field() {
    let result = ConfigBuilder::new()
        .build_without_required();
    assert!(result.is_err());
}
```

## What NOT to Test

- Trivial getters: `fn name(&self) -> &str { &self.name }`
- Pure delegation: `fn log(&self, msg: &str) { self.inner.log(msg) }`
- `main()` function
- Third-party crate behavior
- Compiler guarantees (type safety, borrow checking)
- `Drop` implementations directly (test via the owning types)
- Generated code from derive macros

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
assert!(result.is_ok());                   // Result OK
assert!(result.is_err());                  // Result Err
assert!(option.is_some());                // Option Some
assert!(option.is_none());                // Option None
```

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
