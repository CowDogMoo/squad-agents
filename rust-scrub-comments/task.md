Scan all Rust source files in this codebase for useless, LLM-generated, and
non-idiomatic comments and
{{if eq .Mode "edit"}}delete them{{end}}{{if eq .Mode "readonly"}}report them with confidence scores{{end}}.

In your FIRST iteration, make these parallel calls:

1. `Glob **/*.rs` to discover all Rust source files
2. `Grep` pattern `(crucial|leverage|seamless|robust|Moreover|Furthermore|Additionally|streamlined|meticulous|intricate)` across `**/*.rs` to find priority files

Do NOT call Glob or Grep again after iteration 1. Do NOT use Bash for file
discovery (no find, grep, wc). Start reading files in iteration 2.

THE 5 DELETION CATEGORIES:

1. **States the obvious** — restates the code (e.g., `/// Returns the name` on
   `fn name()`, `// increment counter` above `counter += 1`). INCLUDES inline
   comments that narrate the next line: `// Generate ID` above `let id = Uuid::new_v4()`,
   `// Load state` above `let state = load_state().await?`
2. **LLM-generated** — exhibits 3+ LLM tell categories (e.g., "crucial,"
   "leverage," "Moreover," "This function provides a robust mechanism")
3. **Adds nothing useful** — filler (e.g., "A struct that holds data,"
   "Handles the logic," "Performs the necessary processing")
4. **Non-idiomatic Rust** — doc comments on private items, `//` on pub items
   instead of `///`, implementation-detail docs on public API
5. **Visual noise** — section dividers (`// --- Configuration ---`,
   `// ========================`), decorative separators, numbered step labels
   (`// Step 2: Load state`), and phase labels (`// Phase 1`, `// Phase 2`)
   where the code is self-explanatory

WHAT TO KEEP:

- Comments that explain "why" — rationale, trade-offs, history
- Non-obvious behavior — edge cases, panics, error conditions
- Safety information — `// SAFETY:`, `# Safety` sections
- Convention markers — `// TODO`, `// FIXME`, `// HACK`, `// XXX`, `// NOTE`
- Public API contracts with real information
- `# Errors`/`# Panics` sections with actual descriptions
- Code examples in doc comments
- Complex algorithm explanations
- External references (links, RFCs, issue numbers)
- License/copyright headers

{{if eq .Mode "edit"}}
DELETION RULES:

- Delete entire comment blocks that are entirely useless
- Trim mixed blocks — keep useful parts, delete useless parts
- Clean up whitespace (no double blank lines after deletion)
- Never modify code, only comments
- Never delete code examples inside doc comments
- Run `cargo check 2>&1` after all deletions
- If in doubt, keep the comment
{{end}}

ABSOLUTE PROHIBITIONS:

- Do NOT delete comments that explain "why"
- Do NOT delete safety-related comments
- Do NOT delete convention markers (TODO, FIXME, SAFETY, etc.)
- Do NOT delete code examples inside doc comments
- Do NOT modify code, signatures, attributes, or macros
- Do NOT flag LLM-generated comments with fewer than 3 tell categories
- Do NOT touch files in `target/`, `.git/`, `.github/`, `.claude/`
- Do NOT re-read files after editing — trust Edit output
- Do NOT make additional tool calls after emitting the report

{{include "hard-rules/efficiency.md"}}

Phase allocation:

- Phase 1 (1 iter): Glob + Grep in PARALLEL. Count files. Determine budget tier.
  Reference is already in your system prompt — do NOT Read it.
  Do NOT call Glob or Grep again. Do NOT use Bash for discovery.
- Phase 2 (varies): SINGLE-FILE READ-THEN-EDIT LOOP. Each iteration you MUST:
  (a) Read ONE file (one Read call)
  (b) Analyze comments — decide what to delete
  (c) Make ALL Edit calls for that file IN THE SAME RESPONSE
  YOU MUST MAKE EDIT CALLS. If a file has useless comments and you don't
  call Edit, you have FAILED. Read ONE file, edit it, read the next.
  Do NOT batch-read multiple files.
  Start with Grep-hit files. Spread across ALL crates.
  START READING IN ITERATION 2 — no planning iterations.
{{if eq .Mode "edit"}}
- Phase 3 (1 iter): `cargo check`, then emit report in SAME response, NO more iterations
{{end}}
{{if eq .Mode "readonly"}}
- Phase 3 (1 iter): Emit report in SAME response as final analysis, NO more iterations
{{end}}

ITERATION BUDGET:

- Small (≤20 files): 8 iterations max (readonly), 12 max (edit)
- Medium (21-50 files): 12 iterations max (readonly), 20 max (edit)
- Large (50+ files): 18 iterations max (readonly), 25 max (edit)

For large codebases: you CANNOT read every file. Prioritize Grep-hit files,
entry points (main.rs, lib.rs), and public API modules. Spread reads across
ALL crates — do NOT get stuck reading only one crate. Document what was
sampled vs skipped.

CRITICAL ANTI-PATTERN — RE-READING FILES:

Context compaction will erase files you read earlier. This causes models to
re-read those files, wasting iterations and budget. The fix: EDIT IMMEDIATELY
after reading. Never accumulate a backlog of reads. If you feel the urge to
re-read a file, STOP — you already analyzed it. Move to unread files.

FORBIDDEN PATTERNS (these waste iterations):

- Calling Glob more than once
- Using Bash to run find, grep, wc, or any discovery command
- Spending an iteration "planning" without reading files
- Re-running Grep after Phase 1
- Reading the same file twice — EVER
- Reading files without editing them in the same iteration (edit mode)
- Getting stuck in one crate instead of spreading across the codebase

AGENT-SPECIFIC REQUIREMENTS:

- Every file scanned OR skipped must appear in the output report
- Context check before every deletion: does it explain "why"?
{{if eq .Mode "edit"}}
- `cargo check` must PASS before report is emitted
{{end}}
