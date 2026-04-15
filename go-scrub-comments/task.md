Scan all Go source files in this codebase for useless, LLM-generated, and
non-idiomatic comments and
{{if eq .Mode "edit"}}delete them{{end}}{{if eq .Mode "readonly"}}report them with confidence scores{{end}}.

In your FIRST iteration, make these parallel calls:

1. `Glob **/*.go` to discover all Go source files
2. `Grep` pattern `(crucial|leverage|seamless|robust|Moreover|Furthermore|Additionally|streamlined|meticulous|intricate|comprehensive|pivotal|noteworthy|facilitate|underscore|Step \d|Phase \d)` across `**/*.go` to find priority files (LLM vocabulary AND numbered step/phase labels)

Do NOT call Glob or Grep again after iteration 1. Do NOT use Bash for file
discovery (no find, grep, wc). Start reading files in iteration 2.

FILE FILTERING:

- Skip `vendor/`, `.git/`, `.github/`, `.claude/` directories
- Skip `_test.go` files — test comments have different conventions
- Skip files with `// Code generated ... DO NOT EDIT.` header
- Skip `//go:generate`, `//go:build`, `//go:embed`, `//nolint` directives

THE 5 DELETION CATEGORIES:

1. **States the obvious** — restates the code. ALWAYS delete these patterns:
   `// NewFoo creates a new Foo`, `// SetX sets X`, `// GetX returns X`,
   `// FooManager manages Foo`, `// FooConfig contains config for Foo`.
   These are NOT "standard Go doc convention" — they are restatements.
   Also delete inline narration: `// Generate ID` above `id := uuid.New()`,
   `// Skip terminated instances`, `// Build the tarball`, `// Capture stdout`,
   `// Marshal to pretty JSON`, `// Ensure output directory exists`,
   `// Required flags`, `// Optional flags`, `// Register shell completions`,
   `// Write schema file`. "Aids scanning" is NOT a reason to keep narration.
2. **LLM-generated** — exhibits 3+ LLM tell categories (e.g., "crucial,"
   "leverage," "Moreover," "This function provides a robust mechanism")
3. **Adds nothing useful** — filler (e.g., "Config is a struct that holds data,"
   "handleLogic handles the logic," "Process performs the necessary processing")
4. **Non-idiomatic Go** — doc comment doesn't start with declared name, blank
   line between comment and declaration, `returns true if` instead of `reports
   whether`, implementation-detail docs, doc comments on unexported functions
5. **Visual noise** — section dividers (`// --- Configuration ---`,
   `// ========================`), decorative separators, numbered step labels
   (`// Step 1:`, `// Step 2:`, `// Step N/M:`, `// Step N of M:`), phase
   labels (`// Phase 1:`, `// Phase 2:`, `// Phase N —`), and section labels
   (`// Check directory structure`, `// Validate env.hcl content`,
   `// Build a set of live instance IDs from AWS.`). ALL variants of numbered
   step/phase labels are deletions — they are a strong LLM structural tell.
   Do NOT touch format strings that show step numbers to users (those are
   code, not comments).

WHAT TO KEEP:

- Comments that explain "why" — rationale, trade-offs, history
- Non-obvious behavior — edge cases, panics, error conditions
- Concurrency safety notes ("safe for concurrent use")
- Convention markers — `// TODO`, `// FIXME`, `// HACK`, `// XXX`, `// NOTE`
- Go directives — `//go:generate`, `//go:build`, `//go:embed`, `//nolint`
- Public API contracts with real information
- Error return documentation
- Code examples
- Complex algorithm explanations
- External references (links, RFCs, issue numbers)
- License/copyright headers
- Package comments (unless pure LLM filler)

{{if eq .Mode "edit"}}
DELETION RULES:

- Delete entire comment blocks that are entirely useless
- Trim mixed blocks — keep useful parts, delete useless parts
- Fix blank-line gaps between doc comments and declarations
- Clean up whitespace (no double blank lines after deletion)
- Never modify code, only comments
- Run `go build ./... 2>&1` after all deletions
- If in doubt, keep the comment
{{end}}

