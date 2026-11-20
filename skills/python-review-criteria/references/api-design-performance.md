# API Design and Performance

Read when the diff adds decorators, context managers, or protocols, or touches
a hot loop, large-data path, or string building.

## Contents

- API design: decorators, context managers, protocols
- Performance: string operations, loop optimization, memory efficiency

## API Design Patterns

### Decorators

```python
import functools
from typing import Callable, TypeVar

T = TypeVar('T', bound=Callable)

# Narrow the catch to exceptions that are actually retriable (e.g. transient
# network/IO errors). Catching bare `Exception` swallows bugs like TypeError.
RETRIABLE_ERRORS = (ConnectionError, TimeoutError)

def retry(max_attempts: int = 3) -> Callable[[T], T]:
    """Retry a function on transient failure."""
    def decorator(func: T) -> T:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_error: Exception | None = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except RETRIABLE_ERRORS as e:
                    last_error = e
            # Preserve the chain so the original traceback is not lost.
            raise RuntimeError(f"failed after {max_attempts} attempts") from last_error
        return wrapper  # type: ignore
    return decorator

@retry(max_attempts=3)
def fetch_data(url: str) -> dict:
    pass
```

### Context Managers

```python
from contextlib import contextmanager
from typing import Iterator

@contextmanager
def timer(name: str) -> Iterator[None]:
    """Time a code block."""
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        logger.info(f"{name} took {elapsed:.3f}s")

# Usage
with timer("data processing"):
    process_data()
```

### Protocols (Structural Typing)

```python
from typing import Protocol

class Readable(Protocol):
    def read(self, size: int = -1) -> bytes: ...

class Writable(Protocol):
    def write(self, data: bytes) -> int: ...

def copy_data(source: Readable, dest: Writable) -> int:
    """Copy data from source to destination."""
    data = source.read()
    return dest.write(data)
```

## Performance

### String Operations

| Pattern        | Performance | Use Case                         |
| -------------- | ----------- | -------------------------------- |
| f-strings      | Fastest     | Simple formatting                |
| `str.join()`   | Fast        | Multiple concatenations          |
| `%` formatting | Medium      | Logging with deferred evaluation |
| `+` in loop    | Slow        | Avoid                            |

**Good:**

```python
# f-strings for formatting
message = f"User {user.name} logged in at {timestamp}"

# join for multiple strings
result = "".join(parts)
result = ", ".join(names)

# Logging with % for deferred evaluation
logger.debug("Processing user %s", user_id)
```

**Bad:**

```python
# String concatenation in loop
result = ""
for item in items:
    result += str(item)  # Creates new string each time
```

### Loop Optimization

```python
# Good - list comprehension (faster than loop)
squares = [x ** 2 for x in numbers]

# Good - generator for large data
total = sum(x ** 2 for x in large_numbers)

# Good - avoid repeated attribute lookup
append = result.append
for item in items:
    append(process(item))

# Good - use built-ins
if any(predicate(x) for x in items):
    pass
```

### Memory Efficiency

```python
# Good - generator for large sequences
def read_large_file(path: str) -> Iterator[str]:
    with open(path) as f:
        for line in f:
            yield line.strip()

# Good - slots for many instances
class Point:
    __slots__ = ('x', 'y')

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
```
