---
name: nodejs-documentation-standards
description: "JSDoc standards for Node.js and TypeScript — syntax by declaration type, the JSDoc tag reference, what to document, common mistakes, tooling, and a quality checklist. Use when writing or auditing JSDoc on exported declarations. Also loaded by the nodejs-doc-comments agent as its knowledge base."
---
# Node.js / TypeScript Documentation Standards

A comprehensive guide to JSDoc documentation comments following the JSDoc
specification and TypeScript best practices. This document serves as the
knowledge base for the nodejs-doc-comments pattern.

## Table of Contents

1. [Core Principles](#core-principles)
2. [Syntax by Declaration Type](#syntax-by-declaration-type)
3. [JSDoc Tags Reference](#jsdoc-tags-reference)
4. [What to Document](#what-to-document)
5. [Common Mistakes](#common-mistakes)
6. [Quality Checklist](#quality-checklist)

---

## Core Principles

### The Golden Rule

JSDoc blocks appear **immediately before** the export/declaration with **no
intervening blank lines**. All exported names that carry non-obvious meaning
should have JSDoc blocks. Trivial getters/setters and re-exports are
intentionally left undocumented — a block that only restates the name is a
defect, not a fix.

### Philosophy

| Principle | Description |
|-----------|-------------|
| Complete sentences | Start with an action verb or noun phrase |
| Explain what | Not how it works internally |
| User focus | Focus on caller needs, not implementation |
| Searchable | Clear, explicit, searchable text |
| No redundancy | Avoid "processData — processes the data" |
| Add value | Provide info beyond the function signature |

### Line Length

All comment lines should stay within **80 characters** for readability.

---

## Syntax by Declaration Type

### Functions

```ts
/**
 * Fetches the user with the given ID from the database.
 *
 * @param id - The user's UUID
 * @returns The matching user object, or `null` if not found
 * @throws {DatabaseError} If the database is unreachable
 * @example
 * const user = await getUserById('abc-123');
 * if (!user) throw new NotFoundError('User not found');
 */
export async function getUserById(id: string): Promise<User | null> {
  // ...
}
```

**Rules:**

- Start with an imperative verb: "Fetches...", "Creates...", "Returns...",
  "Validates..."
- `@param name - description` (dash separator, not colon)
- `@returns` describes what is returned and when `null`/`undefined` is possible
- Omit TypeScript types in `@param` and `@returns` for `.ts` files — the
  type system is the source of truth

### Classes

```ts
/**
 * Manages a pool of database connections for efficient reuse.
 *
 * All public methods are safe for concurrent use by multiple callers.
 * Call {@link ConnectionPool.close} when done to release all connections.
 */
export class ConnectionPool {
  /**
   * Creates a new connection pool with the given configuration.
   *
   * @param config - Pool settings. `maxConnections` defaults to 10.
   */
  constructor(private readonly config: PoolConfig) {}
}
```

**Rules:**

- Use "Manages...", "Represents...", "Provides..."
- Document concurrency safety explicitly when relevant
- Document cleanup requirements (`.close()`, `.destroy()`)

### Interfaces and Type Aliases

```ts
/**
 * Configuration options for the HTTP client.
 */
export interface HttpClientOptions {
  /** Base URL prepended to all request paths. */
  baseUrl: string;

  /**
   * Request timeout in milliseconds. Defaults to 30 000.
   * Set to 0 to disable timeout.
   */
  timeout?: number;
}

/**
 * Represents a paginated response envelope from the API.
 */
export type PaginatedResponse<T> = {
  data: T[];
  /** Total number of items across all pages. */
  total: number;
  page: number;
};
```

### Constants and Enums

```ts
/** Maximum number of retry attempts for transient failures. */
export const MAX_RETRIES = 3;

/** Retry delay in milliseconds between attempts. */
export const RETRY_DELAY_MS = 500;

/**
 * HTTP status codes used by the API.
 */
export enum HttpStatus {
  /** Request succeeded. */
  OK = 200,
  /** Resource was not found. */
  NotFound = 404,
  /** Internal server error. */
  InternalServerError = 500,
}
```

### Error Variables / Sentinel Errors

```ts
/**
 * Thrown when a requested resource cannot be found.
 * Use `errors.is(err, ErrNotFound)` or `err instanceof NotFoundError` to check.
 */
export class NotFoundError extends Error {}

/**
 * Returned by database operations when a record does not exist.
 */
export const ErrNotFound = new Error('not found');
```

### Boolean Functions

```ts
/**
 * Returns `true` if the email address passes RFC 5322 format validation.
 */
export function isValidEmail(email: string): boolean {}

/**
 * Returns `true` if the user account is active and not suspended.
 */
export function isActiveUser(user: User): boolean {}
```

---

## JSDoc Tags Reference

### Core Tags

| Tag | Usage | Example |
|-----|-------|---------|
| `@param name - desc` | Document a parameter | `@param id - The user UUID` |
| `@returns desc` | Document return value | `@returns The matching user or null` |
| `@throws {Type} desc` | Document thrown errors | `@throws {ValidationError} If input is invalid` |
| `@example` | Code example block | See below |
| `@deprecated desc` | Mark as deprecated | `@deprecated Use createClientV2 instead` |
| `@remarks desc` | Additional context | `@remarks Not safe for concurrent use` |
| `@see` | Cross-reference | `@see {@link getUserById}` |
| `@since version` | Version introduced | `@since 2.0.0` |

### @example Tag

````ts
/**
 * Parses a JWT and returns its payload without verifying the signature.
 *
 * @param token - The encoded JWT string
 * @returns The decoded payload object
 * @throws {SyntaxError} If the token is malformed
 * @example
 * ```ts
 * const payload = decodeJwt(token);
 * console.log(payload.sub); // user ID
 * ```
 */
export function decodeJwt(token: string): JwtPayload {}
````

### @deprecated Tag

```ts
/**
 * Creates an HTTP client using the legacy connection model.
 *
 * @deprecated Use {@link createHttpClientV2} which supports connection
 * pooling. This function will be removed in v3.0.0.
 */
export function createHttpClient(url: string): HttpClient {}
```

### TypeScript-Specific Conventions

For `.ts` files, **omit types** from `@param` and `@returns` — they are
redundant with the TypeScript signature:

```ts
// Good in TypeScript:
/**
 * @param userId - The target user's UUID
 * @returns The user record, or `null` if not found
 */
async function getUser(userId: string): Promise<User | null>

// Bad — redundant types in TypeScript:
/**
 * @param {string} userId - The target user's UUID
 * @returns {Promise<User|null>} The user record
 */
async function getUser(userId: string): Promise<User | null>
```

For `.js` files (no TypeScript), include types:

```js
/**
 * @param {string} userId - The target user's UUID
 * @returns {Promise<User|null>} The user record, or null if not found
 */
async function getUser(userId) {}
```

---

## What to Document

### Async / Promise Behavior

Document when non-standard:

```ts
/**
 * Sends an email to the specified address.
 *
 * This function resolves as soon as the message is queued — delivery
 * is not guaranteed. Listen to the `'delivery'` event for confirmation.
 */
export async function sendEmail(to: string, subject: string): Promise<void> {}
```

### Error Values

```ts
/**
 * Thrown when a rate limit is exceeded.
 *
 * The `retryAfter` property indicates when to retry (Unix timestamp in ms).
 */
export class RateLimitError extends Error {
  /** Unix timestamp (ms) after which the request may be retried. */
  retryAfter: number;
}
```

### Cleanup Requirements

```ts
/**
 * Opens a connection to the message broker.
 *
 * Always call {@link BrokerClient.disconnect} when done to prevent
 * connection leaks, even if an error is thrown during use.
 */
export async function connect(url: string): Promise<BrokerClient> {}
```

### Parameter Constraints

```ts
/**
 * Schedules a job to run at the specified interval.
 *
 * @param intervalMs - Polling interval in milliseconds. Must be ≥ 100.
 *   Values below 100 are rounded up to prevent CPU saturation.
 * @param fn - The async function to execute. Must resolve within `intervalMs`.
 */
export function schedule(intervalMs: number, fn: () => Promise<void>): Job {}
```

### Return Value Semantics

```ts
/**
 * Searches for users matching the given filter.
 *
 * @returns A paginated result set. Returns an empty `data` array (not
 *   `null`) when no users match. The `total` field always reflects the
 *   full count across all pages.
 */
export async function searchUsers(filter: UserFilter): Promise<PaginatedResult<User>> {}
```

---

## Common Mistakes

### Redundant Comments

**Bad:**

```ts
/** Gets the user. */
export function getUser(id: string): Promise<User> {}
```

**Good:**

```ts
/**
 * Fetches the user with the given ID, including their profile and roles.
 *
 * @param id - The user's UUID
 * @returns The full user object with profile data populated
 * @throws {NotFoundError} If no user exists with the given ID
 */
export function getUser(id: string): Promise<User> {}
```

**Best (when the name already says it all):** add no block. For trivial
getters/setters or re-exports, leaving the declaration undocumented is
correct — list it as trivial in the skipped table. A lateral rewrite of an
already-adequate block is not an improvement either; leave it alone.

### Implementation Details

**Bad:**

```ts
/** Queries the users table with a prepared statement and maps rows. */
export function getUser(id: string): Promise<User> {}
```

**Good:**

```ts
/** Fetches the user with the given ID. */
export function getUser(id: string): Promise<User> {}
```

### Blank Line Between JSDoc and Declaration

**Bad:**

```ts
/**
 * Fetches a user by ID.
 */

export function getUser(id: string): Promise<User> {} // blank line = JSDoc not attached!
```

**Good:**

```ts
/**
 * Fetches a user by ID.
 */
export function getUser(id: string): Promise<User> {} // no blank line
```

### Missing @throws

**Bad:**

```ts
/**
 * Parses a JSON string and returns the result.
 */
export function parseJson(raw: string): unknown {}
```

**Good:**

```ts
/**
 * Parses a JSON string and returns the typed result.
 *
 * @param raw - The JSON string to parse
 * @returns The parsed value
 * @throws {SyntaxError} If `raw` is not valid JSON
 */
export function parseJson(raw: string): unknown {}
```

---

## Special Syntax

### Deprecation

```ts
/**
 * @deprecated Use {@link createClientV2} instead. This method does not
 * support retries and will be removed in v3.0.0.
 */
export function createClient(): Client {}
```

### Doc Links (TypeDoc / TSDoc)

```ts
/**
 * Creates a new {@link Session} from the given token.
 *
 * @see {@link SessionOptions} for available configuration options
 */
export function createSession(token: string): Session {}
```

### Module-Level Documentation

```ts
/**
 * @module auth
 *
 * Provides authentication utilities including JWT parsing, session
 * management, and permission checks.
 *
 * @example
 * ```ts
 * import { createSession, checkPermission } from './auth';
 * ```
 */
```

---

## Tools and Automation

### TypeDoc

Generate HTML docs from JSDoc + TypeScript types:

```bash
npm install --save-dev typedoc
npx typedoc --entryPoints src/index.ts --out docs
```

### TSDoc Linter

```bash
npm install --save-dev @microsoft/tsdoc @microsoft/tsdoc-config
```

### ESLint JSDoc Plugin

```bash
npm install --save-dev eslint-plugin-jsdoc

# .eslintrc.js
module.exports = {
  plugins: ['jsdoc'],
  rules: {
    'jsdoc/require-jsdoc': ['warn', { publicOnly: true }],
    'jsdoc/require-param-description': 'warn',
    'jsdoc/require-returns-description': 'warn',
  },
};
```

---

## Quality Checklist

### Before Submitting

- [ ] All exported names with non-obvious meaning have JSDoc blocks (trivial getters/setters/re-exports left undocumented)
- [ ] Comments start with an action verb or noun phrase
- [ ] Complete sentences with proper punctuation
- [ ] No blank line between JSDoc block and declaration
- [ ] Lines within 80 characters
- [ ] `@param` for all non-obvious parameters
- [ ] `@returns` describing the return value semantics
- [ ] `@throws` for known/documented error types
- [ ] Async behavior documented when non-obvious
- [ ] Cleanup requirements documented
- [ ] Deprecated exports marked with `@deprecated`

### Common Patterns

| Declaration | Pattern |
|-------------|---------|
| `async function` returning value | "Fetches...", "Creates...", "Resolves..." |
| `function` returning bool | "Returns `true` if [condition]" |
| `function` with side effects | "[Action]s [object]..." |
| `class` | "Manages...", "Represents...", "Provides..." |
| Error class/constant | "[Name] is thrown when..." |
| Constant | "[Name] is the [purpose]..." |
| Type alias | "Represents..." |

---

## References

- [JSDoc Reference](https://jsdoc.app/)
- [TSDoc Specification](https://tsdoc.org/)
- [TypeDoc Documentation](https://typedoc.org/)
- [TypeScript JSDoc Reference](https://www.typescriptlang.org/docs/handbook/jsdoc-supported-types.html)
- [Google TypeScript Style Guide](https://google.github.io/styleguide/tsguide.html)
- [eslint-plugin-jsdoc](https://github.com/gajus/eslint-plugin-jsdoc)

---

_Last updated: 2026-05-25_
