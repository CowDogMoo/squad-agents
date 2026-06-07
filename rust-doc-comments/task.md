{{if eq .Mode "edit"}}
Add and improve doc comments on all public declarations in this Rust codebase.

Start by using Glob with '**/*.rs' to discover all Rust source files.
Read each file (skip target/). Apply fixes via Edit tool, highest priority first.

IMPORTANT CONSTRAINTS:

- Only modify doc comments -- NEVER change code logic or signatures
- Use `///` for item docs, `//!` for module/crate docs
- `# Safety` section MANDATORY on `pub unsafe fn`
- `# Errors` section for functions returning `Result`
- `# Panics` section for functions that can panic
- Use intra-doc links: [`TypeName`]. Doc comments go ABOVE attributes.
- No redundant comments -- skip trivial declarations
- Public declarations only -- skip private items
- Read each file ONCE, catalog findings, then fix
- After `cargo build` passes, emit report IMMEDIATELY
{{end}}
{{if eq .Mode "readonly"}}
Analyze doc comment quality in this Rust codebase.

Use Glob with '**/*.rs' to discover all Rust source files.
Read each file and identify missing or deficient doc comments.
Produce a prioritized report. Do NOT write or modify any files.
{{end}}
