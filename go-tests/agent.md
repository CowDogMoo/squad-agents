# Orchestrator + worker

Pattern: orchestrator skill `enqueue-coverage-targets-go` + worker (you).

- **Iter 1:** `Skill("enqueue-coverage-targets-go")` — returns discovery Bash + loop.
- **Iter 2:** run that Bash verbatim (substituting your `COVERAGE_TARGET`). Queue lands at `/tmp/squad-targets.txt`.
- **Iter 3+:** drain the queue in Read/Write-Edit batches of 3–5 packages.

# No mid-run discovery

- No `go test -cover`/`-coverprofile`/`go tool cover` until the final verify pass.
- Do NOT load `Skill("score-coverage-and-report-gaps")`.
- Do NOT `Glob` the codebase — the target list is exact.
- Read `/tmp/squad-targets.txt` ONCE after iter 2.

# The loop

1. **Read batch (parallel, per package):** 1–2 source `.go` files (largest by lines) plus EVERY existing `_test.go`. Skipping the latter is how prior runs deleted thousands of lines.
2. **Write/Edit batch (parallel, per package):**
   - Existing `_test.go` covers the target → `Edit` to ADD tests (or `Write` a new `_test.go` for a different source file). Never `Write` over an existing test file.
   - No `_test.go` for the target → `Write` a new one (`foo.go` → `foo_test.go`).
   - Every symbol/import must come from a file you read this iteration.
3. Repeat until the queue is empty or you're at 80% of the cost budget.

# Critical execution rules

(See system.md for the full set; these are the ones that have failed prior runs.)

- **`_test.go` only.** Never edit source `.go`. Untestable → Skipped Functions.
- **1:1 test filename, ENFORCED.** `<X>_test.go` requires source `<X>.go` in the same package. No `run_extra_test.go`, no `service_state_test.go` (no source), no `_extra/_more/_additional/_coverage/_supplemental/_misc_test.go`. If the natural test file is full and `Edit` fails 3×, SKIP the package — do NOT invent a sibling filename.
- **`Edit` failed → re-Read, fix anchor, retry. NEVER fall back to `Write`.** 3 failed Edit attempts → skip the package.
- **Before adding a new `func Test*`, scan existing `_test.go` files in the package for the same test under a different spelling.** `TestPrintMetrics_Nil` ≠ a new test if `TestPrintMetricsNil` already exists. Functional duplicates will be rejected.
- **No contortion tests.** No field-assign-then-readback "tests" (`s := Foo{X:"y"}; if s.X != "y"`). No sentinel-existence checks (`if pkg.ErrX == nil`). No constructor echoes. No assertionless "should not panic" bodies. If the only test you can write is one of these, list the function under Skipped Functions with reason "no testable behavior."
- **Test name must match the branch the body runs.** Naming a test `_WhenBudgetExceeded` and passing a non-wrapping `fmt.Errorf("budget exceeded")` lies — `errors.Is` will return false and the test will silently cover the early-return. Wrap the real sentinel (`%w`) or rename.
- **Add NEW top-level `func Test*` — do not insert code into existing functions.** Prevents "t.Parallel called multiple times" and "no new variables on left side of :=".
- **Edit's `new_string` must NOT contain `package` or `import (...)` blocks.**
- **Symbols/import paths must come from source you read.** Don't infer from package name.
- **Validation = real exit status of `go build` / `go test`.** Failures on files YOU touched are YOURS — fix or admit, don't call them "unrelated".
- **Report = transcript.** Files Touched matches `git diff --stat`. Tests Added = `+func Test*` line count. After % from a real re-measurement or "not measured".

# OUTPUT COMPLIANCE

Coverage Report (Target/Before/After/Delta) → Discovered Gaps → Packages Tested → Tests Written → Skipped Functions → Files Touched → Validation. Quote `git diff --stat` verbatim somewhere in the report.
