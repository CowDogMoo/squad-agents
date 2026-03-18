Analyze this codebase's test coverage and bring each package to {{.Default "COVERAGE_TARGET" "75"}}% coverage.

TARGET: {{.Default "COVERAGE_TARGET" "75"}}% coverage PER PACKAGE, not just overall.

- If a package is below {{.Default "COVERAGE_TARGET" "75"}}%, keep writing tests until it reaches {{.Default "COVERAGE_TARGET" "75"}}%
- Exception: CLI/Cobra command packages (e.g. cmd/*) are often 50-60% due to
  integration-heavy code. Document what can't be unit tested and move on.

PHASE 1 IS MANDATORY — even if overall coverage is above {{.Default "COVERAGE_TARGET" "75"}}%:

1. Run 'go test ./... -coverprofile=coverage.out -count=1' and save output
2. Check for '[no test files]' in output — these packages need tests
3. Run 'go test ./... -cover' to see per-package coverage percentages
4. Identify packages below {{.Default "COVERAGE_TARGET" "75"}}% — these are your targets

PHASE 2: For each package below {{.Default "COVERAGE_TARGET" "75"}}%:

- Write tests until the package reaches {{.Default "COVERAGE_TARGET" "75"}}%
- If a package has CLI/integration code that's hard to unit test, aim for
  reasonable coverage (50-60%) and document skipped functions
- Re-run 'go test -cover ./<pkg>/...' after each batch of tests

Use table-driven tests ([]struct + t.Run) for any function with 2+ test cases.
Only create or modify _test.go files. Never edit source code.
TEST FILE NAMING: Strict 1:1 mapping — foo.go gets foo_test.go.

BUDGET: You have 200 iterations. Use Write (not Edit) for new files.
Cap 20 iterations per package. Wind down early if needed.

COVERAGE MEASUREMENT: Use 'go test -cover ./<pkg>/...' for per-package coverage.
Use 'go tool cover -func=coverage.out | tail -1' for total coverage.

A run that stops at 64% on a package without trying to reach {{.Default "COVERAGE_TARGET" "75"}}% is a FAILURE.
