Run the full Python quality pipeline on this codebase.

Execute these agents in order, passing context between each:

1. **python-review** -- fix code quality and security issues
2. **python-tests** -- increase test coverage to {{.Default "COVERAGE_TARGET" "75"}}%
3. **python-doc-comments** -- add/improve docstrings on public declarations

Start by confirming this is a Python codebase (Glob **/*.py).
Then run each agent sequentially via the Task tool.
After each agent, summarize its changes and pass that context to the next agent.
Emit a combined pipeline report at the end.

If the user provided specific instructions, incorporate them into each agent's
prompt where relevant. For example, "focus on the api/ directory" should be
forwarded to all three agents.
