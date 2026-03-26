# rust-doc-comments

Autonomous Rust documentation agent that discovers public declarations, adds
or improves doc comments following Rust documentation conventions, and verifies
compilation.

## Overview

The `rust-doc-comments` agent analyzes Rust codebases for missing or deficient
documentation on public declarations. It operates in two modes:

- **edit** — discovers gaps, adds/improves doc comments, verifies compilation
- **readonly** — discovers gaps and produces a prioritized report

## What Gets Documented

- Public functions and methods (`///`)
- Public structs, enums, and traits (`///`)
- Public constants and static items (`///`)
- Module-level documentation (`//!`)
- `# Safety` sections for `unsafe` functions
- `# Errors` sections for `Result`-returning functions
- `# Panics` sections for panicking functions
- `# Examples` for complex public API items

## Structure

```
rust-doc-comments/
├── agent.yaml                              # Agent manifest
├── system.md                               # Core prompt
├── agent.md                                # Execution wrapper
├── task.md                                 # Default task instructions
├── README.md                               # This file
└── references/
    └── rust-documentation-standards.md     # Documentation standards
```

## Usage

```bash
# Run in edit mode (add/fix doc comments)
squad run --agent rust-doc-comments

# Run in readonly mode (report only)
squad run --agent rust-doc-comments --mode readonly

# Print the bundled prompt
squad run --agent rust-doc-comments --print-bundle --dry-run
```

## Hard Rules

- Only modify doc comments — never change code logic
- Use `///` for items, `//!` for modules
- Complete sentences with proper punctuation
- No redundant comments (skip trivial declarations)
- `# Safety` section mandatory on `pub unsafe fn`
- Public declarations only
- Proportional: short comments for simple items

## Version

0.1.0
