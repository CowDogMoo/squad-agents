# Skill Extraction Plan

Plan for extracting reusable procedures from agents in this repo into
`../squad-skills/`. Each candidate is independent and can be landed in
its own PR. Execution order is recommended bottom-of-this-doc, but
nothing blocks anything else.

## Conventions

- Skill dir lives at `../squad-skills/<name>/SKILL.md` with the
  standard frontmatter (`name`, `description`).
- Agents load skills at runtime via `Skill("<name>")` — see
  `go-scrub-comments/system.md:12-15` and `rust-scrub-comments/system.md:12-15`
  for the established calling pattern (the body is loaded into context
  on first need, kept for the rest of the run).
- Skills are host-portable and model-agnostic: no agent identity, no
  pipeline orchestration, no language-specific lint commands.
- Per-language specifics (`go build`, `cargo test`, `pytest`, `c8`,
  exempt-file lists, idiom names like `reports whether`/`# Errors`)
  stay in the agent that calls the skill.
- After extracting, each touched agent gets a 2-3 line invocation
  block replacing the duplicated body, plus any per-language addendum
  that doesn't belong in the skill.

---

## Candidate 1 — `comment-scrub-playbook`

**Priority: highest.** Smallest blast radius (2 agents), highest
duplication (~95% verbatim between Go and Rust), pattern already
established alongside `detect-llm-tells`.

- **Skill name:** `comment-scrub-playbook`
- **Description (frontmatter):** "Classify source-code comments into
  five delete-candidate categories (states-the-obvious, LLM-generated,
  no-info, non-idiomatic, visual noise) and decide delete vs. trim
  vs. keep. Use when scrubbing useless or LLM-slop comments from a
  codebase."

### Sources to extract

- `go-scrub-comments/system.md:91-127` — WHAT TO DELETE (Categories
  1-5) + WHAT TO KEEP.
- `rust-scrub-comments/system.md:88-123` — same five categories +
  WHAT TO KEEP. 95% verbatim match with the Go version (only `///`
  vs `//`, `cargo`/build verb, and `//go:*` vs `#[allow]` differ).
- The "comment block" unit-of-analysis and exempt-content list
  (`TODO`/`FIXME`/`HACK`/`NOTE`/`XXX`/`BUG(`, license headers,
  generated files) — already covered by `detect-llm-tells`; the new
  skill should reference it instead of restating.

### What stays in each agent

- Identity (`You are an autonomous comment-cleanup agent for Go…`),
  hard rules numbered 0-14, and the WORKFLOW phases (these are
  agent-specific orchestration).
- Language-specific items:
  - **Go:** the `//go:*`/`//nolint`/`//lint:ignore`/`//export`/`//line`
    directives list (rule 5), the `golint`/`go vet` exported-doc
    protection (rule 13), the `go build ./...` verify step (E6), the
    `**/*.go` Glob, and the Phase 1 `rg` regex.
  - **Rust:** the `///`/`//!` distinction, `#[allow(...)]`/`#[deny(...)]`
    attribute protection, `cargo build` verify, `**/*.rs` Glob, and
    the Rust-flavored Phase 1 regex.

### Skill body structure

1. Objective (what classifications produce; the caller decides
   action).
2. Unit of analysis (contiguous comment block; cite
   `detect-llm-tells` for the underlying unit/exempt rules).
3. The five categories (verbatim from the agents, generalized so the
   examples cover ≥2 languages or are language-tagged).
4. WHAT TO KEEP (also verbatim).
5. Decision matrix: delete entire block / trim mixed block / keep —
   when each applies.
6. Guardrails: "never touch code, signatures, imports, string
   literals"; "doc comments on exported identifiers stay even if
   tautological — a separate doc-comments agent handles those";
   "blank-line gap between doc comment and decl is a fix-the-gap, not
   a delete-the-comment."

### Agent edits

