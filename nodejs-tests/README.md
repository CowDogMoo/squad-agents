# Node.js / TypeScript Test Coverage Agent

An autonomous agent that discovers coverage gaps, writes tests, and iterates
until each module reaches the target coverage percentage (default 75%).

## Pattern Structure

- **`system.md`** — Coverage workflow, rules, output format
- **`agent.md`** — Autonomous execution wrapper
- **`task.md`** — Default task prompt
- **`references/nodejs-testing-patterns.md`** — Testing patterns and best practices

## How It Works

1. **Measure**: Runs `npm test -- --coverage` to get baseline per-file coverage
2. **Gap Analysis**: Identifies files with no test file and functions at 0%
3. **Prioritize**: Sorts modules by business logic impact and coverage gap
4. **Write**: Creates `*.test.ts` / `*.test.js` files using Jest or Vitest patterns
5. **Verify**: Runs tests after each module, checks coverage, iterates
6. **Report**: Produces a full before/after coverage report

## Coverage Targets

| Module Type | Target |
|-------------|--------|
| Business logic, services | 75% (default) |
| Entry points (`index.ts`, `bin/cli.ts`) | 50-60% |
| Critical paths | 90%+ |

## Testing Patterns Used

- `describe`/`it` blocks for organization
- `it.each`/`test.each` for parameterized cases (2+ similar cases)
- `beforeEach` for state reset and mock initialization
- `jest.mock`/`vi.mock` for external dependencies
- Supertest for Express/Fastify route integration tests
- `jest.useFakeTimers()` for timer-dependent code

## What Gets Tested

- Functions with conditional logic, loops, or error returns
- Exported functions (public API)
- Error paths with correct error types/messages
- Async functions — both resolution and rejection paths
- Express/Fastify route handlers via Supertest

## What Does NOT Get Tested

- Trivial getters/setters
- Entry-point wiring (`app.listen()`, DI composition in `index.ts`)
- Live external services
- `process.exit()` in CLI scripts

## Usage

```bash
# Default 75% target
squad run nodejs-tests

# Custom target
squad run nodejs-tests COVERAGE_TARGET=80
```

## Output

The agent produces a structured report including:

- Before/after/delta coverage percentages
- Per-module table with met/unmet status
- List of discovered gaps (files without tests, 0% functions)
- List of test functions written
- List of skipped functions with reasons

## Related Agents

- **nodejs-review** — Code quality review
- **nodejs-security-audit** — Security vulnerability audit
- **nodejs-doc-comments** — JSDoc documentation

## References

- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [Vitest Documentation](https://vitest.dev/guide/)
- [Supertest](https://github.com/ladjs/supertest)
- [MSW — Mock Service Worker](https://mswjs.io/)
