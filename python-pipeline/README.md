# python-pipeline

Composed agent that runs Python quality agents sequentially: review, tests,
and doc comments.

## Overview

This is a composed agent — it has no prompts of its own. It chains three
sub-agents in dependency order, passing context between stages:

| Order | Agent | Purpose |
|-------|-------|---------|
| 1 | python-review | Code quality and best-practice fixes |
| 2 | python-tests | Test coverage analysis and gap filling |
| 3 | python-doc-comments | PEP 257 docstring documentation |

A gate runs `python -m pytest` after tests to catch regressions.

## Usage

```bash
# Run the full pipeline against the current directory
squad run --agent python-pipeline

# Run against a specific Python project
squad run --agent python-pipeline --working-dir /path/to/python-project

# With cost limit
squad run --agent python-pipeline --max-cost 15.00
```

## Stages

```
review → tests → docs
           │
           ▼
        pytest
```

## Version

0.3.0
