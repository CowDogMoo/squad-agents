Scan all non-test Go (`.go`) and Rust (`.rs`) source files for useless, LLM-generated, and non-idiomatic comments.
Edit mode (the default): **trim** mixed blocks to keep the useful "why" portion; **leave pure single-line narration alone** unless I have explicitly asked you to scrub or delete narration in this prompt (I have NOT). Readonly mode ("readonly"/"report only"): report candidates with confidence scores instead of editing.

WORKFLOW (sequential, one file per iteration):

- Iterations 1-2: `Glob **/*.go`, then `Glob **/*.rs`, one per iteration (only the language I named, if I named one).
- Next iteration: one Bash call with the `rg` discovery searches for each language present (Search A for both; Search B for Go). Hits set PRIORITY ORDER, not the corpus.
- Then, one iteration per file: ONE `Read` per iteration; emit Edits (edit mode) or flags (readonly) for that file in the SAME iteration; narrate `Progress: K/<total> done (last: <path>, edits: M)`; advance. Never parallel-read. Never re-Read a cache-hit file.
- Final iteration: edit mode — run the build check for each language you edited (`go build ./...`, `cargo check`), then emit the structured report; readonly — emit the report.

CONSTRAINTS:

- Skip `vendor/`, `target/`, `.git/`, `.github/`, `.claude/`, `_test.go`, generated files.
- Go: never delete doc comments on exported identifiers. Rust: never delete `///` docs on `pub` items in crates with `#![deny(missing_docs)]` or `#![warn(missing_docs)]`; never touch `// SAFETY:`, `# Safety`/`# Errors`/`# Panics`/`# Examples` headers, attributes, or doctest code.
- Apply the verb-phrase test on each candidate:
  - Multi-line block with any "why"/edge-case/platform/spec/safety/algorithm content → **TRIM** to that content (NOT full-delete).
  - Single-line pure narration with no extra content → **FLAG** in `## Comments Flagged (not deleted — no explicit intent)`. Do NOT delete; this prompt did not ask for narration removal.
- LLM-generated requires 3+ tell categories.
- Comments only — never modify code, signatures, imports/`use`, `mod` declarations, attributes, or string literals.
- No Bash `find`/`grep` for discovery and no extra searches as a substitute for Reading — `rg` only, once.
- Edit mode: if zero edits, the summary must say "No changes needed".

EFFICIENCY: batch all Edits for a file in its own iteration; emit the report the iteration AFTER the last file is Read; if the iteration cap forces an early stop, report anyway with a `## Coverage Shortfall` list.

COVERAGE IS MANDATORY — read EVERY non-test, non-vendor, non-generated source file exactly once; large-codebase "sample remaining files" guidance does not apply to this agent.
