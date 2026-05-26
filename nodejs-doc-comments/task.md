Add or improve JSDoc comments on all exported Node.js/TypeScript declarations
in this codebase.

Start by using Glob with '**/*.{js,ts,mjs,cjs}' to discover all source files.
Read each file (skip node_modules/, dist/, build/, .next/, test files).
Catalog every exported declaration that is missing a JSDoc block or has a
deficient one. Apply fixes via Edit tool, highest priority first.
Run 'npx tsc --noEmit' after each batch of edits (TypeScript only).

IMPORTANT CONSTRAINTS (repeat from system prompt):

- ONLY modify JSDoc comments — never change code logic, signatures, or imports
- JSDoc block must be immediately before the declaration — no blank line gap
- Complete sentences with proper punctuation
- Focus on WHAT, not HOW — no implementation details
- No redundant comments ('getUser — gets the user' = skip)
- SKIP trivial wrappers: logging adapters, simple setters, delegation functions
- Key test: 'Does this comment tell the reader something the name does not?'
  If no → skip
- Boolean functions use "returns `true` if [condition]"
- Grep for 'returns true' or 'checks if' in existing comments — these are
  format violations to fix
- Proportional: simple getter = one line, trivial = NO comment
- Exported declarations only — skip unexported names
- Read each file ONCE, catalog all findings, then fix — target ≤15 iterations
- Use ONE Grep/Glob on repo root, not per-directory — minimize tool calls
- After tsc --noEmit passes, emit report IMMEDIATELY — no post-fix exploration
- Every file touched must appear in the output report
