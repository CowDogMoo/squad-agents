{{if eq .Mode "edit"}}
Review and fix all Go code quality issues in this codebase.

Discover with Glob `**/*.go`, Read each file (skip `_test.go`, `vendor/`),
cross-reference across packages, apply fixes highest severity first,
run `go build ./...` after each batch.

IMPORTANT CONSTRAINTS:

- No cosmetic changes (doc comments, import ordering, naming style)
- No new dependencies not in go.mod
- Skip fixes needing 50+ lines or new files
- Preserve backwards compatibility — no API surface changes
- NEVER change test-asserted behavior (wantPanic/recover)
- NEVER remove intentional panic() precondition guards
- Every fix must be PROPORTIONAL
- Flag inconsistent logging imports
- Read each file ONCE; target ≤12 iterations
- After go build + go test pass, emit report IMMEDIATELY
- Every file touched must appear in the output report
{{end}}
{{if eq .Mode "readonly"}}
Analyze this Go codebase for code quality issues.

Discover with Glob `**/*.go` (skip `_test.go`, `vendor/`), Read each file,
cross-reference across packages. Produce a prioritized report.

Do NOT write or modify any files.
{{end}}
