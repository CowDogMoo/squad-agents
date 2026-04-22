Audit and fix all INJECTION vulnerabilities in this Go codebase.
Your scope: command injection, SQL injection, XSS, input validation ONLY.
Another agent handles crypto, temp files, resource management — do NOT overlap.

Start by using Glob with '**/*.go' to discover all Go source files.
Read each file (skip _test.go and vendor/).
Read go.mod for dependency info.
For files over 500 lines, use Read with offset/limit to cover the ENTIRE file.
Apply fixes via Edit tool, highest severity first.
Run 'go build ./...' after each batch of edits.

IMPORTANT CONSTRAINTS:

- INJECTION FOCUS ONLY — command injection, SQL injection, XSS, input validation
- Trace the FULL CALL CHAIN before fixing — if the consumer re-parses (e.g. Shlex), use the right API
- Grep for ALL occurrences of a pattern before fixing — fix ALL instances
- No new dependencies
- Skip fixes needing 50+ lines or new files
- Preserve backwards compatibility
- NEVER change functions whose behavior is asserted by tests
- Every fix must be PROPORTIONAL
- Phase 1+2 MUST complete in <=4 iterations
- Produce the report before spending 60% of your cost budget
- STOP after go build + go test BOTH pass — emit report IMMEDIATELY
