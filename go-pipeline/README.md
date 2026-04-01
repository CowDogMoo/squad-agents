# go-pipeline

Orchestrator agent that runs `go-review`, `go-tests`, `go-doc-comments`, and
optionally `go-cobra` sequentially with context passing to avoid redundant work.

## Overview

The `go-pipeline` agent coordinates up to four child agents in order:

1. **go-review** — fix code quality and best-practice issues
2. **go-tests** — fill test coverage gaps
3. **go-doc-comments** — add missing doc comments
4. **go-cobra** — fix Cobra/Viper CLI violations (when a Cobra root command is detected)

Each agent receives a summary of what the previous agent changed, so it skips
files and declarations that were already handled.

## Usage

```bash
# Run the full pipeline against the current directory
squad run --agent go-pipeline

# Run against a specific Go project
squad run --agent go-pipeline --working-dir /path/to/go-project

# Specify model and provider
squad run --agent go-pipeline --model claude-opus-4-6 --provider anthropic
```

## Example

```bash
squad run --agent go-pipeline \
  --working-dir /home/user/my-go-service \
  --model claude-opus-4-6 \
  --provider anthropic \
  --max-iterations 50 \
  --api-key "$YOUR_API_KEY"
```

### Example Output

```markdown
## Pipeline Summary

### Stage 1: go-review
**Files modified:** 3
- cmd/server.go — added context.Context to goroutine, fixed goroutine leak
- internal/db/pool.go — replaced bare `panic()` with returned error
- internal/api/handler.go — added early returns to reduce nesting

### Stage 2: go-tests
**Tests added:** 9
**Coverage:** 45% → 72%
- internal/db/pool_test.go — 4 tests (connection lifecycle, error paths)
- internal/api/handler_test.go — 5 tests (HTTP handler table-driven tests)

### Stage 3: go-doc-comments
**Doc comments added:** 11
- internal/db/pool.go — `Pool`, `NewPool`, `Acquire`, `Release`
- internal/api/handler.go — `Handler`, `ServeHTTP`, `healthCheck`
- cmd/server.go — package comment, `Run`

### Stage 4: go-cobra (skipped)
No Cobra root command detected.

## Validation
- `go build ./...`: PASS
- `go test ./...`: PASS (23 tests)
- `go vet ./...`: PASS
```

## Children

| Order | Agent | Purpose |
|-------|-------|---------|
| 1 | go-review | Code quality and best-practice fixes |
| 2 | go-tests | Test coverage analysis and gap filling |
| 3 | go-doc-comments | Exported declaration documentation |
| 4 | go-cobra | Cobra/Viper CLI fixes (conditional) |

## Version

0.1.0
