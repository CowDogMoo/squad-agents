# go-security-audit

Composed agent that runs `go-security-injection` and `go-security-resources`
in parallel for comprehensive Go security auditing.

## Overview

This is a composed agent — it has no prompts of its own. It orchestrates two
focused sub-agents that run concurrently:

| Agent | Focus |
|-------|-------|
| go-security-injection | Command injection, SQL injection, XSS, input validation (CWE-78, CWE-89, CWE-79) |
| go-security-resources | Temp files, path traversal, crypto, TLS, secrets, unsafe code (CWE-377, CWE-22, CWE-319) |

After both agents complete, gates run `go build ./...` and `go test ./...` to
verify the fixes compile and pass tests.

## Usage

```bash
# Run against the current directory
squad run --agent go-security-audit

# Run against a specific project
squad run --agent go-security-audit --working-dir /path/to/go-project

# With cost limit
squad run --agent go-security-audit --max-cost 5.00
```

## Stages

```
audit (parallel)
  ├── go-security-injection
  └── go-security-resources
       │
       ▼
  gates: go build, go test
```

## Version

0.3.0
