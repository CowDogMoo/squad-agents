# Async/Await Patterns

Read when the code uses `asyncio`, `async def`, or an async library.

## Contents

- Best practices table
- Entry point
- TaskGroup versus `gather(return_exceptions=True)`
- Async context managers and generators
- CPU-bound work
- Exception groups
- Common anti-patterns (blocking calls, fire-and-forget tasks)

## Best Practices

| Practice                              | Severity | Rationale                           |
| ------------------------------------- | -------- | ----------------------------------- |
| Use `asyncio.run()` as entry point    | HIGH     | Proper event loop management        |
| Use `TaskGroup` for concurrent tasks (but NOT as a replacement for `gather(return_exceptions=True)`) | HIGH | Structured concurrency (3.11+) |
| Use `async with` for resources        | HIGH     | Proper async cleanup                |
| Don't block the event loop            | CRITICAL | Defeats purpose of async            |

## Entry Point

```python
import asyncio

async def main() -> None:
    result = await fetch_data()
    await process_data(result)

# Always use asyncio.run() to start
if __name__ == "__main__":
    asyncio.run(main())
```

## TaskGroup (Python 3.11+, Recommended)

**Good - structured concurrency:**

```python
async def fetch_all_users(user_ids: list[int]) -> list[User]:
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(fetch_user(uid)) for uid in user_ids]
    return [task.result() for task in tasks]
```

TaskGroup advantages:

- Automatic task lifecycle management
- Proper exception handling (cancels remaining on failure)
- Cleaner than bare `asyncio.gather()` (without `return_exceptions`)

**CRITICAL: TaskGroup and gather(return_exceptions=True) are NOT equivalent.**

`TaskGroup` cancels all remaining tasks when any task raises. This means
partial results are lost. `gather(return_exceptions=True)` runs ALL tasks
to completion and returns both results and exceptions in order.

**When to use each:**

- `TaskGroup` — when all tasks must succeed or you want fail-fast behavior
- `gather(return_exceptions=True)` — when you need partial results from
  fan-out patterns (parallel queries, chunk processing, multi-API calls)

**Do NOT replace `gather(return_exceptions=True)` with `TaskGroup`.**
This is a semantic change that silently drops partial results.

**Legacy (avoid in new code ONLY when return_exceptions is not used):**

```python
# Less safe - exceptions can leave tasks running
results = await asyncio.gather(
    fetch_user(1),
    fetch_user(2),
)
```

**Still correct (do NOT replace):**

```python
# Collects ALL results including exceptions - TaskGroup cannot do this
results = await asyncio.gather(
    fetch_user(1),
    fetch_user(2),
    return_exceptions=True,
)
```

## Async Context Managers

```python
import aiofiles

async def read_config(path: str) -> dict:
    async with aiofiles.open(path) as f:
        content = await f.read()
    return json.loads(content)
```

## Async Generators

```python
async def fetch_pages(url: str) -> AsyncIterator[dict]:
    """Fetch paginated data lazily."""
    page = 1
    while True:
        data = await fetch_page(url, page)
        if not data["items"]:
            break
        for item in data["items"]:
            yield item
        page += 1

# Usage
async for item in fetch_pages(api_url):
    process(item)
```

## CPU-Bound Work

**Never block the event loop with CPU-bound operations:**

```python
import asyncio
from concurrent.futures import ProcessPoolExecutor

async def process_image(image_path: str) -> bytes:
    loop = asyncio.get_running_loop()
    # Offload CPU-bound work to process pool
    with ProcessPoolExecutor() as pool:
        result = await loop.run_in_executor(
            pool, cpu_intensive_transform, image_path
        )
    return result
```

## Exception Groups (Python 3.11+)

Handle multiple concurrent failures:

```python
async def fetch_all(urls: list[str]) -> list[Response]:
    try:
        async with asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(fetch(url)) for url in urls]
        return [t.result() for t in tasks]
    except* ConnectionError as eg:
        # Handle all ConnectionErrors from the group
        for exc in eg.exceptions:
            logger.error(f"Connection failed: {exc}")
        raise
    except* TimeoutError as eg:
        logger.warning(f"{len(eg.exceptions)} requests timed out")
        raise
```

## Common Anti-Patterns

```python
# Bad - blocking call in async function
async def bad_fetch(url: str) -> str:
    return requests.get(url).text  # Blocks event loop!

# Good - use async HTTP client
async def good_fetch(url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

# Bad - fire-and-forget tasks
async def bad_background():
    asyncio.create_task(some_task())  # No await, no tracking!

# Good - track background tasks
async def good_background():
    task = asyncio.create_task(some_task())
    try:
        await do_main_work()
    finally:
        await task  # Ensure task completes
```
