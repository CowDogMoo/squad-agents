Bring each Go package below {{.Default "COVERAGE_TARGET" "75"}}% coverage up to that target by writing tests.

Use the orchestrator-workers pattern: load `Skill("enqueue-coverage-targets-go")` on iter 1, run its discovery Bash on iter 2, then drain `/tmp/squad-targets.txt`.

# Anti-patterns that have tanked prior runs

1. **NEVER `Write` over an existing `_test.go`.** Write truncates. Read first; use `Edit` for existing files. A prior run deleted 2,524 lines this way.
2. **NEVER fall back to `Write` when `Edit` fails.** "Text not found" → re-Read, fix the anchor, retry `Edit`. After 3 failures, skip the package.
3. **NEVER insert code INSIDE an existing test function.** Add a NEW top-level `func Test*` after the previous function's closing `}`. Inserting `t.Parallel()` or `dir := t.TempDir()` into another function's body causes "t.Parallel called multiple times" or "no new variables on left side of :=". See system.md §1e for the hard Edit-anchor rule.
4. **NEVER include `package` or `import (...)` in your Edit's `new_string`.** The file already has them. Add new imports by editing the existing import block.
5. **NEVER invent import paths or symbol names.** Every identifier in your test must appear in a source file you actually read this iteration.

# Report = transcript, not projection

Before drafting the report, run `git diff --stat` and `git diff -U0 -- '*_test.go' | grep -E '^(\+func Test|diff --git)'`. Then:

- **Files Touched** = exact list from `git diff --stat`. If empty, "none".
- **Tests Added** = count of `+func Test*` lines per package. Modifications count 0.
- **After %** = from a fresh `go test -cover ./...` re-measurement. Otherwise "not measured" — never fabricated.
- **Validation** = real exit status of `go build` and `go test`. Failures on files YOU touched are YOURS — identify and fix, or admit explicitly. Don't call them "unrelated".
- Quote the actual `git diff --stat` output verbatim in the report.

# Constraints

- Target {{.Default "COVERAGE_TARGET" "75"}}% per package (`cmd/*` targets 50%)
- Modify only `_test.go` files — never source
- Black-box `package foo_test`; table-driven for 2+ cases; 1:1 naming (`foo.go` → `foo_test.go`)
- Aim for 3+ packages per Write/Edit batch
