# Node.js / TypeScript Review Agent

An autonomous agent for reviewing Node.js and TypeScript code against industry
best practices. Analyzes code quality, async patterns, error handling, and
type safety. Operates in either `edit` (fix) or `readonly` (report-only) mode.

## Pattern Structure

- **`system.md`** — Review framework and analysis rules
- **`agent.md`** — Autonomous execution wrapper
- **`task.md`** — Default task prompt
- **`references/nodejs-review-criteria.md`** — Comprehensive review criteria
- **`README.md`** — This documentation

## Review Categories

1. **Code Formatting & Style** — ESLint, Prettier, naming conventions
2. **Error Handling** — Unhandled rejections, try/catch, callback errors
3. **Async Patterns** — Missing await, Promise chains, async/await correctness
4. **Data Management** — Mutation, deep copies, null/undefined handling
5. **Type Safety** — TypeScript strict mode, type assertions, `any` usage
6. **Code Structure** — Early returns, function length, module organization
7. **API Design** — Middleware patterns, dependency injection, factories
8. **Performance** — Sync I/O in async context, event loop blocking
9. **Module Organization** — Circular deps, global state, barrel exports
10. **Security** — Input validation, SQL, secrets, eval, prototype pollution
11. **Testing** — Coverage, quality, async test patterns
12. **Reliability** — Null checks, error propagation

## Usage

### Edit Mode (apply fixes)

```bash
# Run against the current directory
squad run nodejs-review --mode edit
```

### Read-Only Mode (report only)

```bash
squad run nodejs-review --mode readonly
```

## What Gets Fixed

- Unhandled Promise rejections / empty `.catch(() => {})`
- Missing `await` on async calls
- Empty catch blocks swallowing errors
- Synchronous I/O (`readFileSync`) in Express/Fastify route handlers
- `console.log` when codebase uses structured logger (pino/winston)
- SQL string concatenation
- Hardcoded secrets
- Repeated magic literals (hoist to `const`)
- Missing input validation at route boundaries

## What Does NOT Get Fixed

- JSDoc comments, import ordering, naming style
- Test files
- Changes requiring new dependencies
- Test-asserted behavior

## Related Agents

- **nodejs-security-audit** — Deeper security-focused scan (two stages)
- **nodejs-tests** — Test coverage improvement
- **nodejs-doc-comments** — JSDoc documentation

## References

- [Node.js Best Practices](https://github.com/goldbergyoni/nodebestpractices)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/)
- [OWASP Node.js Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Nodejs_Security_Cheat_Sheet.html)
