# Property-Based, Snapshot, and Diff-Assertion Testing

Read when the code has a round-trip or invariant worth fuzzing (parsers,
serializers), produces large structured output (reports, JSON, YAML), or a
`assert_eq!` failure on a large struct would be unreadable.

## Contents

- Property-based testing with proptest
- Snapshot testing with insta
- Enhanced assertion output: pretty_assertions, similar-asserts

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

## Snapshot Testing with `insta`

Snapshot tests capture complex outputs (JSON, YAML, formatted text)
and compare against stored reference files. Useful for testing
serialization, report generation, or any structured output.

```rust
use insta::assert_yaml_snapshot;

#[test]
fn report_snapshot() {
    let report = generate_report(&data);
    assert_yaml_snapshot!(report);
}
```

### Workflow

- First run creates `.snap` files with the captured output.
- `cargo insta review` opens an interactive TUI to approve/reject
  changes.
- `cargo insta accept` accepts all pending changes.
- Commit `.snap` files to source control.

**Anti-pattern:** Do not blindly accept all snapshot changes — review
each one. Snapshots are only as good as the reviews.

Insta supports redaction of dynamic values (timestamps, UUIDs) to
prevent false failures.

## Enhanced Assertion Output

### `pretty_assertions`

Drop-in replacement for `assert_eq!` that shows colorful diffs on
failure. Add to `[dev-dependencies]`:

```rust
use pretty_assertions::assert_eq;

#[test]
fn complex_struct_equality() {
    assert_eq!(actual, expected); // shows diff on failure
}
```

### `similar-asserts`

Alternative that uses the `similar` library for diffing. Supports
comparing either `Debug` or `Serialize` representations:

```rust
use similar_asserts::assert_eq;

#[test]
fn large_output_comparison() {
    assert_eq!(actual, expected);
}
```

Both are test-only dependencies and safe to add to
`[dev-dependencies]`.