- `go-scrub-comments/system.md`: replace lines 91-127 (WHAT TO
  DELETE + WHAT TO KEEP) with a 3-line block similar to the existing
  `Skill("detect-llm-tells")` invocation, plus the Go-only exempt
  directives table. Keep hard rules 5, 13, E6.
- `rust-scrub-comments/system.md`: same pattern for lines 88-123,
  preserving the Rust attribute-directive rules.

### Validation

- After edits, both agents still pass `pre-commit run --all-files`.
- Manually diff the new skill against both original sections —
  confirm no rule was silently dropped.
- Dry-run each agent in `readonly` mode against a known-dirty fixture
  and verify the same comments get flagged as before.

---

## Candidate 2 — `doc-comments-discovery-and-fix-loop`

**Priority: high.** Unifies 4 agents, near-verbatim workflow
duplication; per-language idioms cleanly separable.

- **Skill name:** `doc-comments-discovery-and-fix-loop`
- **Description:** "Discover exported declarations missing or
  carrying deficient doc comments, prioritize by impact, apply
  proportional fixes in a read-then-edit loop, verify the result
  compiles. Use from any language-specific doc-comment agent."

### Sources to extract

- `go-doc-comments/system.md:59-86` (Phase 1 Discover, Phase 2
  Analyze, Phase 3 Fix and Verify, Phase 4 Report) and rules 1, 9,
  10, 11, 13, 19, 20, 21, 22, 23, 24 — the workflow-and-discipline
  rules that are language-agnostic.
- `python-doc-comments/system.md:59-100` — same phases.
- `rust-doc-comments/system.md:65-91` — same phases.
- `nodejs-doc-comments/system.md` — equivalent phases (verify exact
  line ranges before edit).

### What stays in each agent

- Language-specific style rules:
  - **Go:** "start with declared name," "reports whether," `# Heading`
    package sections, `[Name]` doc links, package-comment-once rule
    (rules 5, 6, 7, 16, 25 of the current go-doc-comments hard rules).
  - **Python:** PEP 257, Google-style Args/Returns/Raises sections,
    module-level docstring placement.
  - **Rust:** `# Errors`, `# Panics`, `# Safety`, `# Examples`
    section conventions, `///` vs `//!` distinction.
  - **Node.js:** JSDoc tags (`@param`, `@returns`, `@throws`).
- Build/verify command (`go build ./...`, `python -m compileall`,
  `cargo check`, `tsc --noEmit` or equivalent).
- File-discovery glob and `_test.go`/`__tests__` filters.

### Skill body structure

1. Objective and inputs (the agent provides language style and verify
   command; the skill provides the loop).
2. Phase 1 Discover (honor pre-discovered list, otherwise Glob — the
   pre-discovered-files contract is the agent's job via
   `{{include "hard-rules/pre-discovered-files.md"}}`; the skill
   simply assumes its file list is authoritative).
3. Phase 2 Analyze (read in parallel batches of 3-5, catalog every
   gap, prioritize: missing-on-complex > missing-on-simple >
   improvements > module-level).
4. Phase 3 Fix and Verify (one fix per edit, group by file, read
   ONLY edited lines to verify, run language-supplied build command,
   revert with `git checkout -- <file>` on failure).
5. Phase 4 Report (use Phase 2 notes; no re-reads).
6. Proportionality and trivial-skip guidance (one-line getter = one-
   line comment; self-documenting names may need no comment).
7. Discipline rules: respect existing good comments, no logic
   changes, no new dependencies, never modify signatures.

### Agent edits

For each of the four `*-doc-comments` agents:

- Replace the WORKFLOW block (Phase 1-4) with
  `Skill("doc-comments-discovery-and-fix-loop")` plus a short "this
  agent's inputs to the skill" block: the file glob, the verify
  command, and a one-paragraph style-rule pointer to the agent's own
  REVIEW CATEGORIES section.
- Keep the language-specific hard rules and REVIEW CATEGORIES intact
  in `system.md`.

