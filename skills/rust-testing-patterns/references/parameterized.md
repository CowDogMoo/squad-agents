# Parameterized Tests

Read when a function needs two or more test cases and you need more than the
basic `#[rstest]` plus `#[case]` form shown in SKILL.md: named cases, value
lists, fixtures, file-driven cases, timeouts, templates, or `test-case`.

## Contents

- rstest: basic cases, named cases, value lists, fixtures, file-based
  testing, async with timeout, `FromStr` conversion, `rstest_reuse`
- test-case, and rstest versus test-case
- When to use parameterized tests, and when not to

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

### Named Cases

Add descriptive names to cases for clearer test output:

```rust
#[rstest]
#[case::zero_base(0, 0)]
#[case::one_base(1, 1)]
#[case::fib_two(2, 1)]
fn fibonacci(#[case] input: u32, #[case] expected: u32) {
    assert_eq!(expected, fib(input));
}
```

### Value Lists (Cartesian Product)

`#[values]` generates all combinations of arguments:

```rust
#[rstest]
fn valid_names(
    #[values("John", "alice", "My_Name")] name: &str,
    #[values(14, 50, 100)] age: u8,
) {
    assert!(is_valid(name, age));
}
// Generates 9 tests: John/14, John/50, ..., My_Name/100
```

### Fixtures

Reusable test setup via `#[fixture]`:

```rust
#[fixture]
fn test_config() -> Config {
    Config::builder().timeout(30).build().unwrap()
}

#[rstest]
fn service_starts(test_config: Config) {
    let svc = Service::new(test_config);
    assert!(svc.is_running());
}
```

Override fixture defaults with `#[with]`:

```rust
#[rstest]
fn custom_user(#[with("Bob")] user: User) {
    assert_eq!(user.name(), "Bob");
}
```

### File-Based Testing

Generate tests from files matching glob patterns:

```rust
#[rstest]
fn valid_configs(
    #[files("testdata/*.toml")] #[exclude("invalid")] path: PathBuf,
) {
    let config = Config::from_file(&path);
    assert!(config.is_ok());
}
```

### Async with Timeout

```rust
#[rstest]
#[timeout(Duration::from_millis(100))]
#[tokio::test]
async fn fast_response(test_config: Config) {
    let result = fetch(&test_config).await;
    assert!(result.is_ok());
}
```

### Magic `FromStr` Conversion

rstest auto-converts string literals to types implementing `FromStr`:

```rust
#[rstest]
#[case("resources/data", 42)]
fn count_lines(#[case] path: PathBuf, #[case] expected: usize) {
    // "resources/data" auto-converts to PathBuf
    assert_eq!(count(&path), expected);
}
```

### Template Reuse with `rstest_reuse`

Share case sets across multiple test functions:

```rust
use rstest_reuse::{self, *, template};

#[template]
#[rstest]
#[case(2, 2)]
#[case(4, 4)]
fn valid_pairs(#[case] a: u32, #[case] b: u32) {}

#[apply(valid_pairs)]
fn equality(#[case] a: u32, #[case] b: u32) {
    assert_eq!(a, b);
}
```

## Parameterized Tests with `test-case`

`test-case` is an alternative to rstest with simpler syntax for
straightforward cases. Add to `[dev-dependencies]`:

```rust
use test_case::test_case;

#[test_case("30s" => Duration::from_secs(30) ; "seconds")]
#[test_case("5m"  => Duration::from_secs(300) ; "minutes")]
fn parse_duration(input: &str) -> Duration {
    my_crate::parse_duration(input).unwrap()
}

#[test_case("" ; "empty string")]
#[test_case("abc" ; "non-numeric")]
#[should_panic]
fn parse_duration_invalid(input: &str) {
    my_crate::parse_duration(input).unwrap();
}
```

**rstest vs test-case:** rstest is stronger for fixtures, async, and
complex setups. test-case is simpler when you just need input/output
pairs. Both generate independent tests visible in `cargo test` output.

### When to Use Parameterized Tests

- 2+ test cases for the same function
- Testing different input/output combinations
- Parameterized error cases

### When NOT to Use Parameterized Tests

- Single test case — just write a normal `#[test]`
- Tests requiring different setup/teardown per case
- Tests with complex assertions that vary per case
