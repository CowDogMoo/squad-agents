# Type Annotations

Read when the diff adds or changes annotations, type aliases, or generics.

## Guidelines (Google Style, PEP 484)

| Check                                     | Severity | Rationale                 |
| ----------------------------------------- | -------- | ------------------------- |
| Annotate public APIs                      | HIGH     | Documentation and tooling |
| Use `X \| None` not `Optional[X]` (3.10+) | LOW      | Modern syntax             |
| Annotate complex functions                | MEDIUM   | Clarity                   |
| Import types correctly                    | MEDIUM   | Avoid runtime overhead    |

Parameters take abstract `collections.abc` types (`Sequence`, `Mapping`,
`Iterable`); return types name the concrete type (`list[str]`). Give complex
types an alias instead of repeating them.

## Generics

```python
from typing import TypeVar

T = TypeVar('T')

def first_or_none(items: Sequence[T]) -> T | None:
    return items[0] if items else None
```

## Modern Type Hints (Python 3.9-3.12)

**Use built-in generics, not typing aliases:**

```python
# Good (Python 3.9+)
def process(items: list[str], config: dict[str, int]) -> tuple[str, int]:
    pass

# Avoid (legacy)
from typing import List, Dict, Tuple
def process(items: List[str], config: Dict[str, int]) -> Tuple[str, int]:
    pass
```

**Use union syntax, not Union/Optional:**

```python
# Good (Python 3.10+)
def fetch(id: int | str) -> User | None:
    pass

# Avoid (legacy)
from typing import Union, Optional
def fetch(id: Union[int, str]) -> Optional[User]:
    pass
```

**Type aliases with `type` statement (Python 3.12+):**

```python
# Good (Python 3.12+)
type UserID = int
type UserMapping = dict[UserID, User]

# Alternative for older Python
from typing import TypeAlias
UserID: TypeAlias = int
```
