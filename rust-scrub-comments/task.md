Scan all Rust source files for useless, LLM-generated, and non-idiomatic comments and
{{if eq .Mode "edit"}}**trim** mixed blocks to keep the useful "why" portion; **leave pure single-line narration alone** unless I have explicitly asked you to scrub or delete narration in this prompt (I have NOT){{end}}{{if eq .Mode "readonly"}}report them with confidence scores{{end}}.

WORKFLOW (sequential, one file per iteration):

- Iteration 1: `Glob **/*.rs`.
- Iteration 2: Bash runs the `rg --type rust` discovery search — Search A (LLM-vocabulary regex `(crucial|leverage|seamless|robust|Moreover|Furthermore|Additionally|streamlined|meticulous|intricate|comprehensive|pivotal|noteworthy|facilitate|underscore|Step \d|Phase \d)`). Separate from Glob. Hits define PRIORITY ORDER; they do NOT define the corpus.
- Iterations 3..N: ONE `Read` per iteration; emit Edits for that file in the SAME iteration; narrate `Progress: K/<total> done (last: <path>, edits: M)`; advance. NEVER parallel-read. NEVER re-Read a cache-hit file.
- Iteration N+1: `cargo check 2>&1`, then emit the structured report.

CONSTRAINTS:

- Skip `target/`, `.git/`, `.github/`, `.claude/`, vendored dirs, generated files.
- Never touch `// SAFETY:` comments, `# Safety`/`# Errors`/`# Panics`/`# Examples` headers, `//!` crate/module docs, attributes, or doctest code blocks.
- In crates with `#![deny(missing_docs)]`, NEVER delete `///` docs on `pub` items — the build depends on them.
- Apply the verb-phrase test on each candidate:
  - Multi-line block with any "why"/edge-case/platform/spec/safety/algorithm content → **TRIM** to that content (NOT full-delete).
  - Single-line pure narration with no extra content → **FLAG** in `## Comments Flagged (not deleted — no explicit intent)`. Do NOT delete; this prompt did not ask for narration removal.
- LLM-generated requires 3+ tell categories.
- Comments only — never modify code, signatures, `use` statements, `mod` declarations, or string literals.
- Cache-hit responses mean "already in context, move on."
- Do NOT use additional `rg`/`Bash` searches as a substitute for Reading files. No Bash `find`/`grep` for discovery — `rg` only.
{{if eq .Mode "edit"}}
- Run `cargo check` after all edits. If zero edits, summary must say "No changes needed".
{{end}}

{{include "hard-rules/efficiency.md"}}

COVERAGE IS MANDATORY — full coverage, no sampling. Read EVERY non-test, non-generated `.rs` file exactly once. The Large-tier "sample" guidance from efficiency.md does NOT apply to this agent.
