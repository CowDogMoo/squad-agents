Bring each Go package below {{.Default "COVERAGE_TARGET" "75"}}% coverage up to that target by writing tests.

Use the orchestrator-workers pattern: load `Skill("enqueue-coverage-targets-go")` on iter 1, run its discovery Bash on iter 2, then drain `/tmp/squad-targets.txt`.

# READ THIS FIRST — last run failed these ways

200 iters, 91.7%→91.8%, destroyed 6 tests in `routine/catchup_test.go` via renames, ignored queue (wrote to `agent` 97.5%, `metrics` 93%, `tools` 91.6%), skipped `routine/service` 72.2%, fabricated "improved"/"<92%"/"partial" in the After column. Fixes are in the anti-patterns below.

# Anti-patterns that have tanked prior runs

1. **NEVER `Write` over an existing `_test.go`.** Read first; use `Edit` for existing files. A prior run deleted 2,524 lines this way.
2. **NEVER fall back to `Write` when `Edit` fails.** "Text not found" → re-Read, fix the anchor, retry `Edit`. After 3 failures, skip the package.
3. **NEVER invent a sibling test filename to dodge a stuck `Edit`.** `<X>_test.go` REQUIRES an existing `<X>.go` in the same package. `_extra/_more/_additional/_coverage/_misc_test.go` are REJECTED. If `Edit` fails 3×, SKIP the package.
4. **NEVER insert code INSIDE an existing test function.** Add a NEW top-level `func Test*` after the previous function's `}`. Inserting `t.Parallel()` or `dir := t.TempDir()` causes "t.Parallel called multiple times" or "no new variables on left side of :=". See system.md §1e.
5. **NEVER include `package` or `import (...)` in your Edit's `new_string`.** Add new imports by editing the existing import block.
6. **NEVER invent import paths or symbol names.** Every identifier in your test must appear in a source file you read this iteration.
7. **NEVER write contortion tests for coverage**: field-assign-then-readback; sentinel-existence; constructor echo with no transformation; functional duplicate of an existing test under a different spelling (`TestPrintMetricsNil` vs `TestPrintMetrics_Nil` — grep first); assertionless "should not panic" bodies. Skip with "no testable behavior" if those are all you can write.
8. **NEVER name a test after a branch the body doesn't exercise.** `errors.Is` on a non-wrapping `fmt.Errorf` hits early-return; the name lies. Wrap the sentinel with `%w`, pass it directly, or rename.
9. **NEVER rename or replace existing `func Test*`.** Renaming is destruction (functional duplicate under a new spelling). A `-func Test*` line in your diff is a fail. If a test name bothers you, leave it.
10. **ONLY work on packages in `/tmp/squad-targets.txt`.** Packages not in the queue are at or above target — touching them is wasted iterations. Use `/tmp/squad-funcs.out` to pick the LOWEST-coverage functions in each queue package.

# Report = transcript, not projection

Run `git diff --stat` and `git diff -U0 -- '*_test.go' | grep -E '^(\+func Test|diff --git)'` before drafting. Then: **Files Touched** = `git diff --stat` (verbatim, quoted); **Tests Added** = count of `+func Test*` per package; **After %** = real `go test -cover ./...` re-measurement, or literal "not measured" — NEVER "improved"/"partial"/"<92%"/prose; **Validation** = real exit status; failures on files YOU touched are YOURS.

# Constraints

Target {{.Default "COVERAGE_TARGET" "75"}}% per package, including `cmd/*` (no carve-outs); only `_test.go`; black-box `package foo_test`; table-driven for 2+ cases; 1:1 naming (`foo.go` → `foo_test.go`); 3+ packages per Write/Edit batch. Iteration target ≤ `2 × queue_size + 5`; reserve the last 5 iters for verify+report.