ABSOLUTE PROHIBITIONS:

- Do NOT delete comments that explain "why"
- Do NOT delete concurrency safety notes
- Do NOT delete convention markers (TODO, FIXME, etc.)
- Do NOT delete Go directives (//go:generate, //go:build, //nolint, etc.)
- Do NOT modify code, signatures, imports, or var/const blocks
- Do NOT flag LLM-generated comments with fewer than 3 tell categories
- Do NOT touch files in `vendor/`, `.git/`, `.github/`, `.claude/`
- Do NOT touch `_test.go` files or generated files
- Do NOT re-read files after editing — trust Edit output
- Do NOT make additional tool calls after emitting the report

{{include "hard-rules/efficiency.md"}}

**OVERRIDE — Coverage vs Efficiency for scrub-comments agents:**
The efficiency.md rule "Coverage is mandatory" does NOT apply to this agent.
Comment scrubbing is a SAMPLING task. If the first 6-8 files are clean and Grep
found no LLM vocabulary in comments, the codebase is clean. BAIL OUT early.

Phase allocation:

- Phase 1 (1 iter): Glob + Grep in PARALLEL. Count files. Determine budget tier.
  Reference is already in your system prompt — do NOT Read it.
  Do NOT call Glob or Grep again. Do NOT use Bash for discovery.
- Phase 2 (varies): READ-THEN-EDIT LOOP.
  DEFAULT: Read 3-4 files per iteration. Only drop to single-file reads when
  making edits (to prevent context compaction erasing analysis).
  For each iteration: Read file(s) → Analyze → Edit if needed → move on.
  YOU MUST MAKE EDIT CALLS if a file has useless comments.
  Start with Grep-hit files.
  START READING IN ITERATION 2 — no planning iterations.

  NO EARLY BAIL-OUT in edit mode. Narration doesn't trigger Grep — Grep
  finding nothing does NOT mean clean. Read LARGEST files first (not
  main.go/doc.go). Keep reading until budget runs out.
{{if eq .Mode "edit"}}
- Phase 3 (1 iter): `go build ./...`, then emit report in SAME response, NO more iterations
{{end}}
{{if eq .Mode "readonly"}}
- Phase 3 (1 iter): Emit report in SAME response as final analysis, NO more iterations
{{end}}

ITERATION BUDGET:

- Small (≤20 files): 8 iterations max (readonly), 12 max (edit)
- Medium (21-50 files): 12 iterations max (readonly), 20 max (edit)
- Large (50+ files): 18 iterations max (readonly), 25 max (edit)

For large codebases: you CANNOT read every file. Prioritize Grep-hit files,
entry points (main.go, package-level files), and exported API files. Document
what was sampled vs skipped.

CRITICAL ANTI-PATTERN — RE-READING FILES:

Context compaction will erase files you read earlier. This causes models to
re-read those files, wasting iterations and budget. The fix: EDIT IMMEDIATELY
after reading. Never accumulate a backlog of reads. If you feel the urge to
re-read a file, STOP — you already analyzed it. Move to unread files.

OUTPUT VALIDATION:

If you make ZERO edits (the codebase is clean), your Summary section MUST include
the phrase "No changes needed" or "No changes applied". This is required for
the harness to accept your output.

FORBIDDEN PATTERNS (these waste iterations):

- Calling Glob more than once
- Using Bash to run find, grep, wc, or any discovery command
- Spending an iteration "planning" without reading files
- Re-running Grep after Phase 1
- Reading the same file twice — EVER
- Reading only ONE file per iteration when NOT making edits (batch 3-4)
- Reading MORE than 5 consecutive clean files without bailing out to Phase 3

AGENT-SPECIFIC REQUIREMENTS:

- Every file scanned OR skipped must appear in the output report
- Context check before every deletion: does it explain "why"?
{{if eq .Mode "edit"}}
- `go build ./...` must PASS before report is emitted
{{end}}
