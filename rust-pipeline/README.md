# rust-pipeline

Composed agent that runs Rust quality agents sequentially: review, tests,
and doc comments.

## Overview

This is a composed agent — it has no prompts of its own. It chains three
sub-agents in dependency order, passing context between stages:

| Order | Agent | Purpose |
|-------|-------|---------|
| 1 | rust-review | Code quality, safety, and correctness fixes |
| 2 | rust-tests | Test coverage analysis and gap filling |
| 3 | rust-doc-comments | Public API documentation |

Gates run `cargo clippy` after review, `cargo test` after tests, and
`cargo build` after docs to catch regressions.

## Usage

```bash
# Run the full pipeline against the current directory
squad run --agent rust-pipeline

# Run against a specific Rust project
squad run --agent rust-pipeline --working-dir /path/to/rust-project

# With cost limit
squad run --agent rust-pipeline --max-cost 20.00
```

## Stages

```
review → tests → docs
  │        │       │
  ▼        ▼       ▼
clippy  cargo   cargo
        test    build
```

## Version

0.4.0
