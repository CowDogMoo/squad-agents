# Structural Pattern Matching

Read when the diff contains a `match` statement (PEP 634-636, Python 3.10+).

## Basic Patterns

```python
def handle_command(command: list[str]) -> str:
    match command:
        case ["quit"]:
            return "Goodbye"
        case ["hello", name]:
            return f"Hello, {name}!"
        case ["add", *numbers]:
            return str(sum(int(n) for n in numbers))
        case _:
            return "Unknown command"
```

## Object Patterns

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float

def describe_point(point: Point) -> str:
    match point:
        case Point(x=0, y=0):
            return "Origin"
        case Point(x=0, y=y):
            return f"On Y-axis at {y}"
        case Point(x=x, y=0):
            return f"On X-axis at {x}"
        case Point(x=x, y=y) if x == y:
            return f"On diagonal at {x}"
        case _:
            return f"Point at ({point.x}, {point.y})"
```

## Guard Clauses

```python
def classify_number(n: int) -> str:
    match n:
        case x if x < 0:
            return "negative"
        case 0:
            return "zero"
        case x if x % 2 == 0:
            return "positive even"
        case _:
            return "positive odd"
```

## Best Practices

| Practice                        | Severity | Rationale                              |
| ------------------------------- | -------- | -------------------------------------- |
| Always include `case _:` default | HIGH    | Handles unexpected input               |
| Order specific before general   | HIGH     | First match wins                       |
| Use guards for conditions       | MEDIUM   | Express relationships between captures |
| Validate external data at edges | MEDIUM   | Match on typed objects internally      |

**When to use match vs if/elif:**

- **Use match**: Destructuring, multiple patterns, type-based dispatch
- **Use if/elif**: Simple boolean conditions, range checks

**Avoid:**

```python
# Bad - using match for simple conditions
match x:
    case x if x > 0:
        return "positive"
    case _:
        return "non-positive"

# Better - use if/else
if x > 0:
    return "positive"
return "non-positive"
```
