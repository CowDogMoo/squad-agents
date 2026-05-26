{{if eq .Mode "edit"}}
Review and fix all Node.js/TypeScript code quality issues in this codebase.

Discover with Glob `**/*.{js,ts,mjs,cjs}`, Read each file (skip `node_modules/`,
`dist/`, `build/`, `.next/`, test files), cross-reference across modules,
apply fixes highest severity first, run `npx eslint --max-warnings=0 .` or
`npx tsc --noEmit` after each batch.

IMPORTANT CONSTRAINTS:

- No cosmetic changes (JSDoc comments, import ordering, naming style)
- No new dependencies not in package.json
- Skip fixes needing 50+ lines or new files
- Preserve backwards compatibility — no API surface changes
- NEVER swallow Promise rejections with empty handlers
- Every fix must be PROPORTIONAL
- Read each file ONCE; target ≤12 iterations
- After lint + tests pass, emit report IMMEDIATELY
- Every file touched must appear in the output report
{{end}}
{{if eq .Mode "readonly"}}
Analyze this Node.js/TypeScript codebase for code quality issues.

Discover with Glob `**/*.{js,ts,mjs,cjs}` (skip `node_modules/`, `dist/`,
`build/`, test files), Read each file, cross-reference across modules.
Produce a prioritized report.

Do NOT write or modify any files.
{{end}}