### Validation

- For each language, run the agent against a fixture with known
  missing docs; confirm the same set of edits land.
- Confirm `_includes/severity/standard.md` and
  `_includes/output/edit-format.md` are still wired in via the
  remaining agent content (the skill doesn't replace them).

---

## Candidate 3 — `pre-discovered-files.md` (build-time include, NOT a skill)

**Priority: medium.** Smallest per-agent footprint (~3 lines) but
touched in ~12 agents. Extract to lock down the contract so future
agents copy from one place.

**Decision: ship as `_includes/hard-rules/pre-discovered-files.md`,
not as a squad-skills entry.** The contract is squad-pipeline-
specific — the `Pre-discovered source files` / `LINT_WARNINGS`
headers are emitted by squad's orchestrator and no other host injects
them, so host-portability buys nothing. A runtime skill would cost 12
tool calls across the fleet to fetch a ~36-line contract that's
already squad-shaped; an include is zero-cost and gives the same DRY
win. This is also why open-question Q2 (cross-skill loading for C2/C4
referencing C3) dissolves: the contract sits in every agent's system
prompt before C2 or C4 is ever invoked.

- **Include path:** `_includes/hard-rules/pre-discovered-files.md`
- **Invocation:** `{{include "hard-rules/pre-discovered-files.md"}}`
  in each affected `system.md`, alongside the existing
  `{{include "hard-rules/efficiency.md"}}` / `universal.md` lines.

### Sources to extract

- `go-review/system.md:84-86`
- `python-review/system.md:65-68` (verify exact range before edit)
- `rust-review/system.md:93-95`
- `nodejs-review/system.md:87-89`
- `go-doc-comments/system.md:63-65`
- `python-doc-comments/system.md:71`
- `rust-doc-comments/system.md:69-71`
- `nodejs-doc-comments/system.md` — Phase 1 step 1
- `go-tests/system.md:57-59` (Phase 0)
- `python-tests/system.md`, `rust-tests/system.md`,
  `nodejs-tests/system.md` — equivalent Phase 0 blocks
- `go-scrub-comments/system.md`, `rust-scrub-comments/system.md` —
  any pre-discovered-files clause (verify; this may not be present
  today)
- `go-security-audit/injection-system.md:90-91` and the
  `resources-system.md` counterpart
- `nodejs-security-audit/*-system.md` counterparts

### What stays in each agent

- The language-specific fallback Glob pattern (`**/*.go`,
  `**/*.py`, etc.) and the language-specific filter rules
  (`_test.go`/`vendor/`, `__tests__/`, `target/`, `node_modules/`).
- The language-specific lint command (`go vet`/`golangci-lint`,
  `ruff`, `clippy`, `eslint`) — the include names the contract; the
  agent supplies the tool.

### Include body structure

1. The two injected prompt blocks (`Pre-discovered source files`,
   `LINT_WARNINGS`) — exact header strings the orchestrator emits.
2. Behavior:
   - If `Pre-discovered source files` present → use it; skip Glob.
   - If `LINT_WARNINGS` present → use it; skip the lint run.
   - If neither present → fall back to the agent-supplied
     discovery (Glob + filter) and lint command.
3. Authority: the injected list is authoritative. Do not Glob
   "to double-check."
4. Output expectation: the agent's later report still names every
   file it touched, regardless of whether discovery came from the
   prompt or from Glob.

### Agent edits

- In each touched `system.md`, replace the local Phase 1 step that
  spells out the contract with
  `{{include "hard-rules/pre-discovered-files.md"}}`. Keep the
  per-agent fallback Glob pattern and lint command nearby — those
  are agent-supplied inputs to the contract, not part of it.
- Verify the pipelines (`go-pipeline/agent.yaml`,
  `python-pipeline/agent.yaml`, `rust-pipeline/agent.yaml`) still
  inject the same header strings — the include is documenting an
  existing contract, not changing it.

### Validation

- Diff a few stage runs before/after with the same fixture; the
  contract is unchanged so behavior should be identical.
- Grep `squad-agents/` for any remaining "Pre-discovered source
  files" prose to confirm all sites migrated.

---

## Candidate 4 — `score-coverage-and-report-gaps`

**Priority: medium.** Unifies 4 test-coverage agents but has the
deepest per-language coupling — extract the *phases and discipline*,
not the commands.

- **Skill name:** `score-coverage-and-report-gaps`
- **Description:** "Measure baseline coverage, enumerate zero-coverage
  functions and untested packages, prioritize by impact, write tests,
  re-verify, and report the delta. Use from any language-specific
  test-coverage agent; the caller supplies the coverage tool and
  assertion patterns."

### Sources to extract

- `go-tests/system.md:55-97` — Phase 0 Use Pre-collected, Phase 1
  Measure, Phase 2 Prioritize, Phase 3 Write Tests, Phase 4 Verify,
  Phase 5 Report. Pull the *shape* of each phase, replacing concrete
  `go test`/`go tool cover` commands with placeholders the caller
  supplies.
- `python-tests/system.md`, `rust-tests/system.md`,
  `nodejs-tests/system.md` — confirm they currently mirror the same
  phase structure with `pytest --cov` / `cargo llvm-cov` / `c8` (or
  `nyc`) substituted.
- Cross-cutting rules referenced in the audit (delta-required Rule
  7, gap-analysis-when-target-met Rule 21, no-empty-test-files Rule
  4a) — these are language-neutral.

### What stays in each agent

- The coverage tool invocation (`go test ./... -coverprofile=...` vs
  `pytest --cov=...` vs `cargo llvm-cov` vs `c8 npm test`).
- The "no test files" probe (`grep '\[no test files\]'` vs
  `--cov-report=term-missing` vs the equivalent).
- The assertion / table-driven / fixture conventions
  (`t.Run`+`t.Parallel` for Go; `pytest.mark.parametrize` for
  Python; `rstest`/`#[test]` for Rust per the existing
  `feedback_rust_test_idioms` preference; Jest/Vitest for Node).
- The `COVERAGE_TARGET` defaults and the cmd/-vs-non-cmd split (a
  Go-ism that doesn't generalize).

### Skill body structure

1. Inputs (caller provides: coverage command, function-listing
   command, target percentage, file glob).
2. Phase 0: Assume the agent has already honored the
   pre-discovered-files contract (Candidate 3, lives as an include);
   the skill takes the file list as input.
3. Phase 1: Measure baseline; record total and per-package.
4. Phase 2: Prioritize — zero-coverage exported functions in
   business-logic packages first; packages with `no test files` next;
   trivial wrappers last.
5. Phase 3: Write tests in priority order; the caller supplies idiom
   patterns.
6. Phase 4: Re-verify with the same coverage command; compare delta.
7. Phase 5: Report before/after coverage delta, files added,
   packages still under target.
8. Discipline: no empty test files, no `_test.go` (or equivalent)
   shells with only setup, gap analysis is mandatory even when
   target is met.

### Agent edits

- In each `*-tests/system.md`, replace the workflow with a
  `Skill("score-coverage-and-report-gaps")` call plus a "this
  agent's inputs to the skill" block: coverage cmd, listing cmd,
  target %, file glob, idiom patterns.
- Keep the language-specific testing-idiom hard rules in the agent.

### Validation

- Run each `*-tests` agent against its existing fixture (or a fresh
  low-coverage repo) and compare the resulting test count + coverage
  delta to a baseline run.
- Confirm `feedback_rust_test_idioms` preferences (no `test_` prefix,
  `approx` for floats, `rstest`/`test-case` for parameterized) are
  still enforced — they live in the agent, not the skill.

---

## Anti-candidates (do NOT extract)

Document these explicitly so a future reader doesn't re-litigate.

- **`_includes/severity/*`, `_includes/output/*`, `_includes/hard-rules/*`.**
  These are build-time template includes inlined at agent-load time.
  Converting to runtime skills would force every agent to burn a tool
  call to fetch a 30-line table. The current `{{include "..."}}`
  model is correct.
- **`_includes/basic/`, `_includes/weekly-planner-template/`.**
  Scaffolding/starter agents, not procedures.
- **Per-language WHAT TO FIX / WHAT NOT TO FIX lists** in
  `go-review/system.md:156-205`, `python-review/system.md:103-153`,
  `rust-review/system.md:165-205`, `nodejs-review/system.md` (verify
  range). Each list is a single-language bug taxonomy
  (Go `_ =` rules, Rust `unwrap()` rules, Python `# nosec` handling,
  Node `==`/`===`); merging would force every review agent to load
  all languages.
- **`grocery-runner/stages/shop/system.md` overrides.** Squad-runtime
  glue around the already-extracted `add-groceries-to-whole-foods-cart`
  skill (CORS pre-navigate, `#add-to-cart-button-grocery` vs
  `#add-to-cart-button`, prime-vs-WF cart detection). Pipeline-
  specific; stays in the agent.
- **`go-security-audit` injection/resources split.** Deep, single-
  language CWE taxonomies; orthogonal sub-agents; don't merge.
- **`weekly-planner/agent.yaml` inline prompt body.** Pipeline-style
  orchestration (compute dates → find heading → parse rows → create
  events). One-agent-only; only the doc-creation slice
  (`bootstrap-weekly-planner-doc`) was correctly skill-shaped.

---

## Execution order

Recommended order, biggest leverage per unit of effort:

1. **Candidate 1 — `comment-scrub-playbook`.** Smallest blast radius
   (2 agents). Validates the extraction pattern end-to-end without
   touching the high-traffic review/test agents.
2. **Candidate 2 — `doc-comments-discovery-and-fix-loop`.** 4 agents,
   highest verbatim duplication of substantive content.
3. **Candidate 3 — `_includes/hard-rules/pre-discovered-files.md`.**
   ~12 agents, small per-agent footprint but locks down a contract
   that future agents will copy. Build-time include, not a skill —
   see Candidate 3 section for rationale.
4. **Candidate 4 — `score-coverage-and-report-gaps`.** Most coupling
   to language tooling; do last so the extraction shape is
   well-rested by then.

Each lands as its own PR. None depends on another. Candidate 3 is
a single squad-agents PR (no squad-skills counterpart). Candidates
2 and 4 don't transitively load Candidate 3 — the include sits in
each agent's system prompt before either skill is invoked.

## Per-candidate PR shape

### Skill candidates (C1, C2, C4)

1. Add `../squad-skills/<name>/SKILL.md` (PR against squad-skills).
2. After that lands, open a squad-agents PR that:
   - Edits the affected `system.md` files to call `Skill("<name>")`.
   - Adds a one-line entry to the "Available Skills" table in
     `../squad-skills/README.md`.
   - Runs `pre-commit run --all-files` clean.
3. Smoke-test each touched agent against a fixture (readonly mode is
   cheap and sufficient for the comment/doc agents; the test
   coverage skill needs an actual run to confirm coverage delta).

### Include candidate (C3)

Single squad-agents PR:

1. Add `_includes/hard-rules/pre-discovered-files.md`.
2. Replace the inline contract block in each affected `system.md`
   with `{{include "hard-rules/pre-discovered-files.md"}}`.
3. Run `pre-commit run --all-files` clean.
4. Diff a representative stage run before/after — behavior should
   be identical.

## Open questions

- **Validation harness.** No fixture suite exists today for any of
  these agents. Worth setting up a tiny `tests/fixtures/` per
  language with a few known-dirty files before landing Candidate 1
  so subsequent extractions have a regression check.
