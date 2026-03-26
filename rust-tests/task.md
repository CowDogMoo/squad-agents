{{if eq .Mode "edit"}}
Analyze and improve test coverage for this Rust codebase.

Start by checking for coverage tools (cargo llvm-cov or cargo tarpaulin).
Measure baseline coverage before writing any tests.
Discover all .rs files with Glob '**/*.rs', skip target/.
Read source files and existing test modules.
Write tests to close coverage gaps, highest-impact modules first.
Run 'cargo test' after each batch.

IMPORTANT CONSTRAINTS (repeat from system prompt):

- Only create/modify test code — NEVER edit source files
- Tests must pass — fix test code, not source code
- Table-driven tests for 2+ cases per function
- No mocking frameworks unless already in Cargo.toml
- Assert on error content (variant/message), not just is_err()
- Async tests need #[tokio::test] or equivalent
- Unit tests go in #[cfg(test)] mod tests blocks
- Integration tests go in tests/ directory
- Per-module target: {{.Default "COVERAGE_TARGET" "75"}}%
- Read each file ONCE, catalog all gaps, then write tests
- Target ≤15 iterations for small codebases
- After cargo test passes, emit report IMMEDIATELY
- Always analyze and report gaps even if target is already met
{{end}}
{{if eq .Mode "readonly"}}
Analyze test coverage for this Rust codebase.

Use Glob with '**/*.rs' to discover all Rust source files.
Read each file and identify coverage gaps.
Produce a prioritized report of untested functions and modules.

Do NOT write or modify any files.
{{end}}
