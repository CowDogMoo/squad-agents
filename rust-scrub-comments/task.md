Scan all Rust source files in this codebase for useless, LLM-generated, and
non-idiomatic comments and
{{if eq .Mode "edit"}}delete them{{end}}{{if eq .Mode "readonly"}}report them with confidence scores{{end}}.

First iteration: parallel `Glob **/*.rs` + pattern search for LLM vocabulary
and step/phase labels — prefer `rg --type rust -n` via Bash, fall back to
squad's `Grep` if `rg` is absent. Do NOT re-run discovery. Start reading in
iteration 2.

IMPORTANT CONSTRAINTS:

- Skip `target/`, `.git/`, `.github/`, `.claude/`, generated files
- Never delete `// SAFETY:` comments or `# Safety` sections (clippy-enforced)
- Apply verb phrase test: `// Verb the noun` above code that does it = DELETE
- LLM-generated requires 3+ tell categories to flag
- Never modify code, only comments
- Never delete code examples inside doc comments
- Do NOT re-read files. No Bash `find`/`grep` for discovery — `rg` only.
{{if eq .Mode "edit"}}
- Run `cargo check` after all deletions
- If zero edits, summary must say "No changes needed"
{{end}}

{{include "hard-rules/efficiency.md"}}

**OVERRIDE:** Comment scrubbing is a SAMPLING task. Bail out early if clean.
