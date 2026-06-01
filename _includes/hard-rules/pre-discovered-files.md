# Pre-Discovered Files Contract

When this agent runs standalone, Phase 1 discovers files itself via
the language-specific Glob pattern and runs the language-specific
lint command. When this agent runs as a stage in a Squad pipeline,
the orchestrator pre-computes both and injects them into the prompt
so the stage doesn't burn iterations redoing work the orchestrator
already did.

## Injected blocks

The orchestrator may inject either or both of these blocks into your
prompt. Both headers are exact-match strings.

- `Pre-discovered source files` — followed by a newline-delimited
  list of file paths. **Authoritative.** If present, use this list
  verbatim. Skip the agent's fallback Glob. Do not Glob "to
  double-check," and do not re-filter (the orchestrator already
  applied the language's filter rules).

- `LINT_WARNINGS` (or a tool-specific variant the agent declares —
  e.g. `CLIPPY_WARNINGS` for Rust) — followed by the output of the
  agent's lint command (`go vet ./...` / `golangci-lint run` /
  `ruff check` / `cargo clippy` / `eslint` / etc.). The exact
  header name is whatever the agent's Phase 1 step calls out.
  **Authoritative.** If present, treat as the lint result for
  Phase 2. Skip the agent's fallback lint run.

## Behavior matrix

| `Pre-discovered source files` present? | Warnings block present? | Phase 1 behavior |
|---|---|---|
| Yes | Yes | Use injected file list; use injected lint output; skip both Glob and lint |
| Yes | No | Use injected file list; skip Glob; run agent's fallback lint command |
| No | Yes | Run agent's fallback Glob; use injected lint output; skip lint run |
| No | No | Standalone mode — run both fallback Glob and fallback lint |

## Output expectation

Your report still names every file you touched, regardless of
whether discovery came from the injected list or from the fallback
Glob. The pipeline orchestrator reads the report to decide whether
the next stage can run.
