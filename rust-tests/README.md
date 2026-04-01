# rust-tests

Autonomous Rust test coverage agent that discovers gaps, writes tests, and
iterates to a target percentage.

## Overview

The `rust-tests` agent analyzes Rust codebases for test coverage gaps, writes
idiomatic tests, and verifies they compile and pass. It always analyzes
coverage even if the target is already met.

## Features

- Measures baseline coverage with `cargo llvm-cov` or `cargo tarpaulin`
- Discovers untested modules and functions
- Writes table-driven unit tests and integration tests
- Supports async tests with `#[tokio::test]`
- Uses trait-based mocking (no external mocking frameworks required)
- Per-module coverage targeting

## Structure

```
rust-tests/
├── agent.yaml                          # Agent manifest
├── system.md                           # Core prompt (identity, rules, workflow)
├── agent.md                            # Execution wrapper
├── task.md                             # Default task instructions
├── README.md                           # This file
└── references/
    └── rust-testing-patterns.md        # Testing patterns knowledge base
```

## Usage

```bash
# Run with default 75% target
squad run --agent rust-tests

# Run with custom coverage target
squad run --agent rust-tests -v COVERAGE_TARGET=80

# Print the bundled prompt
squad run --agent rust-tests --print-bundle --dry-run
```

## What It Tests

- Functions with conditional logic, loops, error returns
- Public API surface
- Error paths with variant/message assertions
- Edge cases (None, empty, zero, boundary)
- Constructor and validation functions
- From/TryFrom implementations

## What It Skips

- Trivial getters/setters
- Pure delegation functions
- `main()` functions
- Functions requiring live external services
- Generated code

## Example

### Input

```rust
pub fn clamp(value: f64, min: f64, max: f64) -> f64 {
    if value < min {
        min
    } else if value > max {
        max
    } else {
        value
    }
}

pub fn parse_hex_color(s: &str) -> Result<(u8, u8, u8), ColorError> {
    let s = s.strip_prefix('#').unwrap_or(s);
    if s.len() != 6 {
        return Err(ColorError::InvalidLength);
    }
    let r = u8::from_str_radix(&s[0..2], 16).map_err(|_| ColorError::InvalidHex)?;
    let g = u8::from_str_radix(&s[2..4], 16).map_err(|_| ColorError::InvalidHex)?;
    let b = u8::from_str_radix(&s[4..6], 16).map_err(|_| ColorError::InvalidHex)?;
    Ok((r, g, b))
}
```

### Output

```rust
#[cfg(test)]
mod tests {
    use super::*;
    use rstest::rstest;

    #[rstest]
    #[case(5.0, 0.0, 10.0, 5.0)]
    #[case(-1.0, 0.0, 10.0, 0.0)]
    #[case(15.0, 0.0, 10.0, 10.0)]
    #[case(0.0, 0.0, 10.0, 0.0)]
    #[case(10.0, 0.0, 10.0, 10.0)]
    fn clamp_returns_expected(
        #[case] value: f64,
        #[case] min: f64,
        #[case] max: f64,
        #[case] expected: f64,
    ) {
        approx::assert_relative_eq!(clamp(value, min, max), expected);
    }

    #[rstest]
    #[case("#ff8000", (255, 128, 0))]
    #[case("00ff00", (0, 255, 0))]
    #[case("#000000", (0, 0, 0))]
    fn parse_hex_color_valid(
        #[case] input: &str,
        #[case] expected: (u8, u8, u8),
    ) {
        assert_eq!(parse_hex_color(input).unwrap(), expected);
    }

    #[rstest]
    #[case("")]
    #[case("#fff")]
    #[case("#zzzzzz")]
    fn parse_hex_color_invalid(#[case] input: &str) {
        assert!(parse_hex_color(input).is_err());
    }
}
```

## Version

0.1.0
