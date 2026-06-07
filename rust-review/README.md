# rust-review

Autonomous Rust code review agent that discovers code quality issues, fixes
best-practice violations, and verifies the result compiles and passes tests.

## Overview

The `rust-review` agent analyzes Rust codebases for correctness, safety,
performance, and maintainability issues. It operates in two modes:

- **edit** — discovers issues, applies fixes, verifies compilation and tests
- **readonly** — discovers issues and produces a prioritized report

## Review Categories

1. Error Handling
2. Ownership & Borrowing
3. Concurrency
4. Data Management
5. Trait Design
6. Code Structure
7. API Design
8. Performance
9. Module Organization
10. Security
11. Testing
12. Reliability

## Structure

```
rust-review/
├── agent.yaml                         # Agent manifest
├── system.md                          # Core prompt (identity, rules, workflow)
├── agent.md                           # Execution wrapper
├── task.md                            # Default task instructions
├── README.md                          # This file
└── references/
    └── rust-review-criteria.md        # Comprehensive review knowledge base
```

## Usage

```bash
# Run in edit mode (fix issues)
squad run --agent rust-review

# Run in readonly mode (report only)
squad run --agent rust-review --mode readonly

# Print the bundled prompt
squad run --agent rust-review --print-bundle --dry-run
```

## What It Fixes

- `unwrap()` in non-test code on fallible operations
- Missing error propagation (silently discarded `Result` values)
- Unnecessary `clone()` where borrowing suffices
- Missing safety comments on `unsafe` blocks
- `std::sync::Mutex` in async code
- Fire-and-forget `tokio::spawn` without `JoinHandle`
- Silent integer truncation with `as` casts
- Inconsistent error types and logging
- Hardcoded secrets and SQL string concatenation
- Unbounded collection growth from user input

## What It Skips

- Doc comments and formatting (handled by `rust-doc-comments` and `rustfmt`)
- Test modules (`#[cfg(test)]` blocks)
- Naming style preferences
- Changes requiring new crate dependencies
- Functions whose behavior is asserted by existing tests

## Severity Levels

- **CRITICAL** — crashes, data loss, security vulnerabilities
- **HIGH** — reliability issues, resource leaks, concurrency bugs
- **MEDIUM** — unnecessary allocations, inconsistent patterns, dead code
- **LOW** — minor improvements, non-idiomatic but correct code
- **INFO** — optimization suggestions, modernization opportunities

## Example Output

```markdown
## Summary

The crate has a critical error-handling gap in the network client and an unsafe
block missing a safety comment. Overall structure is sound with good use of
enums for domain modeling.

## Critical Issues

### Silently Discarded Error in Connection Retry
**Severity:** CRITICAL
**Category:** Error Handling
**File:** src/client.rs:47
**Impact:** Failed reconnections go unnoticed, leading to silent data loss

**Problem:**
​```rust
fn reconnect(&mut self) {
    let _ = self.stream.shutdown(Shutdown::Both);
    self.stream = TcpStream::connect(&self.addr).unwrap();
}
​```

**Solution:**
​```rust
fn reconnect(&mut self) -> io::Result<()> {
    let _ = self.stream.shutdown(Shutdown::Both);
    self.stream = TcpStream::connect(&self.addr)?;
    Ok(())
}
​```

**Explanation:** Discarding the `Result` from `connect` and calling `unwrap`
means a transient DNS failure crashes the process. Propagate the error so the
caller can decide whether to retry or alert.

---

## Improvements

### Missing Safety Comment on Unsafe Block
**Severity:** HIGH
**Category:** Security
**File:** src/ffi.rs:23

**Current:**
​```rust
unsafe { libc::mmap(ptr::null_mut(), len, PROT_READ, MAP_PRIVATE, fd, 0) }
​```

**Suggested:**
​```rust
// SAFETY: `fd` is a valid file descriptor obtained from `File::as_raw_fd()`
// and `len` is bounded by the file size checked on the preceding line.
unsafe { libc::mmap(ptr::null_mut(), len, PROT_READ, MAP_PRIVATE, fd, 0) }
​```

**Why:** Every `unsafe` block must document why the invariants hold, per the
Rust API Guidelines.

---

## Positive Observations

- Good use of `thiserror` for structured error types
- Consistent `#[must_use]` on builder methods

## Recommendations

- Run `cargo clippy -- -W clippy::unwrap_used` in CI to catch future `unwrap` calls
```

## Version

0.1.0
