{{if eq .Mode "edit"}}
Review and fix all Rust code quality issues in this codebase.

Discover with Glob `**/*.rs`, Read each file (skip `target/`),
cross-reference across modules, apply fixes highest severity first,
run `cargo build` after each batch.

IMPORTANT CONSTRAINTS:

- No cosmetic changes (doc comments, use-statement ordering, naming style)
- No new deps (except community-standard: log, env_logger, tracing)
- Skip fixes needing 50+ lines or new files; preserve backwards compatibility
- NEVER change test-asserted behavior (#[should_panic]) or remove intentional panics
- NEVER add unwrap()/expect() in non-test code
- Every fix must be PROPORTIONAL; flag inconsistent logging
- Read each file ONCE; verify API exists before edits; batch edits per file
- After cargo build + cargo test pass, emit report IMMEDIATELY
{{end}}
{{if eq .Mode "readonly"}}
Analyze this Rust codebase for code quality issues.

Discover with Glob `**/*.rs` (skip `target/`), Read each file,
cross-reference across modules. Produce a prioritized report.

Do NOT write or modify any files.
{{end}}
