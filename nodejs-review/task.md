Review all Node.js/TypeScript code quality issues in this codebase. Default
is edit mode: fix them in place. If the request says "readonly", "report
only", "analysis only", or "do not modify": produce a prioritized report and
do NOT write or modify any files.

Discover with Glob `**/*.{js,ts,mjs,cjs}`, Read each file (skip
`node_modules/`, `dist/`, `build/`, `.next/`, test files), cross-reference
across modules. In edit mode, apply fixes highest severity first and run
`npx eslint --max-warnings=0 .` or `npx tsc --noEmit` after each batch.

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
