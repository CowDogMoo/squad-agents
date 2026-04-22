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

## Trait Extraction for Testability (Hexagonal Architecture)

When I/O-heavy code blocks coverage, the fix is to separate business
logic from I/O by introducing traits. This is the "ports and adapters"
pattern.

### Before (untestable — logic coupled to Redis)

```rust
pub struct AgentCache {
    client: redis::Client,
}

impl AgentCache {
    pub async fn get_or_fetch(&self, id: &str) -> Result<Agent, Error> {
        let mut conn = self.client.get_multiplexed_async_connection().await?;
        if let Some(cached) = redis::cmd("GET").arg(id).query_async(&mut conn).await? {
            return Ok(serde_json::from_str(&cached)?);
        }
        // ... fetch from DB, cache it, return
    }
}
```

### After (testable — logic separated from I/O)

```rust
// Port (trait) — defines what the business logic needs
#[async_trait::async_trait]
pub trait CachePort: Send + Sync {
    async fn get(&self, key: &str) -> Result<Option<String>, CacheError>;
    async fn set(&self, key: &str, val: &str, ttl: u64) -> Result<(), CacheError>;
}

// Business logic — generic over the port
pub struct AgentService<C: CachePort> {
    cache: C,
}

impl<C: CachePort> AgentService<C> {
    pub async fn get_or_fetch(&self, id: &str) -> Result<Agent, Error> {
        if let Some(cached) = self.cache.get(id).await? {
            return Ok(serde_json::from_str(&cached)?);
        }
        // ... fetch, cache, return
    }
}

// Adapter (real implementation) — thin I/O wrapper
pub struct RedisCache { client: redis::Client }

#[async_trait::async_trait]
impl CachePort for RedisCache {
    async fn get(&self, key: &str) -> Result<Option<String>, CacheError> {
        let mut conn = self.client.get_multiplexed_async_connection().await?;
        Ok(redis::cmd("GET").arg(key).query_async(&mut conn).await?)
    }
    async fn set(&self, key: &str, val: &str, ttl: u64) -> Result<(), CacheError> {
        let mut conn = self.client.get_multiplexed_async_connection().await?;
        redis::cmd("SET").arg(key).arg(val).arg("EX").arg(ttl)
            .query_async(&mut conn).await?;
        Ok(())
    }
}
```

### Testing with mockall

When traits exist, use `mockall` to auto-generate mocks:

```rust
#[cfg(test)]
mod tests {
    use super::*;
    use mockall::mock;

    mock! {
        Cache {}
        #[async_trait::async_trait]
        impl CachePort for Cache {
            async fn get(&self, key: &str) -> Result<Option<String>, CacheError>;
            async fn set(&self, key: &str, val: &str, ttl: u64) -> Result<(), CacheError>;
        }
    }

    #[tokio::test]
    async fn cache_hit_returns_deserialized_agent() {
        let mut mock = MockCache::new();
        let agent = Agent { id: "a1".into(), name: "test".into() };
        let json = serde_json::to_string(&agent).unwrap();

        mock.expect_get()
            .with(mockall::predicate::eq("a1"))
            .returning(move |_| Ok(Some(json.clone())));

        let svc = AgentService { cache: mock };
        let result = svc.get_or_fetch("a1").await.unwrap();
        assert_eq!(result.name, "test");
    }

    #[tokio::test]
    async fn cache_miss_fetches_and_caches() {
        let mut mock = MockCache::new();
        mock.expect_get().returning(|_| Ok(None));
        mock.expect_set().times(1).returning(|_, _, _| Ok(()));

        let svc = AgentService { cache: mock };
        let result = svc.get_or_fetch("a1").await;
        // assert on the fetch + cache behavior
    }
}
```

### Testing with manual mock structs (no mockall)

```rust
#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::HashMap;
    use std::sync::Mutex;

    struct FakeCache {
        data: Mutex<HashMap<String, String>>,
    }

    #[async_trait::async_trait]
    impl CachePort for FakeCache {
        async fn get(&self, key: &str) -> Result<Option<String>, CacheError> {
            Ok(self.data.lock().unwrap().get(key).cloned())
        }
        async fn set(&self, key: &str, val: &str, _ttl: u64) -> Result<(), CacheError> {
            self.data.lock().unwrap().insert(key.into(), val.into());
            Ok(())
        }
    }
}
```

## Integration Tests with testcontainers

When you need to verify real I/O behavior (SQL query correctness, Redis
serialization), use `testcontainers` to spin up disposable containers.
These are slower (~2-5s startup) but catch bugs mocks cannot.

### Setup

```toml
# Cargo.toml [dev-dependencies]
testcontainers = "0.27"
testcontainers-modules = { version = "0.15", features = ["redis", "postgres"] }
```

### Postgres Example

```rust
use testcontainers::runners::AsyncRunner;
use testcontainers_modules::postgres::Postgres;

#[tokio::test]
async fn saves_and_retrieves_agent() {
    let container = Postgres::default()
        .with_db_name("test_db")
        .with_user("test")
        .with_password("test")
        .start()
        .await
        .expect("postgres container");

    let host = container.get_host().await.unwrap();
    let port = container.get_host_port_ipv4(5432).await.unwrap();
    let url = format!("postgres://test:test@{host}:{port}/test_db");

    let pool = sqlx::PgPool::connect(&url).await.unwrap();
    sqlx::migrate!("./migrations").run(&pool).await.unwrap();

    let repo = PgRepo::new(pool);
    repo.save(&agent).await.unwrap();
    let found = repo.find_by_id(agent.id).await.unwrap();
    assert_eq!(found.unwrap().name, "test-agent");
    // container auto-cleans on drop
}
```

### Redis Example

```rust
use testcontainers::runners::AsyncRunner;
use testcontainers_modules::redis::Redis;

#[tokio::test]
async fn redis_set_and_get() {
    let container = Redis::default()
        .start()
        .await
        .expect("redis container");

    let host = container.get_host().await.unwrap();
    let port = container.get_host_port_ipv4(6379).await.unwrap();
    let url = format!("redis://{host}:{port}");

    let client = redis::Client::open(url).unwrap();
    let cache = RedisCache { client };

    cache.set("key", "value", 60).await.unwrap();
    assert_eq!(cache.get("key").await.unwrap(), Some("value".into()));
}
```

### When to Use testcontainers vs Mocks

| Use mocks when... | Use testcontainers when... |
|---|---|
| Testing business logic that consumes a trait | Verifying SQL queries return correct results |
| Fast feedback loop needed | Validating migrations work |
| Testing error/retry paths | Testing serialization round-trips with real Redis |
| The trait boundary is clean | The adapter itself has complex logic |

## Coverage Exclusions

### Excluding Files from Coverage

**tarpaulin.toml (project root):**

```toml
[default]
exclude-files = [
    "src/telemetry/init.rs",
    "src/main.rs",
]
```

**CLI:**

```bash
cargo tarpaulin --exclude-files 'src/telemetry/*' 'src/main.rs'
```

**llvm-cov:**

```bash
cargo llvm-cov --ignore-filename-regex 'telemetry/init|main\.rs'
```

### Excluding Functions from Coverage

Use `#[cfg(not(tarpaulin_include))]` on functions that are pure I/O
glue with no testable logic:

```rust
#[cfg(not(tarpaulin_include))]
pub fn init_tracing() {
    // Pure OTel provider wiring — no branches, no error mapping
    opentelemetry::global::set_text_map_propagator(/* ... */);
}
```

**Only exclude when the function body is 100% I/O calls with no branches
or error mapping.** If there's an `if`, `match`, or `map_err`, it has
testable logic — don't exclude it.

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
