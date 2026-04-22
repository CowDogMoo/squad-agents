{{if eq .Mode "edit"}}
{{- if .Var "CRATE"}}
**SCOPE: Focus exclusively on the `{{.Var "CRATE"}}` crate.** Do NOT wander to
other crates. All Glob patterns, Read calls, and test writes must target
files within the `{{.Var "CRATE"}}` directory. Ignore source files outside it.
{{- end}}

Analyze and improve test coverage for this Rust codebase.

If the orchestrator provided a file list and baseline, use them — do NOT
run Glob, cargo test, or check for coverage tools. Read 2-3 source files,
then WRITE TESTS. You must start writing by iteration 6. No exceptions.

If running standalone: discover .rs files with Glob, read source files,
then write tests immediately. Use Write (not Edit) for new test files.

Write tests to close coverage gaps. PRIORITY ORDER:

1. Files with ZERO tests — address these first, no exceptions
2. Files below target — improve these next
3. Already-tested files — only after all others are addressed

Files that import sqlx, redis, reqwest, or opentelemetry are NOT exempt.
Read them, find the pure logic (query builders, data transforms,
validation, type conversions, formatters), and test it. Only skip the
specific functions that require a live connection.

When traits already exist for I/O dependencies, use mockall to test
business logic that consumes them. You may add mockall to dev-dependencies.

Calculate the coverage ceiling before writing tests. If the ceiling is
below target, report it with specific recommendations (trait extraction,
--exclude-files, testcontainers). You may add #[cfg(not(tarpaulin_include))]
to pure I/O glue functions (no branches, no error mapping).

Run 'cargo test' after each batch of tests.

IMPORTANT CONSTRAINTS (repeat from system prompt):

- Only create/modify test code — NEVER edit non-test lines in source files
- Tests must pass — fix test code, not source code
- Check src/lib.rs for #[cfg(feature)] — test with --features flag if needed
- Use rstest for parameterized tests (2+ cases), not loop-based tables
- No mocking frameworks unless already in Cargo.toml
- Assert on error content (variant/message), not just is_err() — prefer
  assert_matches! over assert!(matches!(...)), use is_err_and() for inline checks
- No test_ prefix on test functions by default — use <function>_<behavior>
  (but match existing style if module already uses test_ prefix)
- Use approx crate (assert_abs_diff_eq!) for float comparisons
- Result-returning tests: use -> Result<(), E> with ? instead of .unwrap() chains
- Do NOT use #[should_panic] + unwrap() for error tests — false positives
- May add rstest, approx, assert_matches, pretty_assertions to [dev-dependencies]
- Async tests need #[tokio::test] or equivalent
- Binary crates (main.rs only, no lib.rs): use inline #[cfg(test)] mod tests
- Library/mixed crates: unit tests inline in #[cfg(test)] mod tests blocks
- Do NOT create tests/*.rs files unless testing cross-module workflows
- tests/ directory does NOT work for binary-only crates
- Use Write (not Edit) for new test files and new #[cfg(test)] blocks:
  Read the file once, then Write the complete file with tests appended.
  One Write call replaces many fragile Edit calls.
- If Edit fails ("text not found"), switch to Write immediately.
- Do NOT use Write on files >10KB — use Edit instead (content truncates).
  Empty test modules are forbidden — always include real test functions.
- After every Edit, Read the last few lines to verify nothing was deleted
- Do NOT use git stash or git checkout — they destroy prior agents' changes
- Read each file at most once — catalog all gaps, then write tests
- Per-module target: {{.Default "COVERAGE_TARGET" "75"}}%
- Target ≤15 iterations for small codebases
- After cargo test passes, emit report IMMEDIATELY
- Always analyze and report gaps even if target is already met
{{end}}
{{if eq .Mode "readonly"}}
{{- if .Var "CRATE"}}
**SCOPE: Focus exclusively on the `{{.Var "CRATE"}}` crate.** Ignore files outside it.
{{- end}}

Analyze test coverage for this Rust codebase.

Use Glob with '**/*.rs' to discover all Rust source files.
Read each file and identify coverage gaps.
Produce a prioritized report of untested functions and modules.

Do NOT write or modify any files.
{{end}}
