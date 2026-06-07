Audit and fix all RESOURCE and CRYPTO vulnerabilities in this Node.js/TypeScript
codebase. Your scope: path traversal, weak crypto, hardcoded secrets, SSRF,
missing TLS, ReDoS, insecure temp files, error info leaks ONLY.
Another agent handles injection, XSS, and prototype pollution — do NOT overlap.

Start by using Glob with '**/*.{js,ts,mjs,cjs}' to discover all source files.
Read each file (skip node_modules/, dist/, build/, .next/, test files).
Read package.json for dependency info.
For files over 500 lines, use Read with offset/limit to cover the ENTIRE file.
Grep for ALL occurrences of a pattern before fixing — fix ALL instances.
Apply fixes via Edit tool, highest severity first.
Run lint (eslint or tsc --noEmit) after each batch of edits.

IMPORTANT CONSTRAINTS:

- RESOURCE/CRYPTO FOCUS ONLY — path traversal, weak crypto, secrets, SSRF,
  TLS issues, ReDoS, insecure temp files, error info leaks
- Grep for ALL occurrences of a vulnerable pattern before fixing — fix ALL
  instances, not just the first
- Use consistent variable names across identical fix patterns
- No new dependencies
- Skip fixes needing 50+ lines or new files
- Preserve backwards compatibility
- NEVER change functions whose behavior is asserted by tests
- Phase 1+2 MUST complete in <=4 iterations
- Produce the report before spending 60% of your cost budget
- STOP after lint + tests BOTH pass — emit report IMMEDIATELY
