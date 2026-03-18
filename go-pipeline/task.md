Run the full Go quality pipeline on this codebase.

Start by confirming this is a Go codebase (Glob **/*.go) and checking go.mod
for Cobra dependencies to decide whether to include go-cobra.

Execute these agents in order, passing context between each:

1. **go-cobra** -- fix Cobra/Viper anti-patterns (ONLY if go.mod contains
   github.com/spf13/cobra)
2. **go-review** -- fix code quality and best-practice violations
3. **go-tests** -- increase test coverage to {{.Default "COVERAGE_TARGET" "75"}}%
4. **go-doc-comments** -- add/improve doc comments on exported declarations

Run each agent sequentially via the Task tool.
After each agent, summarize its changes and pass that context to the next agent.
Emit a combined pipeline report at the end.

If the user provided specific instructions, incorporate them into each agent's
prompt where relevant. For example, "focus on the cmd/ directory" should be
forwarded to all agents.
