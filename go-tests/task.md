Analyze this codebase's test coverage and add tests to reach 75% coverage.

PHASE 1 IS MANDATORY — even if coverage is already above 75%:
1. Run 'go test ./... -coverprofile=coverage.out -count=1' and save output
2. Check for '[no test files]' in output — these packages need tests
3. Run 'go tool cover -func=coverage.out | grep 0.0%' to find untested functions
4. Report what you found BEFORE deciding whether to write tests

If coverage is already ≥75% but packages have [no test files], you MUST:
- Create at least one test file for the highest-impact untested package
- Report all untested packages/functions in Skipped Functions table

Target: 75% total coverage.
Use table-driven tests ([]struct + t.Run) for any function with 2+ test cases.
Only create or modify _test.go files. Never edit source code.
TEST FILE NAMING: Strict 1:1 mapping — foo.go gets foo_test.go. Never create
_extra_test.go, _coverage_test.go, or any *_<suffix>_test.go variant.

BUDGET: You have 200 iterations. Use Write (not Edit) for new files.
Cap 20 iterations per package. Wind down early if needed — a partial
report with before/after numbers is better than no report.

COVERAGE MEASUREMENT: Always use 'go tool cover -func=coverage.out | tail -1'
for total coverage. Never parse coverage.out manually with awk or read it raw.
One command, one iteration.

A run that says "target already met" without analyzing gaps is a FAILURE.
