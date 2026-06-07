Analyze this codebase's test coverage and bring each package to {{.Default "COVERAGE_TARGET" "75"}}% coverage.

Discover all Go source files, measure baseline coverage, then write tests for
each package below target. Use `go test -cover ./<pkg>/...` for per-package
coverage and `go tool cover -func=coverage.out | tail -1` for total.

IMPORTANT CONSTRAINTS:

- Target is {{.Default "COVERAGE_TARGET" "75"}}% PER PACKAGE, not just overall
- CLI/Cobra packages (cmd/*): aim for 50-60%, document untestable functions
- Only create/modify `_test.go` files — never edit source code
- Table-driven tests (`[]struct` + `t.Run`) for 2+ test cases
- Strict 1:1 naming: `foo.go` -> `foo_test.go`
- Use Write (not Edit) for new test files
- Budget: 200 iterations max, 20 per package. Wind down early if needed
- Phase 1 is MANDATORY — always run gap analysis even if above target
