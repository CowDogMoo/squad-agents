Scan all Go source files in this codebase for useless, LLM-generated, and
non-idiomatic comments and
{{if eq .Mode "edit"}}**trim** mixed blocks to keep the useful "why" portion; **leave pure single-line narration alone** unless I have explicitly asked you to scrub or delete narration in this prompt (I have NOT){{end}}{{if eq .Mode "readonly"}}report them with confidence scores{{end}}.

First iteration: parallel `Glob **/*.go` + Search A (LLM-vocabulary regex)
and Search B (PCRE2 structural-narration regex with method-receiver support)
— prefer `rg --type go` via Bash, fall back to squad's `Grep` if `rg` is
absent. Do NOT re-run discovery. Start reading in iteration 2.

IMPORTANT CONSTRAINTS:

- Skip `vendor/`, `.git/`, `.github/`, `.claude/`, `_test.go`, generated files
- NEVER delete doc comments on exported identifiers (required by `golint`/`go vet`)
- Apply the verb phrase test on each candidate:
  - Multi-line block with any "why"/edge-case/platform/spec/algorithm content → **TRIM** to that content (NOT full-delete)
  - Single-line pure narration with no extra content → **FLAG** in `## Comments Flagged (not deleted — no explicit intent)`. Do NOT delete; this prompt did not ask for narration removal.
- LLM-generated requires 3+ tell categories to flag
- Never modify code, only comments
- Do NOT re-read files. No Bash `find`/`grep` for discovery — `rg` only.
{{if eq .Mode "edit"}}
- Run `go build ./...` after any edits
- If zero edits, summary must say "No changes needed"
{{end}}
