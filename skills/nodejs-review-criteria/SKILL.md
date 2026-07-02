---
name: nodejs-review-criteria
description: "Reference knowledge base for the nodejs-review agent. Loaded by that agent on its first iteration when the host has not already injected it; not intended for direct invocation."
---
# Node.js / TypeScript Code Review Criteria

A comprehensive guide to reviewing Node.js and TypeScript code for quality, correctness, performance, and adherence to best practices. This document serves as the knowledge base for the nodejs-review pattern.

## Table of Contents

1. [Review Philosophy](#review-philosophy)
2. [Code Formatting and Style](#code-formatting-and-style)
3. [Error Handling](#error-handling)
4. [Async Patterns](#async-patterns)
5. [Data Management](#data-management)
6. [Type Safety](#type-safety)
7. [Code Structure](#code-structure)
8. [API Design Patterns](#api-design-patterns)
9. [Performance](#performance)
10. [Module Organization](#module-organization)
11. [Documentation](#documentation)
12. [Security Considerations](#security-considerations)
13. [Testing](#testing)
14. [Severity Classification](#severity-classification)

---

## Review Philosophy

### Core Principles

**Clarity Over Cleverness**
Node.js code is often asynchronous and callback-heavy. Prefer explicit, readable patterns over concise but cryptic ones.

**Fail Fast and Loudly**
Unhandled rejections and swallowed errors are production incidents waiting to happen. Every error path must be deliberate.

**Constructive Feedback**

- Be educational, not critical
- Explain the "why" behind suggestions
- Provide concrete examples with code
- Acknowledge good practices
- Prioritize actionable feedback
- Focus on idiomatic Node.js patterns, not personal preferences

---

## Code Formatting and Style

### Mandatory Checks

| Check | Severity | Rationale |
|-------|----------|-----------|
| ESLint / Prettier configured | HIGH | Consistent style across team |
| `const` for immutable bindings | MEDIUM | Prevent accidental reassignment |
| `===` over `==` | HIGH | Prevents type coercion bugs |
| Consistent semicolons | LOW | Team style consistency |
| camelCase for variables/functions | MEDIUM | Node.js convention |
| PascalCase for classes/types | MEDIUM | Convention |

### Import Organization

Imports should be in logical groups:

```js
// Node.js built-ins
import { readFile } from 'fs/promises';
import path from 'path';

// Third-party packages
import express from 'express';
import { z } from 'zod';

// Local modules
import { UserService } from './services/user.js';
```

### Naming Conventions

**Good:**

```ts
fetchUser        // short, clear verb
userId           // camelCase for variables
HttpClient       // PascalCase for classes
MAX_RETRIES      // SCREAMING_SNAKE for constants
```

**Bad:**

```ts
get_user_data_from_database  // underscores not idiomatic in JS
httpClient                   // inconsistent casing for class
```

---

## Error Handling

### Critical Rules

| Rule | Severity | Example |
|------|----------|---------|
| All Promise rejections handled | CRITICAL | `.catch(() => {})` empty handler — EXCEPT intentional fire-and-forget (must have a non-empty `.catch`) and promises deliberately returned for the caller to await; verify by tracing the call site |
| Callback first-arg errors checked | HIGH | `if (err) return cb(err)` |
| No swallowed `try/catch` | HIGH | `catch {}` empty block |
| Errors wrapped with context | MEDIUM | `new Error('context: ' + err.message)` |

### Promise Error Handling

**Good:**

```ts
async function fetchUser(id: string): Promise<User> {
  const user = await db.query('SELECT * FROM users WHERE id = $1', [id]);
  if (!user) throw new Error(`User not found: ${id}`);
  return user;
}

// At the call site — VALID only when the result is intentionally not awaited
// by any caller (genuine fire-and-forget). If a caller uses the value,
// propagate with `throw`/`await` instead of swallowing via `.catch` + log:
fetchUser(id).catch(err => logger.error({ err }, 'fetchUser failed'));
```

**Bad:**

```ts
fetchUser(id).catch(() => {}); // swallows all errors silently
```

### Callback Error Pattern

**Always check the first argument:**

```ts
fs.readFile(path, 'utf8', (err, data) => {
  if (err) {
    return callback(new Error(`Failed to read ${path}: ${err.message}`));
  }
  // process data
});
```

### Try/Catch in Async Functions

**Good:**

```ts
async function processOrder(id: string) {
  try {
    const order = await fetchOrder(id);
    await chargePayment(order);
  } catch (err) {
    logger.error({ err, orderId: id }, 'processOrder failed');
    throw new Error(`Order processing failed for ${id}: ${err.message}`);
  }
}
```

**Bad:**

```ts
async function processOrder(id: string) {
  try {
    const order = await fetchOrder(id);
    await chargePayment(order);
  } catch {} // swallows errors — never acceptable
}
```

---

## Async Patterns

### Critical Checks

| Check | Severity | Impact |
|-------|----------|--------|
| `await` not missing on async calls | CRITICAL | Silent failures — EXCEPT a promise deliberately returned for the caller to await (verify by tracing the call site); do NOT blindly add `await` |
| No fire-and-forget without `.catch` | CRITICAL | Unhandled rejections — EXCEPT intentional fire-and-forget that already has a non-empty `.catch` |
| No `async` functions returning ignored Promises | HIGH | Error propagation lost |
| No mixing callbacks + async/await | HIGH | Confused control flow |

### Missing Await

**Good:**

```ts
const user = await fetchUser(id);
```

**Bad:**

```ts
const user = fetchUser(id); // returns Promise<User>, not User
```

### Fire-and-Forget

Only acceptable with explicit error logging:

```ts
// Acceptable fire-and-forget — error is handled:
sendWelcomeEmail(user).catch(err =>
  logger.warn({ err, userId: user.id }, 'welcome email failed')
);
```

**Never:**

```ts
sendWelcomeEmail(user); // rejection may crash the process
```

### Async in Express Middleware

**Good — wrap async handlers:**

```ts
app.get('/users/:id', async (req, res, next) => {
  try {
    const user = await userService.getById(req.params.id);
    res.json(user);
  } catch (err) {
    next(err); // pass to Express error handler
  }
});
```

**Bad:**

```ts
app.get('/users/:id', async (req, res) => {
  const user = await userService.getById(req.params.id); // unhandled rejection
  res.json(user);
});
```

### Promise.all vs Sequential Awaits

Use `Promise.all` for independent concurrent operations:

```ts
// Good — concurrent:
const [user, orders] = await Promise.all([
  fetchUser(id),
  fetchOrders(id),
]);

// Bad — sequential when independent:
const user = await fetchUser(id);
const orders = await fetchOrders(id);
```

---

## Data Management

### Null/Undefined Handling

**Good — explicit guards:**

```ts
function getDisplayName(user: User | null): string {
  if (!user) return 'Anonymous';
  return user.name ?? user.email;
}
```

**Bad:**

```ts
function getDisplayName(user: User | null): string {
  return user.name; // TypeError if user is null
}
```

### Immutability

Prefer immutable updates:

```ts
// Good:
const updated = { ...user, email: newEmail };

// Bad — mutates shared state:
user.email = newEmail;
```

### Deep Copies

Only deep-copy when necessary; use `structuredClone` (Node 17+) or `JSON.parse(JSON.stringify(x))` for plain objects:

```ts
// Good for plain objects:
const copy = structuredClone(config);

// BAD — misses prototype chain, Date objects, etc.:
const copy = Object.assign({}, config);  // shallow only
```

---

## Type Safety

### Critical Checks

| Check | Severity | Rationale |
|-------|----------|-----------|
| No unchecked `as` casts on external input | CRITICAL | Runtime type errors |
| `strict: true` in tsconfig | HIGH | Catches null/undefined bugs |
| No `any` in new code | MEDIUM | Defeats TypeScript |
| No `@ts-ignore` without comment | MEDIUM | Hides real bugs |

### Type Assertions

**Good — validate before asserting:**

```ts
const data = JSON.parse(raw);
if (!isUserSchema(data)) throw new Error('Invalid user payload');
const user = data as User; // safe after validation
```

**Bad — blind assertion on external input:**

```ts
const user = JSON.parse(raw) as User; // crashes if schema is wrong
```

### Avoiding `any`

**Use `unknown` for untyped input, then narrow:**

```ts
function processInput(value: unknown): string {
  if (typeof value !== 'string') throw new TypeError('Expected string');
  return value.toUpperCase();
}
```

---

## Code Structure

### Early Returns

**Good:**

```ts
if (!user) return res.status(404).json({ error: 'Not found' });
// continue with user
```

**Bad — deep nesting:**

```ts
if (user) {
  if (user.isActive) {
    if (user.hasPermission) {
      // deeply nested logic
    }
  }
}
```

### Function Length

- Functions over 40 lines should be candidates for splitting
- A single function should do one thing

### Variable Scope

- Declare `const`/`let` close to usage
- Minimize scope — avoid `var`

---

## API Design Patterns

### Middleware Pattern (Express)

```ts
function authenticate(req: Request, res: Response, next: NextFunction) {
  const token = req.headers.authorization?.replace('Bearer ', '');
  if (!token) return res.status(401).json({ error: 'Unauthorized' });
  try {
    req.user = verifyToken(token);
    next();
  } catch (err) {
    next(new AuthError('Invalid token'));
  }
}
```

### Repository Pattern

```ts
interface UserRepository {
  getById(id: string): Promise<User | null>;
  create(user: CreateUserDto): Promise<User>;
  update(id: string, patch: Partial<User>): Promise<User>;
  delete(id: string): Promise<void>;
}
```

### Factory Functions

```ts
function createHttpClient(baseUrl: string, options?: ClientOptions): HttpClient {
  const timeout = options?.timeout ?? 30_000;
  return {
    get: (path: string) => fetch(`${baseUrl}${path}`, { signal: AbortSignal.timeout(timeout) }),
  };
}
```

---

## Performance

### Synchronous I/O

| Pattern | Impact | Use Case |
|---------|--------|----------|
| `fs.readFileSync` in handler | CRITICAL | Never in request path |
| `child_process.execSync` | HIGH | Only in CLI scripts |
| `fs.promises.readFile` | OK | Async file I/O |
| Streaming large files | BEST | Large file transfers |

### Event Loop Blocking

CPU-intensive work blocks the event loop for all concurrent requests:

```ts
// Bad — blocks event loop:
app.get('/hash', (req, res) => {
  const hash = computeExpensiveHash(req.body.data); // blocks
  res.json({ hash });
});

// Good — offload to worker thread or child process:
app.get('/hash', async (req, res) => {
  const hash = await workerPool.run('computeHash', req.body.data);
  res.json({ hash });
});
```

### Memory Leaks

| Pattern | Severity | Fix |
|---------|----------|-----|
| Event listeners not removed | HIGH | `emitter.removeListener` or `once` |
| Timers not cleared | HIGH | `clearTimeout`/`clearInterval` |
| Large closures in long-lived objects | MEDIUM | Dereference when done |
| Accumulating data in module-level arrays | HIGH | Use LRU cache or limit size |

---

## Module Organization

### Circular Dependencies

Circular imports cause subtle initialization bugs:

```
// Bad: a.ts imports b.ts, b.ts imports a.ts
```

Use dependency injection or restructure to a shared module.

### Barrel Exports

Barrel `index.ts` files are convenient but can cause slow startup:

```ts
// OK for small modules
export { UserService } from './user.service.js';
export { OrderService } from './order.service.js';

// Bad — re-exporting everything from large subtrees slows bundling
export * from './all-services/index.js';
```

### Global State

Avoid module-level mutable state:

```ts
// Bad:
let requestCount = 0; // module-level mutable state

// Good — encapsulate:
export function createMetrics() {
  let requestCount = 0;
  return {
    increment: () => ++requestCount,
    value: () => requestCount,
  };
}
```

---

## Documentation

### Requirements

Exported functions and classes must have JSDoc comments:

```ts
/**
 * Fetches a user by their unique identifier.
 *
 * @param id - The user's UUID
 * @returns The user, or `null` if not found
 * @throws {DatabaseError} If the database connection fails
 */
export async function getUserById(id: string): Promise<User | null> {
  // ...
}
```

### Comment Quality

JSDoc is report-only at INFO severity for public entry points, and is NEVER
an edit-mode fix (edit mode bans JSDoc changes — see WHAT NOT TO FIX).

| Rule | Severity |
|------|----------|
| JSDoc on all exported functions | INFO (report-only) |
| `@param` and `@returns` documented | INFO (report-only) |
| `@throws` for known error types | INFO (report-only) |
| No implementation details in docs | LOW |

---

## Security Considerations

### Critical Checks

| Check | Severity | Impact |
|-------|----------|--------|
| Input validation at boundaries | CRITICAL | Injection attacks |
| SQL parameterization | CRITICAL | SQL injection |
| No `eval` / `new Function(str)` | CRITICAL | Code injection |
| No prototype pollution | CRITICAL | Privilege escalation |
| Secret management | CRITICAL | Credential exposure |

### Input Validation

```ts
// Good — validate with schema library:
const schema = z.object({
  email: z.string().email(),
  age: z.number().min(0).max(150),
});

function createUser(input: unknown) {
  const data = schema.parse(input); // throws ZodError on invalid input
  return db.create(data);
}
```

### SQL Queries

**Good:**

```ts
db.query('SELECT * FROM users WHERE id = $1', [userId]);
```

**Bad:**

```ts
db.query(`SELECT * FROM users WHERE id = '${userId}'`); // SQL injection!
```

---

## Testing

### Coverage Expectations

| Type | Target | Priority |
|------|--------|----------|
| Unit tests | 70%+ | HIGH |
| Integration tests | Critical paths | MEDIUM |
| E2E tests | Happy paths | LOW |

### Testing Tools (2026)

| Tool | Use Case |
|------|----------|
| Jest | Most popular test runner |
| Vitest | Fast Vite-native runner |
| Supertest | Express integration tests |
| nock / msw | HTTP mocking |

### Test Quality

- `describe`/`it` blocks for organization
- `beforeEach` to reset state
- Mock external services (db, http)
- Test error paths explicitly
- Test async functions with `await`

### Example

```ts
describe('getUserById', () => {
  it('returns the user when found', async () => {
    mockDb.query.mockResolvedValueOnce({ id: '1', name: 'Alice' });
    const user = await getUserById('1');
    expect(user).toEqual({ id: '1', name: 'Alice' });
  });

  it('returns null when not found', async () => {
    mockDb.query.mockResolvedValueOnce(null);
    const user = await getUserById('999');
    expect(user).toBeNull();
  });

  it('throws DatabaseError on connection failure', async () => {
    mockDb.query.mockRejectedValueOnce(new Error('connection refused'));
    await expect(getUserById('1')).rejects.toThrow('connection refused');
  });
});
```

---

## Severity Classification

### CRITICAL

- Unhandled Promise rejections (can crash the process)
- `eval` / `new Function(str)` / prototype pollution
- SQL injection, command injection
- Hardcoded credentials / secrets
- Missing `await` causing silent data loss

### HIGH

- Empty `catch {}` swallowing errors
- Synchronous I/O in request handlers (blocks event loop)
- Memory leaks (event listeners, timers not cleared)
- Missing error handling in Express middleware
- Unchecked type assertions on external input

### MEDIUM

- Missing input validation at system boundaries
- `console.log` when codebase uses structured logger
- `any` type in TypeScript
- Missing `@ts-ignore` justification
- Module-level mutable global state

### LOW

- Naming convention issues
- Non-idiomatic async patterns
- Minor style inconsistencies
- Missing JSDoc on exported functions

### INFO

- Performance suggestions for non-critical paths
- Advanced pattern recommendations
- Tooling recommendations

---

## Quick Reference Checklist

### Before Approving

- [ ] All tests pass
- [ ] No unhandled Promise rejections
- [ ] All async calls have `await` or `.then`/`.catch`
- [ ] No `eval` or dynamic code execution
- [ ] No hardcoded secrets
- [ ] Input validation at all system boundaries
- [ ] TypeScript strict mode (if using TS)
- [ ] No synchronous I/O in request handlers

### Common Issues to Watch

1. Missing `await` on async calls
2. Empty catch blocks swallowing errors
3. Fire-and-forget Promises without `.catch`
4. `eval()` or `new Function(str)` usage
5. Prototype pollution via `obj[userKey] = val`
6. SQL string interpolation
7. Synchronous I/O in Express handlers
8. Event listeners leaking across tests
9. Module-level mutable state

---

## References

- [Node.js Best Practices](https://github.com/goldbergyoni/nodebestpractices)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/)
- [OWASP Node.js Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Nodejs_Security_Cheat_Sheet.html)
- [Express Security Best Practices](https://expressjs.com/en/advanced/best-practice-security.html)
- [Google JavaScript Style Guide](https://google.github.io/styleguide/jsguide.html)

---

_Last updated: 2026-05-25_
