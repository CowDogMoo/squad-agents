Run the full Rust quality pipeline on this codebase.

Start by confirming this is a Rust codebase (Glob **/*.rs) and reading
Cargo.toml to understand the crate structure.

Execute these agents in order, passing context between each:

1. **rust-review** -- fix code quality and best-practice violations
2. **rust-tests** -- increase test coverage to {{.Default "COVERAGE_TARGET" "75"}}%
3. **rust-doc-comments** -- add/improve doc comments on public declarations

Run each agent sequentially via the Task tool.
After each agent, summarize its changes and pass that context to the next agent.
Emit a combined pipeline report at the end.

If the user provided specific instructions, incorporate them into each agent's
prompt where relevant. For example, "focus on the src/parser/ directory" should
be forwarded to all agents.
