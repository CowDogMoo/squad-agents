Review all Rust code quality issues in this codebase. Default: fix them in
place. If the request says "readonly"/"report only": analyze only, produce a
prioritized report, and do NOT write or modify any files.

Discover with Glob `**/*.rs`, Read each file (skip `target/`),
cross-reference across modules. In edit mode apply fixes highest severity
first and run `cargo build` after each batch.

IMPORTANT CONSTRAINTS:

- No cosmetic changes (doc comments, use-statement ordering, naming style)
- No new deps (except community-standard: log, env_logger, tracing)
- Skip fixes needing 50+ lines or new files; preserve backwards compatibility
- NEVER change test-asserted behavior (#[should_panic]) or remove intentional panics
- NEVER add unwrap()/expect() in non-test code
- Every fix must be PROPORTIONAL; flag inconsistent logging
- Read each file ONCE; verify API exists before edits; batch edits per file
- After cargo build + cargo test pass, emit report IMMEDIATELY
