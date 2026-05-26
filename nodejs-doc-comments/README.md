# Node.js / TypeScript Doc Comments Agent

An autonomous agent that discovers exported declarations missing JSDoc
documentation, adds or improves comments following JSDoc and TSDoc standards,
and verifies TypeScript compilation.

## Pattern Structure

- **`system.md`** — Documentation framework and analysis rules
- **`agent.md`** — Autonomous execution wrapper
- **`task.md`** — Default task prompt
- **`references/nodejs-documentation-standards.md`** — JSDoc/TSDoc standards reference

## What It Does

1. Globs all `*.ts` / `*.js` source files, skipping `node_modules/`, `dist/`, tests
2. Reads each file and catalogs exported declarations without JSDoc
3. Adds or improves `/** ... */` JSDoc blocks
4. Verifies `npx tsc --noEmit` passes after edits
5. Produces a structured report of all changes

## JSDoc Conventions

The agent enforces these conventions:

- **Function comments** start with an imperative verb: "Fetches...", "Creates..."
- **Class comments** use "Manages...", "Represents...", "Provides..."
- **Boolean functions** use "Returns `true` if [condition]"
- **`@param name - description`** (dash separator, not colon)
- **`@returns`** describes what is returned and when `null`/`undefined` is possible
- **`@throws {Type}`** for documented error types
- **No blank line** between JSDoc closing `*/` and the declaration
- **No types** in `@param`/`@returns` for TypeScript files (type system is
  the source of truth)

## What Gets Documented

- Exported `function`, `async function`, `class`, `interface`, `type`, `const`, `enum`
- Constructor parameters for classes
- Complex parameter semantics (units, constraints, invariants)
- Cleanup requirements (`.close()`, `.destroy()`)
- Async/Promise behavior when non-obvious
- Deprecated exports with migration hint

## What Does NOT Get Documented

- Unexported declarations
- Trivial wrappers where the name is self-explanatory
- Test files
- Generated code files
- `.d.ts` declaration files

## Example

**Before:**

```ts
export async function getUser(id: string): Promise<User | null> {
```

**After:**

```ts
/**
 * Fetches the user with the given ID.
 *
 * @param id - The user's UUID
 * @returns The matching user, or `null` if not found
 * @throws {DatabaseError} If the database connection fails
 */
export async function getUser(id: string): Promise<User | null> {
```

## Usage

```bash
squad run nodejs-doc-comments
```

## Related Agents

- **nodejs-review** — Code quality review
- **nodejs-security-audit** — Security vulnerability audit
- **nodejs-tests** — Test coverage improvement

## References

- [JSDoc Reference](https://jsdoc.app/)
- [TSDoc Specification](https://tsdoc.org/)
- [TypeDoc](https://typedoc.org/)
- [eslint-plugin-jsdoc](https://github.com/gajus/eslint-plugin-jsdoc)
