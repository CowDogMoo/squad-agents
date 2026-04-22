Audit and fix all RESOURCE and CRYPTO vulnerabilities in this Go codebase.
Your scope: temp files, path traversal, weak crypto, hardcoded secrets,
HTTP client misconfig, TLS issues, unsafe code, error info leaks ONLY.
Another agent handles injection and XSS — do NOT overlap.

Start by using Glob with '**/*.go' to discover all Go source files.
Read each file (skip _test.go and vendor/).
Read go.mod for dependency info.
For files over 500 lines, use Read with offset/limit to cover the ENTIRE file.
Grep for ALL occurrences of a pattern before fixing — fix ALL instances.
Apply fixes via Edit tool, highest severity first.
Run 'go build ./...' after each batch of edits.

IMPORTANT CONSTRAINTS:

- RESOURCE/CRYPTO FOCUS ONLY — temp files, path traversal, crypto, secrets, HTTP/TLS, unsafe, error leaks
- Grep for ALL occurrences of a vulnerable pattern before fixing — fix ALL instances, not just the first
- Use consistent variable names across identical fix patterns (e.g. tmpFile everywhere, not tmpFile2)
- No new dependencies
- Skip fixes needing 50+ lines or new files
- Preserve backwards compatibility
- NEVER change functions whose behavior is asserted by tests
- Phase 1+2 MUST complete in <=4 iterations
- Produce the report before spending 60% of your cost budget
- STOP after go build + go test BOTH pass — emit report IMMEDIATELY
