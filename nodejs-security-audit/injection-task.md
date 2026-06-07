Audit and fix all INJECTION vulnerabilities in this Node.js/TypeScript codebase.
Your scope: command injection, SQL injection, XSS, prototype pollution, input
validation ONLY. Another agent handles crypto, secrets, path traversal, and
resource management — do NOT overlap.

Start by using Glob with '**/*.{js,ts,mjs,cjs}' to discover all source files.
Read each file (skip node_modules/, dist/, build/, .next/, test files).
Read package.json for dependency info.
For files over 500 lines, use Read with offset/limit to cover the ENTIRE file.
Apply fixes via Edit tool, highest severity first.
Run lint (eslint or tsc --noEmit) after each batch of edits.

IMPORTANT CONSTRAINTS:

- INJECTION FOCUS ONLY — command injection, SQL injection, XSS, prototype
  pollution, input validation
- Trace the FULL CALL CHAIN before fixing — if downstream re-joins args, use
  the right API
- Grep for ALL occurrences of a pattern before fixing — fix ALL instances
- No new dependencies
- Skip fixes needing 50+ lines or new files
- Preserve backwards compatibility
- NEVER change functions whose behavior is asserted by tests
- Every fix must be PROPORTIONAL
- Phase 1+2 MUST complete in <=4 iterations
- Produce the report before spending 60% of your cost budget
- STOP after lint + tests BOTH pass — emit report IMMEDIATELY
