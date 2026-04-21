{{if eq .Mode "edit"}}
Analyze and improve test coverage for this Rust codebase.

If the orchestrator provided a file list and baseline, use them — do NOT
run Glob, cargo test, or check for coverage tools. Read 2-3 source files,
then WRITE TESTS. You must start writing by iteration 6. No exceptions.

If running standalone: discover .rs files with Glob, read source files,
then write tests immediately. Use Write (not Edit) for new test files.

Write tests to close coverage gaps, highest-impact modules first.
Run 'cargo test' after each batch of tests.

IMPORTANT CONSTRAINTS (repeat from system prompt):

- Only create/modify test code — NEVER edit non-test lines in source files
- Tests must pass — fix test code, not source code
- Check src/lib.rs for #[cfg(feature)] — test with --features flag if needed
- Use rstest for parameterized tests (2+ cases), not loop-based tables
- No mocking frameworks unless already in Cargo.toml
- Assert on error content (variant/message), not just is_err()
- No test_ prefix on test functions by default — use <function>_<behavior>
  (but match existing style if module already uses test_ prefix)
- Use approx crate (assert_abs_diff_eq!) for float comparisons
- May add rstest and approx to [dev-dependencies]
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
Analyze test coverage for this Rust codebase.

Use Glob with '**/*.rs' to discover all Rust source files.
Read each file and identify coverage gaps.
Produce a prioritized report of untested functions and modules.

Do NOT write or modify any files.
{{end}}
