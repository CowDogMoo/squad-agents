# go-pipeline

Composed agent that runs Go quality agents sequentially: review, tests,
doc comments, and optionally Cobra fixes.

## Overview

This is a composed agent — it has no prompts of its own. It chains four
sub-agents in dependency order, passing context between stages:

| Order | Agent | Purpose |
|-------|-------|---------|
| 1 | go-cobra | Cobra/Viper CLI fixes (runs first) |
| 2 | go-review | Code quality and best-practice fixes |
| 3 | go-tests | Test coverage analysis and gap filling |
| 4 | go-doc-comments | Exported declaration documentation |

Gates run `go test ./...` after tests and `go build ./...` after docs to
catch regressions.

## Usage

```bash
# Run the full pipeline against the current directory
squad run --agent go-pipeline

# Run against a specific Go project
squad run --agent go-pipeline --working-dir /path/to/go-project

# With cost limit
squad run --agent go-pipeline --max-cost 20.00
```

## Stages

```
cobra → review → tests → docs
                   │        │
                   ▼        ▼
              go test   go build
```

## Version

0.3.0
