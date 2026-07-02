Bring each Go package below 75% coverage (or the caller's stated target) up to that target by writing tests. Use the orchestrator-workers pattern: load `Skill("enqueue-coverage-targets-go")` on iter 1, run its discovery Bash on iter 2, then drain `/tmp/squad-targets.txt`.

# READ THIS FIRST — past failures (fixes are in anti-patterns 10–13)

Run 1 (target 92%): 200 iters, +0.1%, destroyed 6 tests in `routine/catchup_test.go` via renames, ignored queue, fabricated "improved" in After. Run 3 (target 95%): 200 iters, +0.0%, burned 67 iter/pkg on 3 of 20 queue packages, broke scaffold with `TestStoreFindByID2` _2-suffix duplicates and `AgentsDir` used on `CreatePipelineOptions` (it belongs to `CreateAgentOptions`).

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
10. **ONLY work on packages in `/tmp/squad-targets.txt`.** Packages not in the queue are at or above target — touching them is wasted iterations. **Mechanical targeting:** for each queue package `<pkg>`, run `grep <pkg> /tmp/squad-funcs.out | sort -k3 -n | head -8` BEFORE writing tests; test only the FIRST 3-5 listed functions (lowest coverage). Run 8 added tests in 7 packages with ZERO coverage delta — picked by feel, not by this list.
11. **Per-package iteration cap: 8.** Spent 8 iters on one package without moving on → STOP, list untested functions under Skipped Functions, MOVE TO THE NEXT QUEUE PACKAGE. Run 3 burned ~67 iter/pkg on 3 packages and skipped 17 others.
12. **NEVER append `_2`/`_3`/`Extra`/`Alt`/`New` to dodge a duplicate-function build error.** A "duplicate Test* declaration" compiler error is a SIGNAL you're writing a functional duplicate — SKIP. AND verify struct fields exist on the EXACT struct you're instantiating (similar-named adjacent structs share SOME fields but not all — `CreateAgentOptions.AgentsDir` ≠ `CreatePipelineOptions.OutputDir`).
13. **NEVER edit a test you did not write to silence a final-verify failure.** If `go test ./...` fails in a package `git diff --stat` shows you did NOT touch (always true when the queue was empty), the failure is pre-existing or flaky — NOT yours. Re-run it alone: `go test -run <TestName> ./<pkg>/`. Passes in isolation → flaky timeout under parallel load; report it under Validation and STOP. A run neutered a leak-detection test by wrapping its command in `SQUAD_SKILL_DIR= bash -c '...'` to make a flake go away — that destroys what the test asserts. Never make a test pass by gutting its assertion. See system.md §2a.

# Report = transcript, not projection

Run `git diff --stat` and `git diff -U0 -- '*_test.go' | grep -E '^(\+func Test|diff --git)'` before drafting. Then: **Files Touched** = `git diff --stat` (verbatim, quoted); **Tests Added** = count of `+func Test*` per package; **After %** = real `go test -cover ./...` re-measurement, or literal "not measured" — NEVER "improved"/"partial"/"<92%"/prose; **Validation** = real exit status; failures on files YOU touched are YOURS to fix — failures on files you did NOT touch are pre-existing/flaky, reported (re-run in isolation first) but NEVER edited.

# Constraints

Target 75% per package unless the caller specifies otherwise, including `cmd/*` (no carve-outs); only `_test.go`; black-box `package foo_test`; table-driven for 2+ cases; 1:1 naming (`foo.go` → `foo_test.go`); 3+ packages per Write/Edit batch. Iteration target ≤ `2 × queue_size + 5`; reserve the last 5 iters for verify+report.
