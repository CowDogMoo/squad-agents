Scan all non-test Go source files for useless, LLM-generated, and non-idiomatic comments.
Edit mode (the default): **trim** mixed blocks to keep the useful "why" portion; **leave pure single-line narration alone** unless I have explicitly asked you to scrub or delete narration in this prompt (I have NOT). Readonly mode ("readonly"/"report only"): report candidates with confidence scores instead of editing.

WORKFLOW (sequential, one file per iteration):

- Iteration 1: `Glob **/*.go`.
- Iteration 2: Bash runs BOTH `rg --type go` discovery searches in a single call — Search A (LLM-vocabulary regex `(crucial|leverage|seamless|robust|Moreover|Furthermore|Additionally|streamlined|meticulous|intricate|comprehensive|pivotal|noteworthy|facilitate|underscore|Step \d|Phase \d)`) and Search B (PCRE2 structural-narration regex with method-receiver support, needs `--pcre2 -U`). Separate from Glob. Hits define PRIORITY ORDER (Search B first, then Search A, then remaining files); they do NOT define the corpus.
- Iterations 3..N: ONE `Read` per iteration; emit Edits (edit mode) or flags (readonly) for that file in the SAME iteration; narrate `Progress: K/<total> done (last: <path>, edits: M)`; advance. NEVER parallel-read. NEVER re-Read a cache-hit file.
- Iteration N+1: edit mode — `go build ./... 2>&1`, then emit the structured report; readonly — emit the report.

CONSTRAINTS:

- Skip `vendor/`, `.git/`, `.github/`, `.claude/`, `_test.go`, generated files.
- NEVER delete doc comments on exported identifiers (`golint`/`go vet`/`godoc` require them).
- Apply the verb-phrase test on each candidate:
  - Multi-line block with any "why"/edge-case/platform/spec/algorithm content → **TRIM** to that content (NOT full-delete).
  - Single-line pure narration with no extra content → **FLAG** in `## Comments Flagged (not deleted — no explicit intent)`. Do NOT delete; this prompt did not ask for narration removal.
- LLM-generated requires 3+ tell categories.
- Comments only — never modify code, signatures, imports, var/const, or string literals.
- Cache-hit responses mean "already in context, move on."
- Do NOT use additional `rg`/`Bash` searches as a substitute for Reading files. No Bash `find`/`grep` for discovery — `rg` only.
- Edit mode: run `go build ./...` after all edits; if zero edits, the summary must say "No changes needed".

EFFICIENCY: batch all Edits for a file in its own iteration; emit the report the iteration AFTER the last file is Read; if the iteration cap forces an early stop, report anyway with a `## Coverage Shortfall` list.

COVERAGE IS MANDATORY — full coverage, no sampling. Read EVERY non-test, non-vendor, non-generated `.go` file exactly once; large-codebase "sample remaining files" guidance does NOT apply to this agent.
