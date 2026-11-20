# Python 3.11 to 3.13 Features

Read when the project's `requires-python` allows 3.11 or later and you are
deciding whether to suggest newer syntax, or when the code imports a stdlib
module that may have been removed.

This file covers features through Python 3.13. Python 3.14 (October 2025) and
3.15 (October 2026) have shipped since and are not covered here. Check the
project's `requires-python` before suggesting any feature: syntax newer than
the minimum supported version is a bug, not a modernization.

## Python 3.11

- Exception notes: `e.add_note("While processing: ...")` adds context while
  re-raising the same exception.
- Exception groups and `except*`, mostly seen with `TaskGroup`. See
  `async.md`.
- `asyncio.TaskGroup` for structured concurrency. See `async.md` before
  suggesting it as a replacement for `gather`.

## Python 3.12

| Feature                      | PEP     | Review impact                          |
| ---------------------------- | ------- | -------------------------------------- |
| Relaxed f-strings            | PEP 701 | Nested quotes, multiline, comments     |
| `type` statement for aliases | PEP 695 | Cleaner alias and generic syntax       |

**Relaxed f-strings (PEP 701):**

```python
# Python 3.12+ - nested quotes, multiline, comments allowed
name = "world"
message = f"Hello {
    name.upper()  # Can include comments now
}"

# Nested quotes without escaping
data = f"User: {user['name']}"  # Previously required: user[\"name\"]
```

**Type statement (PEP 695):**

```python
# Python 3.12+ - cleaner type alias syntax
type Vector = list[float]
type UserID = int
type Callback[T] = Callable[[T], None]

# Generic type aliases
type ListOrSet[T] = list[T] | set[T]
```

## Python 3.13

| Feature                      | PEP     | Review impact                           |
| ---------------------------- | ------- | --------------------------------------- |
| Free-threaded build          | PEP 703 | Experimental in 3.13; no-GIL builds     |
| JIT compiler                 | PEP 744 | Experimental in 3.13                    |
| `locals()` defined semantics | PEP 667 | Predictable mutation behavior           |
| Dead batteries removed       | —       | Legacy modules removed (list below)     |

**Removed modules (dead batteries):**

These were deprecated in 3.11-3.12 and removed in 3.13. An import of any of them
fails on 3.13 and later, so flag it when the project supports 3.13+:
`aifc`, `audioop`, `cgi`, `cgitb`, `chunk`, `crypt`, `imghdr`, `mailcap`,
`msilib`, `nis`, `nntplib`, `ossaudiodev`, `pipes`, `sndhdr`, `spwd`,
`sunau`, `telnetlib`, `uu`, `xdrlib`.
