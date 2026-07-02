Add and improve doc comments on all public declarations in this Rust
codebase. Default: apply fixes in place. If the request says
"readonly"/"report only": identify missing or deficient doc comments,
produce a prioritized report, and do NOT write or modify any files.

Start by using Glob with '**/*.rs' to discover all Rust source files.
Read each file (skip target/). In edit mode apply fixes via Edit tool,
highest priority first.

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
