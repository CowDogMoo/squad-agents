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

## Version

0.1.0
