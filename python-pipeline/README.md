# python-pipeline

Orchestrator agent that runs `python-review`, `python-tests`, and
`python-doc-comments` sequentially with context passing to avoid redundant work.

## Overview

The `python-pipeline` agent coordinates three child agents in order:

1. **python-review** — fix code quality and best-practice issues
2. **python-tests** — fill test coverage gaps
3. **python-doc-comments** — add missing docstrings

Each agent receives a summary of what the previous agent changed, so it skips
files and declarations that were already handled.

## Usage

```bash
# Run the full pipeline against the current directory
squad run --agent python-pipeline

# Run against a specific Python project
squad run --agent python-pipeline --working-dir /path/to/python-project

# Specify model and provider
squad run --agent python-pipeline --model claude-opus-4-6 --provider anthropic
```

## Example

```bash
squad run --agent python-pipeline \
  --working-dir /home/user/my-flask-app \
  --model claude-opus-4-6 \
  --provider anthropic \
  --max-iterations 50 \
  --api-key "$YOUR_API_KEY"
```

### Example Output

```markdown
## Pipeline Summary

### Stage 1: python-review
**Files modified:** 3
- src/auth.py — replaced mutable default argument `def login(users=[])`
- src/db.py — parameterized raw SQL query to prevent injection
- src/utils.py — replaced bare `except:` with `except Exception`

### Stage 2: python-tests
**Tests added:** 11
**Coverage:** 38% → 71%
- tests/test_auth.py — 4 tests (login, logout, token validation)
- tests/test_db.py — 5 tests (connection, query, transaction rollback)
- tests/test_utils.py — 2 tests (retry logic, timeout handling)

### Stage 3: python-doc-comments
**Docstrings added:** 8
- src/auth.py — module docstring, `login()`, `validate_token()`
- src/db.py — `Database`, `connect()`, `execute()`
- src/utils.py — `retry()`, `timeout()`

## Validation
- `python -m py_compile`: PASS
- `pytest`: PASS (19 tests)
- `ruff check .`: PASS
```

## Children

| Order | Agent | Purpose |
|-------|-------|---------|
| 1 | python-review | Code quality and best-practice fixes |
| 2 | python-tests | Test coverage analysis and gap filling |
| 3 | python-doc-comments | PEP 257 docstring documentation |

## Version

0.1.0
