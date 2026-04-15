Run the full Rust quality pipeline on this codebase.

Start by calling **RepoMap** to discover the workspace structure — crate
boundaries, dependency graph, and file/line counts per crate.

For **workspace repos** (multiple crates):

1. Group crates into dependency tiers using the RepoMap dependency graph.
   Crates with no local dependencies are Tier 1 and can be processed in
   parallel.
2. For each agent phase (review → tests → docs), dispatch child agents
   per-crate using `Task(background=true, working_dir="path/to/crate")`.
   Process all crates in a tier simultaneously, then move to the next tier.
3. After each phase, run the regression gate from the workspace root.

For **single-crate repos** (no workspace):

1. Run agents sequentially: rust-review → rust-tests → rust-doc-comments.
2. Run the regression gate after each agent.

Agents to execute in order (per crate):

1. **rust-review** -- fix code quality and best-practice violations
2. **rust-tests** -- increase test coverage to {{.Default "COVERAGE_TARGET" "75"}}%
3. **rust-doc-comments** -- add/improve doc comments on public declarations

After each phase, summarize changes per crate and pass that context to the
next phase. Emit a combined pipeline report at the end.

If the user provided specific instructions, incorporate them into each
agent's prompt where relevant.
