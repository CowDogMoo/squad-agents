---
name: python-review-criteria
description: "Review criteria for Python — 3.12/3.13 features, exception handling, type annotations, structural pattern matching, data structures, dataclasses/Pydantic/attrs, function and class design, and async patterns. Use when reviewing Python code for best-practice violations. Also loaded by the python-review agent as its knowledge base."
---
# Python Code Review Criteria

Severity calls, house calibrations, and the checks a Python review applies.
Topic detail lives in `references/`; the index below says when to read each
file.

## Contents

1. [Read-When Index](#read-when-index)
2. [Scope and Precedence](#scope-and-precedence)
3. [House Calibrations](#house-calibrations)
4. [Error and Exception Handling](#error-and-exception-handling)
5. [Data Structures and Mutability](#data-structures-and-mutability)
6. [Functions, Classes, and Code Structure](#functions-classes-and-code-structure)
7. [Imports and Module State](#imports-and-module-state)
8. [Severity Classification](#severity-classification)
9. [Quick Reference Checklist](#quick-reference-checklist)
10. [Anti-Patterns to Avoid](#anti-patterns-to-avoid)

## Read-When Index

Each file sits under this skill's base directory. Read one only when its
condition matches the code under review.

| File                                   | Read when                                                                 |
| -------------------------------------- | ------------------------------------------------------------------------- |
| `references/typing.md`                 | The diff adds or changes annotations, type aliases, or generics           |
| `references/pattern-matching.md`       | The diff contains a `match` statement                                     |
| `references/data-models.md`            | The code defines dataclasses, attrs classes, or Pydantic models           |
| `references/async.md`                  | The code uses `asyncio`, `async def`, or an async library                 |
| `references/api-design-performance.md` | The diff adds decorators, context managers, or protocols, or a hot loop   |
| `references/modern-python.md`          | You are about to suggest newer syntax, or the code imports a removed module |

Out of scope here, use the sibling skill instead:

- Docstrings and comments: `python-documentation-standards`.
- Injection, secrets, subprocess, path traversal, TLS, and other security
  detail: `python-security-guide`. The severity entries below still apply.
- Test design: `python-testing-patterns`.

## Scope and Precedence

- Baseline is PEP 8 plus the Google Python Style Guide. The project's own
  configuration (`pyproject.toml`, `ruff.toml`, `setup.cfg`) and established
  conventions win where they differ.
- Formatting belongs to the formatter and linter. Do not report anything
  `ruff format` or `ruff check` enforces: whitespace, indentation, blank
  lines, import order, quote style, line length.
- Line length default is 88 (the ruff and black default). Use the project's
  `[tool.ruff] line-length` when it sets one. Never apply PEP 8's 79.
- Check the project's `requires-python` before suggesting newer syntax.
  Python 3.14 and 3.15 have shipped; do not describe 3.12 or 3.13 as the
  newest release.

## House Calibrations

These are the judgment calls a generic review gets wrong.

- **`gather(return_exceptions=True)` is not legacy.** `TaskGroup` cancels the
  remaining tasks when one raises, so partial results are lost.
  `gather(return_exceptions=True)` runs every task to completion and returns
  results and exceptions in order. Replacing one with the other is a semantic
  change: do not make it and do not approve it. Only bare `gather()` (without
  `return_exceptions`) is a MEDIUM "prefer `TaskGroup`" finding on 3.11+.
- **`%` formatting in logging calls is correct.** `logger.debug("x %s", v)`
  defers formatting. Flag f-strings inside logging calls, not `%` there.
- **Module-level constants are fine.** Flag mutable global state that code
  mutates at runtime. Internal module state prefixed with `_` is acceptable.
- **Wildcard imports** are a finding only outside `__init__.py`.
  Re-exporting through `__init__.py` is acceptable; business logic in
  `__init__.py` is MEDIUM.
- **`match` is not a better `if`.** Use it for destructuring, multiple shapes,
  or type dispatch. A `match` with one guard and a default is worse than
  `if`/`else`.
- **Retry and wrapper code must catch narrowly.** A retry decorator that
  catches bare `Exception` retries bugs such as `TypeError`. Catch the
  transient errors (`ConnectionError`, `TimeoutError`) and chain the last
  one with `raise ... from`.
- **Properties only for cheap, side-effect-free access.** Network calls, disk
  reads, or mutation behind a property are findings.
- **Proportionality.** Skip micro-optimizations in small loops. String `+=`
  in a loop matters only on hot paths (dozens of iterations or more).
- **Not findings:** missing annotations on local variables, `-> None` on
  simple private functions, restructuring equivalent syntax, magic numbers
  that are not a real bug.

## Error and Exception Handling

### Critical Rules

| Rule                              | Severity | Reference     |
| --------------------------------- | -------- | ------------- |
| Never use bare `except:`          | CRITICAL | PEP 8, Google |
| Catch specific exceptions         | HIGH     | Google Style  |
| Minimize code in try block        | HIGH     | Google Style  |
| Use `finally` for cleanup         | MEDIUM   | Google Style  |
| Use `raise X from Y` for chaining | MEDIUM   | PEP 8         |

### Exception Patterns

**Good:**

```python
try:
    value = collection[key]
except KeyError as e:
    raise ConfigurationError(f"Missing key: {key}") from e
```

**Bad:**

```python
try:
    # Too much code in try block
    data = fetch_data()
    process_data(data)
    save_data(data)
except:  # Bare except - catches everything including SystemExit
    pass  # Silently ignoring errors
```

### Strategy: Raise Low, Catch High

- Lower-level functions raise specific exceptions, chained with `from e`.
- Catch and translate at application boundaries (CLI entry points, web
  handlers, event loops).
- Add context as exceptions propagate: `raise X from e`, or `e.add_note(...)`
  and a bare `raise` on 3.11+.
- Resources use `with` (or `contextlib.contextmanager` with `try`/`finally`
  around the `yield`). An `open()` or client without a context manager is a
  resource leak.
- Leave silenced errors alone when the caller can do nothing useful with them
  (best-effort cleanup, optional cache, `finally` blocks).

## Data Structures and Mutability

- **Mutable default arguments** are CRITICAL. Use `None` and initialize inside
  the function.
- Comprehensions are for simple transforms and filters. Multiple `for`
  clauses or stacked `if` filters (three or more nested) belong in a loop.
- Use a generator expression when the result is consumed once
  (`sum(x * x for x in xs)`, `next((x for x in xs if p(x)), None)`).
- Objects that store a caller's list or dict should copy it on the way in and
  hand out copies, when external mutation would break invariants.

## Functions, Classes, and Code Structure

- Prefer functions under about 40 lines with one responsibility (Google
  style). Many parameters suggest a dataclass.
- One return type per function. Signal failure with an exception or
  `X | None`, not a sentinel string.
- Early returns over nesting three or more levels deep.
- Truthiness for sequences (`if items:`), `is None` for None, no `== True`.
- `isinstance()`, not `type(x) == T`.
- `str.startswith()`/`endswith()`, not slicing comparisons.
- `print()` used for logging in a codebase that uses `logging`, `loguru`, or
  `structlog` is a MEDIUM consistency finding.

## Imports and Module State

| Check                                    | Severity | Rationale                                            |
| ---------------------------------------- | -------- | ---------------------------------------------------- |
| `from X import *` outside `__init__.py`  | MEDIUM   | Unclear dependencies, namespace pollution            |
| Missing `__all__` in a public API module | LOW      | Consumers cannot tell public from private names      |
| Mutable global state mutated at runtime  | HIGH     | Hidden coupling, hard to test                        |
| Internal globals without `_` prefix      | MEDIUM   | Unclear intent                                       |
| Business logic in `__init__.py`          | MEDIUM   | Keep it to public re-exports                         |

## Severity Classification

### CRITICAL

Issues that affect correctness, security, or cause crashes:

- SQL injection vulnerabilities
- Command injection vulnerabilities (`shell=True`, `os.system`)
- Bare `except:` clauses (catches `SystemExit`, `KeyboardInterrupt`)
- Mutable default arguments
- Unhandled exceptions in critical paths
- Security credential exposure
- Blocking calls in async event loop
- Path traversal vulnerabilities

### HIGH

Significant issues affecting reliability or maintainability:

- Missing type annotations on public APIs
- Poor error handling (swallowing exceptions, no context)
- Resource leaks (unclosed files, connections, sessions)
- Global mutable state
- Missing critical tests
- Fire-and-forget async tasks
- Missing `case _:` default in match statements
- HTTPS verification disabled

### MEDIUM

Best practice violations:

- Google Style Guide violations that the linter does not enforce
- Missing docstrings on public APIs
- Inconsistent or misleading naming
- Complex comprehensions (3+ nested)
- Legacy type syntax (`List`, `Optional`, `Union`)
- Using bare `asyncio.gather()` (without `return_exceptions`) instead of `TaskGroup` (3.11+)

### LOW

Minor improvements:

- Comment quality
- Code organization
- Additional type hints on internal functions
- Could use newer Python features the project's `requires-python` allows

### INFO

Suggestions for optimization:

- Performance improvements
- Alternative patterns (dataclass vs attrs vs Pydantic)
- Tooling recommendations

Formatter- and linter-enforced issues (whitespace, import order, line length)
get no severity: they are not review findings.

## Quick Reference Checklist

### Before Approving

- [ ] All tests pass (including async tests)
- [ ] No critical or high severity issues
- [ ] Error handling is complete and specific
- [ ] Resources are properly managed (context managers)
- [ ] Public API is documented (see `python-documentation-standards`)
- [ ] No security vulnerabilities (see `python-security-guide`)
- [ ] Type hints on public functions (modern syntax)
- [ ] Code passes the project's lint and type checks (`ruff check`, `ruff format --check`, `mypy` where configured)

### Common Issues to Watch

1. Mutable default arguments (`def f(items=[]): ...`)
2. Bare `except:` clauses (catches `SystemExit`, `KeyboardInterrupt`)
3. SQL/command injection vulnerabilities (`shell=True`, f-string SQL)
4. Deep nesting instead of early returns
5. Missing context managers for resources
6. Global mutable state
7. Missing or legacy type annotations (`List` instead of `list`)
8. Hardcoded secrets/credentials
9. Blocking calls in async functions (defeats concurrency)
10. Fire-and-forget tasks without tracking
11. Using `Optional[X]` instead of `X | None` (Python 3.10+)
12. Missing `case _:` default in match statements
13. String concatenation in hot loops (use `"".join()`)
14. Over-complex comprehensions (3+ nested for/if)

## Anti-Patterns to Avoid

### Critical Anti-Patterns

| Anti-Pattern                    | Severity | Fix                                      |
| ------------------------------- | -------- | ---------------------------------------- |
| Mutable default arguments       | CRITICAL | Use `None` with initialization           |
| Bare `except:`                  | CRITICAL | Catch specific exceptions                |
| `from module import *`          | MEDIUM   | Explicit imports (outside `__init__.py`) |
| Inconsistent return types       | HIGH     | Single return type + exceptions          |
| `try/except` as control flow    | MEDIUM   | Use proper conditionals                  |
| String `+` in loops             | MEDIUM   | Use `"".join()` or f-strings             |
| 3+ nested comprehensions        | MEDIUM   | Use explicit loops                       |

### Examples

```python
# Bad - mutable default
def add_item(item, items=[]):  # Bug: shared list!
    items.append(item)
    return items

# Good
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items

# Bad - bare except
try:
    risky_operation()
except:  # Catches SystemExit, KeyboardInterrupt!
    pass

# Good
try:
    risky_operation()
except SpecificError as e:
    logger.error("Operation failed: %s", e)
    raise

# Bad - inconsistent returns
def find_user(user_id):
    if user_id < 0:
        return "Invalid ID"  # str
    user = db.find(user_id)
    if user:
        return user  # User object
    return None  # None

# Good - consistent return type
def find_user(user_id: int) -> User | None:
    if user_id < 0:
        raise ValueError(f"Invalid user ID: {user_id}")
    return db.find(user_id)
```
