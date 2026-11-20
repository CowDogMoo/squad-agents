# Dataclasses, attrs, and Pydantic

Read when the code defines dataclasses, attrs classes, or Pydantic models, or
holds mutable collections on an object.

## Contents

- When to use each
- Dataclasses
- attrs
- Pydantic
- Performance comparison
- Defensive copying

## When to Use Each

| Tool        | Use Case                                    | Key Strength                |
| ----------- | ------------------------------------------- | --------------------------- |
| `dataclass` | Simple internal data grouping               | Built-in, no dependencies   |
| `attrs`     | Performance + custom validation             | Fine-grained control, fast  |
| `Pydantic`  | API validation, serialization, settings     | Comprehensive validation    |

## Dataclasses (stdlib)

**Best for:** Internal data transfer objects, configuration, simple records.

```python
from dataclasses import dataclass, field

# Modern dataclass with slots (Python 3.10+)
@dataclass(slots=True, frozen=True)
class Point:
    x: float
    y: float

# With defaults and factory
@dataclass
class Config:
    name: str
    tags: list[str] = field(default_factory=list)
    timeout: int = 30

    def __post_init__(self) -> None:
        if self.timeout < 0:
            raise ValueError("timeout must be non-negative")
```

**Key options:**

| Option     | Effect                                |
| ---------- | ------------------------------------- |
| `slots`    | Memory efficient, faster attr access  |
| `frozen`   | Immutable (hashable)                  |
| `kw_only`  | All fields keyword-only (3.10+)       |
| `order`    | Generate comparison methods           |

## attrs

**Best for:** Performance-critical code, complex validation without JSON serialization.

```python
import attrs

@attrs.define
class User:
    name: str = attrs.field(validator=attrs.validators.instance_of(str))
    age: int = attrs.field(validator=[
        attrs.validators.instance_of(int),
        attrs.validators.ge(0),
    ])
    email: str = attrs.field()

    @email.validator
    def _validate_email(self, attribute, value):
        if "@" not in value:
            raise ValueError(f"Invalid email: {value}")
```

## Pydantic

**Best for:** API request/response models, settings management, JSON serialization.

```python
from pydantic import BaseModel, Field, field_validator

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str
    age: int = Field(..., ge=0, le=150)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("Invalid email format")
        return v.lower()

    model_config = {"str_strip_whitespace": True}
```

## Performance Comparison

Performance differences are minimal for most use cases. Choose based on features needed:

- **Fastest:** `attrs` or `dataclass` without validation
- **Most features:** Pydantic (validation, serialization, settings)
- **No dependencies:** `dataclass`

## Defensive Copying

```python
class DataHolder:
    def __init__(self, items: list[str]) -> None:
        self._items = list(items)  # Copy to prevent external modification

    @property
    def items(self) -> list[str]:
        return list(self._items)  # Return copy
```
