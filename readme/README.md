# readme

Autonomous README generation agent that analyzes a project's structure,
determines the project type, and writes a comprehensive `README.md`
following progressive disclosure best practices.

## Overview

This agent reads manifest files and source entry points to understand what
a project does, then generates a README that answers the three fundamental
questions: What is this? Why should I care? How do I use it? It applies
templates from the embedded knowledge base (`readme-standards.md`) and
writes the result directly to `README.md`.

## Usage

```bash
# Generate README for the current directory
squad run --agent readme

# Generate README with a custom prompt
squad run --agent readme "Focus on the CLI usage and deployment sections"

# Analysis only — print the planned structure without writing
squad run --agent readme --mode readonly
```

## What Gets Generated

The agent produces a structured README covering:

- **Project Title** — descriptive name
- **One-line Description** — what it does and who it's for
- **Overview** — 2-3 sentence problem/solution/audience summary
- **Features** — key capabilities as a bullet list
- **Installation** — prerequisites with versions and install commands
- **Quick Start** — copy-paste example that works immediately
- **Usage** — detailed examples for common scenarios
- **Configuration** — environment variables and config file options
- **Contributing** — PR workflow (open source projects)
- **License** — license type and link

Sections that don't apply to the project type are omitted automatically.

## Project Types Supported

| Type | Detection Signal | Template Applied |
|------|-----------------|-----------------|
| CLI tool | `cmd/`, cobra/viper, click, argparse | Commands table, options table |
| Library | `lib/`, exported API surface, no main | API reference, code examples |
| Web App | Express/Gin/FastAPI entry, `public/` | Demo link, screenshots |
| Framework | Plugin system, scaffolding commands | Architecture overview |
| Monorepo | `packages/`, `apps/` directories | Package structure listing |

## Hard Rules

Key constraints the agent enforces:

1. **No placeholder text** — never outputs "TODO", "Coming soon", or "TBD"
2. **Working examples** — all Quick Start and Usage blocks are real commands
3. **Version numbers** — prerequisites always include minimum versions
4. **Single Write** — generates the complete README in memory, writes once
5. **Omit empty sections** — no scaffolding for sections that don't apply

## Output Format

After writing `README.md`, the agent emits:

```
## README Generated

Project type: CLI
Sections included: Overview, Features, Installation, Quick Start, Usage, Configuration, License
Sections omitted: Contributing (not open source), API Reference (CLI, not library)
Output: README.md written (142 lines)
```

## Reference

See [references/readme-standards.md](references/readme-standards.md)
for the complete knowledge base covering core principles, section templates,
project type variations, badge recommendations, and the quality checklist.

## Related Agents

- **go-doc-comments** — add doc comments to Go source files
- **nodejs-doc-comments** — add JSDoc to Node.js/TypeScript exports
- **python-doc-comments** — add docstrings to Python declarations
