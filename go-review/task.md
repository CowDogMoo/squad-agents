Review all Go code quality issues in this codebase. Default is edit mode: fix
them in place. If the request says "readonly", "report only", "analysis
only", or "do not modify": produce a prioritized report and do NOT write or
modify any files.

Discover with Glob `**/*.go`, Read each file (skip `_test.go`, `vendor/`),
cross-reference across packages. In edit mode, apply fixes highest severity
first and run `go build ./...` after each batch.

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
