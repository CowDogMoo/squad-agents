Scan all non-test Go source files for useless, LLM-generated, and non-idiomatic comments and {{if eq .Mode "edit"}}delete them{{end}}{{if eq .Mode "readonly"}}report them with confidence scores{{end}}.

WORKFLOW (sequential, one file per iteration):

- Iteration 1: `Glob **/*.go`.
- Iteration 2: Bash `rg --type go -n '(crucial|leverage|seamless|robust|Moreover|Furthermore|Additionally|streamlined|meticulous|intricate|comprehensive|pivotal|noteworthy|facilitate|underscore|Step \d|Phase \d)' .`. Separate from Glob.
- Iterations 3..N: ONE `Read` per iteration; emit Edits for that file in the SAME iteration; narrate `Progress: K/<total> done (last: <path>, edits: M)`; advance. NEVER parallel-read. NEVER re-Read a cache-hit file.
- Iteration N+1: `go build ./... 2>&1`, then emit the structured report.

CONSTRAINTS:

- Skip `vendor/`, `.git/`, `.github/`, `.claude/`, `_test.go`, generated files.
- NEVER delete doc comments on exported identifiers (`golint`/`go vet`/`godoc` require them).
- Verb-phrase test: `// Verb the noun` above code that does it = DELETE.
- LLM-generated requires 3+ tell categories.
- Comments only — never modify code, signatures, imports, var/const, or string literals.
- Cache-hit responses mean "already in context, move on."
- Do NOT use additional `rg`/`Bash` searches as a substitute for Reading files.
{{if eq .Mode "edit"}}
- Run `go build ./...` after all deletions. If zero edits, summary must say "No changes needed".
{{end}}

{{include "hard-rules/efficiency.md"}}

COVERAGE IS MANDATORY — full coverage, no sampling. Read EVERY non-test, non-vendor, non-generated `.go` file exactly once. The Large-tier "sample" guidance from efficiency.md does NOT apply to this agent.
