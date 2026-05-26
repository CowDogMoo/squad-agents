# Node.js / TypeScript Testing Patterns

A comprehensive guide to writing effective Node.js and TypeScript tests
following community best practices. This document serves as the knowledge base
for the nodejs-tests pattern.

## Table of Contents

1. [Testing Philosophy](#testing-philosophy)
2. [Parameterized Tests](#parameterized-tests)
3. [Describe/It Organization](#describeit-organization)
4. [Test Helpers and Fixtures](#test-helpers-and-fixtures)
5. [Mocking Strategies](#mocking-strategies)
6. [Async Testing](#async-testing)
7. [Coverage](#coverage)
8. [Common Patterns](#common-patterns)
9. [What Not to Test](#what-not-to-test)
10. [Express Route Testing](#express-route-testing-supertest)

---

## Testing Philosophy

### Core Principles

| Principle | Description |
|-----------|-------------|
| Simple and readable | Tests should be easy to understand at a glance |
| Test behavior | Test what the code does, not how it does it |
| Avoid over-mocking | Only mock at system boundaries |
| Clarity over DRY | Prefer clarity to avoiding repetition |
| One thing per test | Each `it` block verifies one behavior |
| Reset all state | `beforeEach` resets mocks and module state |

### Simplicity Guidelines

**DO:**

- Inline test data rather than complex fixtures
- Keep setup minimal
- Use `async/await` — never mix with `done` callbacks
- Test one thing per `it` block

**DON'T:**

- Create shared helpers unless used in many places
- Build complex hierarchies of `describe` blocks
- Mock internal implementation details
- Write tests for unlikely edge cases that cannot occur

---

## Parameterized Tests

Use `it.each` / `test.each` when you have multiple similar test cases.

### Basic Structure (Jest / Vitest)

```ts
describe('parseUrl', () => {
  it.each([
    ['valid http', 'http://example.com', { scheme: 'http', host: 'example.com' }],
    ['valid https', 'https://example.com/path', { scheme: 'https', host: 'example.com' }],
  ])('%s: parseUrl(%s)', (_, input, expected) => {
    expect(parseUrl(input)).toEqual(expected);
  });

  it.each([
    ['invalid scheme', '://invalid'],
    ['empty string', ''],
  ])('%s: throws on invalid input', (_, input) => {
    expect(() => parseUrl(input)).toThrow();
  });
});
```

### Template Literal Form (Readable Names)

```ts
it.each`
  input       | expected
  ${'hello'}  | ${'HELLO'}
  ${'world'}  | ${'WORLD'}
  ${''}       | ${''}
`('toUpperCase($input) === $expected', ({ input, expected }) => {
  expect(toUpperCase(input)).toBe(expected);
});
```

---

## Describe/It Organization

### Structure

```ts
describe('UserService', () => {
  let service: UserService;
  let mockDb: jest.Mocked<Database>;

  beforeEach(() => {
    mockDb = createMockDb();
    service = new UserService(mockDb);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('getById', () => {
    it('returns the user when found', async () => {
      mockDb.findOne.mockResolvedValueOnce({ id: '1', name: 'Alice' });
      const user = await service.getById('1');
      expect(user).toEqual({ id: '1', name: 'Alice' });
    });

    it('returns null when not found', async () => {
      mockDb.findOne.mockResolvedValueOnce(null);
      const user = await service.getById('999');
      expect(user).toBeNull();
    });

    it('throws DatabaseError on connection failure', async () => {
      mockDb.findOne.mockRejectedValueOnce(new Error('ECONNREFUSED'));
      await expect(service.getById('1')).rejects.toThrow('ECONNREFUSED');
    });
  });
});
```

---

## Test Helpers and Fixtures

### When to Create Helpers

Only create helpers when:

- Used across multiple test files
- Significantly reduces test complexity
- Makes tests more readable

### Factory Functions (avoid shared state)

```ts
// factories.ts — test-only factories
export function buildUser(overrides: Partial<User> = {}): User {
  return {
    id: 'user-123',
    name: 'Test User',
    email: 'test@example.com',
    createdAt: new Date('2026-01-01'),
    ...overrides,
  };
}
```

### Temp Files

```ts
import os from 'os';
import path from 'path';
import fs from 'fs/promises';

let tmpDir: string;

beforeEach(async () => {
  tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), 'test-'));
});

afterEach(async () => {
  await fs.rm(tmpDir, { recursive: true, force: true });
});

it('reads a file', async () => {
  const filePath = path.join(tmpDir, 'data.txt');
  await fs.writeFile(filePath, 'hello');
  expect(await readContent(filePath)).toBe('hello');
});
```

---

## Mocking Strategies

### Module-Level Mocking (Jest)

```ts
jest.mock('./database');
jest.mock('axios');

import { Database } from './database';
import axios from 'axios';

const mockDb = jest.mocked(Database);
const mockAxios = jest.mocked(axios);

beforeEach(() => {
  jest.clearAllMocks();
});
```

### Spy on Methods

```ts
it('calls logger.error on failure', async () => {
  const errorSpy = jest.spyOn(logger, 'error').mockImplementation(() => {});
  mockDb.query.mockRejectedValueOnce(new Error('DB error'));

  await expect(service.getUser('1')).rejects.toThrow('DB error');
  expect(errorSpy).toHaveBeenCalledWith(
    expect.objectContaining({ err: expect.any(Error) }),
    'getUser failed',
  );
});
```

### HTTP Mocking with MSW (Module Service Worker)

```ts
import { setupServer } from 'msw/node';
import { http, HttpResponse } from 'msw';

const server = setupServer(
  http.get('https://api.example.com/users/:id', ({ params }) => {
    return HttpResponse.json({ id: params.id, name: 'Alice' });
  }),
);

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

### When to Mock

**Do mock:**

- External services (databases, HTTP APIs)
- File system in unit tests
- Time (`jest.useFakeTimers()`)
- Crypto randomness (`jest.spyOn(crypto, 'randomBytes')`)

**Don't mock:**

- Simple value objects or pure functions
- Internal implementation details
- The module under test itself

---

## Async Testing

### async/await (Preferred)

```ts
it('resolves to user data', async () => {
  const user = await fetchUser('123');
  expect(user.name).toBe('Alice');
});

it('rejects on not found', async () => {
  await expect(fetchUser('999')).rejects.toThrow('Not found');
});
```

### Testing Promise Rejection with Assertions

```ts
it('rejects with ValidationError', async () => {
  await expect(createUser({ email: 'not-an-email' }))
    .rejects
    .toThrow('Invalid email');
});

it('rejects with the right error type', async () => {
  await expect(createUser({}))
    .rejects
    .toBeInstanceOf(ValidationError);
});
```

### Timers

```ts
jest.useFakeTimers();

it('retries after 1 second', async () => {
  const mock = jest.fn().mockRejectedValueOnce(new Error('fail')).mockResolvedValueOnce('ok');
  const resultPromise = withRetry(mock, { delay: 1000 });

  jest.advanceTimersByTime(1000);
  const result = await resultPromise;
  expect(result).toBe('ok');
  expect(mock).toHaveBeenCalledTimes(2);
});

afterEach(() => {
  jest.useRealTimers();
});
```

---

## Coverage

### Running Coverage

```bash
# Full coverage report
npm test -- --coverage

# Per-file text summary
npx jest --coverage --coverageReporters text

# Coverage for a specific file
npx jest --coverage src/services/user.service.ts
```

### Coverage Goals

| Type | Target |
|------|--------|
| Business logic | 80%+ |
| Entry points / CLI | 50-60% |
| Critical paths | 90%+ |

### What Coverage Doesn't Tell You

- Quality of assertions
- Whether error paths are properly tested
- Whether tests are meaningful
- Whether mocks accurately reflect real behavior

---

## Common Patterns

### Error Message Testing

```ts
it.each([
  [null, 'Input must not be null'],
  ['', 'Input must not be empty'],
  ['x'.repeat(1001), 'Input exceeds maximum length'],
])('validate(%s) throws "%s"', async (input, expectedMessage) => {
  await expect(validate(input)).rejects.toThrow(expectedMessage);
});
```

### Testing Context / Cancellation

```ts
it('respects AbortSignal', async () => {
  const controller = new AbortController();
  const promise = fetchWithAbort('https://api.example.com', controller.signal);
  controller.abort();
  await expect(promise).rejects.toThrow(/abort/i);
});
```

### Express Route Testing (Supertest)

```ts
import request from 'supertest';
import { app } from '../app.js';

describe('GET /users/:id', () => {
  it('returns 200 with user data', async () => {
    mockUserService.getById.mockResolvedValueOnce({ id: '1', name: 'Alice' });

    const res = await request(app).get('/users/1');

    expect(res.status).toBe(200);
    expect(res.body).toEqual({ id: '1', name: 'Alice' });
  });

  it('returns 404 when user not found', async () => {
    mockUserService.getById.mockResolvedValueOnce(null);

    const res = await request(app).get('/users/999');

    expect(res.status).toBe(404);
    expect(res.body).toHaveProperty('error');
  });

  it('returns 500 on service error', async () => {
    mockUserService.getById.mockRejectedValueOnce(new Error('DB down'));

    const res = await request(app).get('/users/1');

    expect(res.status).toBe(500);
    // Should NOT leak internal details in production:
    expect(res.body.error).not.toContain('DB down');
  });
});
```

---

## What Not to Test

### Skip Testing

- **Trivial getters/setters** without logic
- **Third-party library behavior** (trust the library)
- **TypeScript type checks** (the compiler handles these)
- **Entry-point wiring** (`app.listen(3000)`, `index.ts` DI composition)

### Example: Don't Test This

```ts
// Trivial delegation — test the underlying service instead
class UserController {
  constructor(private service: UserService) {}
  async getUser(id: string) {
    return this.service.getById(id); // pure delegation
  }
}
```

### Example: Do Test This

```ts
// Has branching logic — should test all paths
async function getUserDisplayName(id: string): Promise<string> {
  const user = await userService.getById(id);
  if (!user) return 'Anonymous';
  return user.preferredName ?? `${user.firstName} ${user.lastName}`;
}
```

---

## Quick Reference

### Test File Naming

- `foo.ts` → `foo.test.ts` (strict 1:1 mapping)
- `foo.ts` → `foo.spec.ts` (alternative, match existing project convention)
- Do NOT create `foo.extra.test.ts` or `foo.coverage.test.ts`

### Common Jest Matchers

```ts
// Equality
expect(result).toBe(42);             // strict equality (===)
expect(result).toEqual({ id: 1 });   // deep equality
expect(result).toStrictEqual(obj);   // deep + type equality

// Truthiness
expect(value).toBeTruthy();
expect(value).toBeNull();
expect(value).toBeUndefined();

// Collections
expect(arr).toHaveLength(3);
expect(arr).toContain('item');
expect(obj).toHaveProperty('key', 'value');

// Errors
expect(() => fn()).toThrow('message');
expect(fn()).rejects.toThrow('message');  // async

// Mocks
expect(mockFn).toHaveBeenCalledTimes(1);
expect(mockFn).toHaveBeenCalledWith('arg1', expect.any(Number));
```

---

## References

- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [Vitest Documentation](https://vitest.dev/guide/)
- [Supertest GitHub](https://github.com/ladjs/supertest)
- [MSW (Mock Service Worker)](https://mswjs.io/docs/)
- [Testing Library for Node.js](https://testing-library.com/)
- [Node.js Best Practices — Testing](https://github.com/goldbergyoni/nodebestpractices#4-testing-and-overall-quality-practices)

---

_Last updated: 2026-05-25_
