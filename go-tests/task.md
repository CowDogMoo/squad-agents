Bring each Go package below {{.Default "COVERAGE_TARGET" "75"}}% coverage up to that target by writing tests.

Use the orchestrator-workers pattern: load `Skill("enqueue-coverage-targets-go")` on iter 1, run its discovery Bash on iter 2, then drain `/tmp/squad-targets.txt`.

# Anti-patterns that have tanked prior runs

1. **NEVER `Write` over an existing `_test.go`.** Write truncates. Read first; use `Edit` for existing files. A prior run deleted 2,524 lines this way.
2. **NEVER fall back to `Write` when `Edit` fails.** "Text not found" → re-Read, fix the anchor, retry `Edit`. After 3 failures, skip the package.
3. **NEVER invent a sibling test filename to dodge a stuck `Edit`.** `<X>_test.go` REQUIRES an existing `<X>.go` in the same package. `run_extra_test.go`, `service_state_test.go`, and any `_extra/_more/_additional/_coverage/_misc_test.go` are REJECTED — the most recent user review rejected exactly these. If the natural test file is full and `Edit` fails 3×, SKIP the package; do not invent a sibling.
4. **NEVER insert code INSIDE an existing test function.** Add a NEW top-level `func Test*` after the previous function's closing `}`. Inserting `t.Parallel()` or `dir := t.TempDir()` into another function's body causes "t.Parallel called multiple times" or "no new variables on left side of :=". See system.md §1e.
5. **NEVER include `package` or `import (...)` in your Edit's `new_string`.** The file already has them. Add new imports by editing the existing import block.
6. **NEVER invent import paths or symbol names.** Every identifier in your test must appear in a source file you actually read this iteration.
7. **NEVER write contortion tests for coverage** (user rejected in most recent review): field-assign-then-readback (`s := pkg.Foo{X:"y"}; if s.X != "y"` tests Go's struct semantics); sentinel-existence (`if pkg.ErrX == nil`); constructor echo with no transformation; functional duplicate of an existing test under a different spelling (`TestPrintMetricsNil` vs `TestPrintMetrics_Nil` — grep first); assertionless "should not panic" bodies. If those are all you can write, list the function under Skipped Functions with reason "no testable behavior."
8. **NEVER name a test after a branch the body doesn't exercise.** `TestX_WhenBudgetExceeded` with `err := fmt.Errorf("cost budget exceeded")` (no `%w` wrap of `metrics.ErrBudgetExceeded`) silently hits the early-return — `errors.Is` is false, the name lies. Wrap the real sentinel (`fmt.Errorf("...: %w", sentinel)`), pass the sentinel directly, or rename. Confirm against `errors.Is` predicates in the source you just read.

# Report = transcript, not projection

Before drafting the report, run `git diff --stat` and `git diff -U0 -- '*_test.go' | grep -E '^(\+func Test|diff --git)'`. Then:

- **Files Touched** = exact list from `git diff --stat`. If empty, "none".
- **Tests Added** = count of `+func Test*` lines per package. Modifications count 0.
- **After %** = from a fresh `go test -cover ./...` re-measurement. Otherwise "not measured" — never fabricated.
- **Validation** = real exit status of `go build` and `go test`. Failures on files YOU touched are YOURS — identify and fix, or admit explicitly. Don't call them "unrelated".
- Quote the actual `git diff --stat` output verbatim in the report.

# Constraints

- Target {{.Default "COVERAGE_TARGET" "75"}}% per package (`cmd/*` targets 50%); modify only `_test.go`; black-box `package foo_test`; table-driven for 2+ cases; strict 1:1 naming (`foo.go` → `foo_test.go`); aim for 3+ packages per Write/Edit batch.
