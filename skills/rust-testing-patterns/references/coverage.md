# Coverage Tools, Exclusions, and Mutation Testing

Read when choosing or running a coverage tool, setting per-area targets,
excluding pure I/O glue from coverage, or checking whether covered code is
actually asserted on.

## Contents

- Tools: cargo llvm-cov, cargo tarpaulin
- Test runners: cargo nextest
- Coverage targets
- Mutation testing with cargo-mutants
- Coverage exclusions: files and functions

## Tools

- **`cargo llvm-cov`** (preferred) — LLVM source-based instrumentation,
  most accurate. Supports line, region, and branch coverage. Cross-platform
  (Linux, macOS, Windows). Install: `cargo install cargo-llvm-cov`
- **`cargo tarpaulin`** (fallback) — Linux-focused, limited macOS support,
  no Windows. Primarily line coverage. Install: `cargo install cargo-tarpaulin`

Use `cargo llvm-cov` when available; fall back to tarpaulin for
Linux-only CI environments.

## Test Runners

- **`cargo nextest`** — runs each test in its own process, with better
  output and retry support. Install: `cargo install cargo-nextest`
- **Important:** `cargo nextest` does not run doctests. Run
  `cargo test --doc` separately when using nextest.
- Use `cargo nextest run` in CI for speed; use `cargo test` locally
  when you need doctests.

## Coverage Targets

| Code Type | Target |
|-----------|--------|
| Business logic | 80%+ |
| Error handling | 75%+ |
| Public API | 90%+ |
| Generated code | Skip |
| CLI glue code | 50%+ |

## Mutation Testing with `cargo-mutants`

Coverage measures "was this code reached?" Mutation testing measures
"do tests actually check this code's behavior?" It injects small bugs
(flips operators, replaces return values, removes calls) and verifies
at least one test fails for each mutation.

```bash
cargo install cargo-mutants
cargo mutants              # run against the whole crate
cargo mutants -f src/parser.rs  # run against one file
```

**Outcomes:**

| Result | Meaning |
|--------|---------|
| Caught | A test failed — good |
| Missed | No test caught the mutation — gap |
| Unviable | Mutation didn't compile — skip |
| Timeout | Test hung — possibly an infinite loop |

Use mutation testing to complement coverage, especially for code with
high coverage but weak assertions. "Missed" mutants point to tests
that execute the code but don't actually verify its behavior.

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
