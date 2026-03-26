{{if eq .Mode "edit"}}
Analyze and improve test coverage for this Rust codebase.

Start by checking for coverage tools (cargo llvm-cov or cargo tarpaulin).
Measure baseline coverage before writing any tests.
Discover all .rs files with Glob '**/*.rs', skip target/.
Read source files and existing test modules.
Write tests to close coverage gaps, highest-impact modules first.
Run 'cargo test' after each batch.

IMPORTANT CONSTRAINTS (repeat from system prompt):

- Only create/modify test code — NEVER edit non-test lines in source files
- Tests must pass — fix test code, not source code
- Use rstest for parameterized tests (2+ cases), not loop-based tables
- No mocking frameworks unless already in Cargo.toml
- Assert on error content (variant/message), not just is_err()
- No test_prefix on test functions — use <function>_<behavior>
- Use approx crate (assert_abs_diff_eq!) for float comparisons
- May add rstest and approx to [dev-dependencies]
- Async tests need #[tokio::test] or equivalent
- Binary crates (main.rs only, no lib.rs): use inline #[cfg(test)] mod tests
- Library/mixed crates: unit tests inline, integration tests in tests/
- tests/ directory does NOT work for binary-only crates
- Add tests INCREMENTALLY: first Edit empty #[cfg(test)] mod tests skeleton,
  then add 1-3 test fns per Edit (≤30 lines each). NEVER 50+ lines at once.
- NEVER rewrite entire source files — Write truncates content >10KB
- After every Edit, run 'tail -5 <file>' to verify nothing was deleted
- Do NOT use git stash or git checkout — they destroy prior agents' changes
- Read each file at most twice: once to analyze, once before writing
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
