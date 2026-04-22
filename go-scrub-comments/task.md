Scan all Go source files in this codebase for useless, LLM-generated, and
non-idiomatic comments and
{{if eq .Mode "edit"}}delete them{{end}}{{if eq .Mode "readonly"}}report them with confidence scores{{end}}.

First iteration: parallel `Glob **/*.go` + `Grep` for LLM vocabulary and
step/phase labels. Do NOT call Glob/Grep again. Start reading in iteration 2.

IMPORTANT CONSTRAINTS:

- Skip `vendor/`, `.git/`, `.github/`, `.claude/`, `_test.go`, generated files
- NEVER delete doc comments on exported identifiers (required by `golint`/`go vet`)
- Apply verb phrase test: `// Verb the noun` above code that does it = DELETE
- LLM-generated requires 3+ tell categories to flag
- Never modify code, only comments
- Do NOT re-read files or use Bash for discovery
{{if eq .Mode "edit"}}
- Run `go build ./...` after all deletions
- If zero edits, summary must say "No changes needed"
{{end}}

{{include "hard-rules/efficiency.md"}}

**OVERRIDE:** Comment scrubbing is a SAMPLING task. Bail out early if clean.
