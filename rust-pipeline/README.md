# rust-pipeline

Orchestrator agent that runs `rust-review`, `rust-tests`, and
`rust-doc-comments` sequentially with context passing to avoid redundant work.

## Overview

The `rust-pipeline` agent coordinates three child agents in order:

1. **rust-review** — fix code quality and safety issues
2. **rust-tests** — fill test coverage gaps
3. **rust-doc-comments** — add missing doc comments

Each agent receives a summary of what the previous agent changed, so it skips
files and declarations that were already handled.

## Usage

```bash
# Run the full pipeline against the current directory
squad run --agent rust-pipeline

# Run against a specific Rust project
squad run --agent rust-pipeline --working-dir /path/to/rust-project

# Specify model and provider
squad run --agent rust-pipeline --model claude-opus-4-6 --provider anthropic

# With explicit API key
squad run --agent rust-pipeline \
  --working-dir /path/to/project \
  --model claude-opus-4-6 \
  --provider anthropic \
  --max-iterations 50 \
  --api-key "$YOUR_API_KEY"
```

## Example

```bash
LOG_LEVEL=debug squad run \
  --agent rust-pipeline \
  --working-dir /home/user/my-rust-crate \
  --model claude-opus-4-6 \
  --provider anthropic \
  --max-iterations 50 \
  --api-key "$YOUR_API_KEY"
```

### Example Output

```markdown
## Pipeline Summary

### Stage 1: rust-review
**Files modified:** 4
- src/client.rs — propagated error from `reconnect()` instead of `unwrap()`
- src/ffi.rs — added safety comment on `unsafe` block
- src/parser.rs — replaced `as` truncation with `try_into()`
- src/config.rs — switched `std::sync::Mutex` to `tokio::sync::Mutex`

### Stage 2: rust-tests
**Tests added:** 12
**Coverage:** 62% → 78%
- src/parser.rs — 5 tests (edge cases for malformed input)
- src/client.rs — 4 tests (reconnect error paths)
- src/config.rs — 3 tests (concurrent access)

### Stage 3: rust-doc-comments
**Doc comments added:** 9
- src/lib.rs — module-level documentation
- src/client.rs — `Client`, `connect()`, `reconnect()`
- src/parser.rs — `Parser`, `parse()`, `validate()`
- src/config.rs — `Config`, `load()`

## Validation
- `cargo build`: PASS
- `cargo test`: PASS (34 tests)
- `cargo clippy`: PASS
```

## Children

| Order | Agent | Purpose |
|-------|-------|---------|
| 1 | rust-review | Code quality, safety, and correctness fixes |
| 2 | rust-tests | Test coverage analysis and gap filling |
| 3 | rust-doc-comments | Public API documentation |

## Version

0.1.0
