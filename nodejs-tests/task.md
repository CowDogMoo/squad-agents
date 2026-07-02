Analyze this codebase's test coverage and bring each module to 75%
coverage (unless the caller specifies a different target).

Discover all source files, measure baseline coverage with
`npm test -- --coverage --passWithNoTests` or `npx jest --coverage --passWithNoTests`,
then write tests for each module below target. Use per-file coverage percentages
from Jest's text reporter.

IMPORTANT CONSTRAINTS:

- Target is 75% PER MODULE, not just overall
- Entry point files (index.ts, bin/cli.ts): aim for 50-60%,
  document untestable functions
- Only create/modify `*.test.{js,ts}` or `*.spec.{js,ts}` files — never
  edit source code
- Parameterized tests (`it.each`/`test.each`) for 2+ similar cases
- Strict 1:1 naming: `foo.ts` → `foo.test.ts`
- Use Write (not Edit) for new test files
- Reset mocks in `beforeEach` — no shared state between tests
- Mock external deps with `jest.mock`/`vi.mock` at module boundaries
- Budget: 200 iterations max, 20 per module. Wind down early if needed
- Phase 1 is MANDATORY — always run gap analysis even if above target
