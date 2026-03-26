{{if eq .Mode "edit"}}
Review and fix all Rust code quality issues in this codebase.

Start by using Glob with '**/*.rs' to discover all Rust source files.
Read each file (skip target/).
Cross-reference between files for consistency issues.
Apply fixes via Edit tool, highest severity first.
Run 'cargo build' after each batch of edits.

IMPORTANT CONSTRAINTS (repeat from system prompt):

- No cosmetic changes (doc comments, use-statement ordering, naming style)
- No new dependencies
- Skip fixes needing 50+ lines or new files
- Preserve backwards compatibility — no API surface changes
- NEVER change functions whose behavior is asserted by tests (especially panics with #[should_panic])
- NEVER remove intentional panic!() calls — they are invariant guards, not bugs
- NEVER add unwrap()/expect() in non-test code
- Every fix must be PROPORTIONAL — no micro-optimizations for small iterators
- Flag inconsistent logging (e.g. println! when codebase uses tracing/log)
- Read each file ONCE, catalog all findings, then fix — target ≤12 iterations
- Use ONE Grep/Glob on repo root, not per-directory — minimize tool calls
- After cargo build + cargo test pass, emit report IMMEDIATELY — no post-fix exploration
- Every file touched must appear in the output report
{{end}}
{{if eq .Mode "readonly"}}
Analyze this codebase for Rust code quality issues.

Use Glob with '**/*.rs' to discover all Rust source files.
Read each file (skip target/).
Cross-reference between files for consistency issues.
Produce a prioritized report of all findings.

Do NOT write or modify any files.
{{end}}
