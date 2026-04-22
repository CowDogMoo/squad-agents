{{if eq .Mode "edit"}}
{{- if .Var "CRATE"}}
**SCOPE: Focus exclusively on the `{{.Var "CRATE"}}` crate.**
{{- end}}

Analyze and improve test coverage for this Rust codebase.

Use pre-collected data if provided, otherwise discover .rs files with Glob.
Write tests to close coverage gaps. Start writing by iteration 6.

IMPORTANT CONSTRAINTS:

- Only create/modify test code — NEVER edit non-test source lines
- NEVER create `tests/` directory or `tests/*.rs` files — inline tests only
- Priority: 0% files first, then below-target, then already-tested last
- Use `rstest` for parameterized tests, `approx` for floats, `assert_matches!` for errors
- No `test_` prefix by default — use `<function>_<behavior>` naming
- Calculate coverage ceiling. If below target, explain why with recommendations
- Run `cargo test` after each batch. Check `--features` for gated modules
- Per-module target: {{.Default "COVERAGE_TARGET" "75"}}%. Budget: <=15 files = 15 iter
{{end}}
{{if eq .Mode "readonly"}}
{{- if .Var "CRATE"}}
**SCOPE: Focus exclusively on the `{{.Var "CRATE"}}` crate.**
{{- end}}

Analyze test coverage for this Rust codebase. Use Glob to discover .rs files,
read each file, and produce a prioritized report of untested functions/modules.
Do NOT write or modify any files.
{{end}}
