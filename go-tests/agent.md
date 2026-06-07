# ORCHESTRATOR + WORKER

Orchestrator-workers pattern via skill `enqueue-coverage-targets-go`.

**Iter 1:** `Skill("enqueue-coverage-targets-go")` — returns a Bash discovery
command and the worker loop.
**Iter 2:** run the command verbatim (sub your target % for
`${SQUAD_COVERAGE_TARGET:-75}`). Queue → `/tmp/squad-targets.txt`.
**Iter 3+:** drain in Read/Write batches of 3–5 packages.

# CRITICAL: NO DISCOVERY

- No `go test -cover`/`-coverprofile`/`go tool cover` until final verify.
- Do NOT load `Skill("score-coverage-and-report-gaps")`.
- Do NOT `Glob` the codebase — the target list is exact.
- Read `/tmp/squad-targets.txt` ONCE after iter 2.

# THE LOOP

1. **Read batch:** parallel `Read` for 1–2 `.go` files per package (skip
   `_test.go` unless you need style hints).
2. **Write batch:** parallel `Write` for one `_test.go` per package, each
   with a real `func Test*(t *testing.T)` and meaningful assertions on
   lowest-coverage funcs. Empty stubs FORBIDDEN.
3. Repeat until queue empty or 80% of cost budget used.

# EXECUTION RULES

- **`_test.go` only.** Never edit source `.go`. Untestable without refactor
  → Skipped Functions.
- **Tests must compile and pass.** `go build ./...` + `go test ./...` once
  at end; fix only test code.
- **Verify assertions against actual behavior.** Re-read the function
  before setting `want`; contradictory tests waste the next iteration.
- **Black-box `package foo_test`** by default; `package foo` only for
  unexported with no exported caller path.
- **Naming / table style:** `foo.go` → `foo_test.go` (no `_extra_test.go`);
  table-driven for 2+ cases; `t.TempDir()` for files; no global state swap.
- **Imports complete.** `runtime.GOOS` → import `"runtime"`; missing
  imports were the #1 quality bug last run.

# OUTPUT COMPLIANCE

Final response MUST include in order: Coverage Report (Target/Before/After/
Delta), Discovered Gaps, Packages Tested, Tests Written, Skipped Functions,
Files Touched, Validation. Missing any section = failure.

# INPUT

Orchestrator instructions and the target list path.
