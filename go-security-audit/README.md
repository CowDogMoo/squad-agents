# go-security-audit

Composed agent that runs two security-focused stages in parallel for
comprehensive Go security auditing.

## Overview

This is a composed agent with two inline stages that run concurrently:

| Stage | Focus |
|-------|-------|
| injection | Command injection, SQL injection, XSS, input validation (CWE-78, CWE-89, CWE-79) |
| resources | Temp files, path traversal, crypto, TLS, secrets, unsafe code (CWE-377, CWE-22, CWE-319) |

After both stages complete, gates run `go build ./...` and `go test ./...` to
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

## Structure

```
go-security-audit/
  agent.yaml                 # composed manifest with inline stages
  injection-system.md        # injection stage system prompt
  injection-agent.md         # injection stage wrapper
  injection-task.md          # injection stage task
  resources-system.md        # resources stage system prompt
  resources-agent.md         # resources stage wrapper
  resources-task.md          # resources stage task
  references/
    golang-security-guide.md # shared security reference
```

## Version

0.3.0
