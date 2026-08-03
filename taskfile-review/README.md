# Taskfile Review Agent

Autonomous Taskfile review agent that discovers configuration issues, fixes
best-practice violations, and verifies the result parses correctly.

Works on any [go-task](https://taskfile.dev) Taskfile regardless of what
language the project is written in — `go-task` is the tool's name, not a
constraint on the codebase.

## Usage

### Fix Mode (default)

Review and fix all Taskfile issues:

```bash
task run:taskfile-review MODEL=gpt-5.2-codex PROVIDER=openai API_KEY="$YOUR_API_KEY"
```

### Analyze Mode (readonly)

Analyze without applying fixes:

```bash
task run:taskfile-review-analyze MODEL=gpt-5.2-codex PROVIDER=openai API_KEY="$YOUR_API_KEY"
```

## What It Reviews

- **Structure** - version field, schema comment, file organization
- **Variables** - declaration, scoping, hardcoded values, secrets
- **Task Design** - naming, desc, summary, preconditions
- **Commands** - execution, chaining, multi-line, silent mode
- **Dependencies** - ordering, circular deps, parallel vs sequential
- **Error Handling** - preconditions, status checks, ignore_error usage
- **Security** - secrets, input validation, path safety
- **Includes** - external taskfiles, variable passing, remote includes
- **Output** - logging, echo, silent mode usage

## Severity Levels

| Level | Description |
|-------|-------------|
| CRITICAL | Security issues, syntax errors that break parsing |
| HIGH | Missing required elements, hardcoded values, no error handling |
| MEDIUM | Best practice violations, inconsistent naming |
| LOW | Minor improvements, style consistency |
| INFO | Suggestions for optimization |

## Output

- Fix mode: Applies fixes and produces a report to `/tmp/squad-taskfile-review.txt`
- Analyze mode: Produces a report to `/tmp/squad-taskfile-review-analysis.txt`

## Example

### Input (Taskfile.yaml)

```yaml
version: '3'

tasks:
  build:
    cmds:
      - go build -o bin/app .

  test:
    cmds:
      - go test ./...

  deploy:
    cmds:
      - scp bin/app admin:password123@prod-server:/opt/app
      - ssh admin@prod-server "systemctl restart app"

  lint:
    cmds:
      - golangci-lint run
```

### Example Output

```markdown
## Changes Summary

Fixed 3 issues in Taskfile.yaml: added missing task descriptions, replaced
hardcoded credentials with variable reference, and added dependency ordering.

## Issues Found and Fixed

### Hardcoded Credentials in Deploy Task
**Severity:** CRITICAL
**Category:** Security
**File:** Taskfile.yaml
**Line:** 12
**What was changed:** Replaced inline password with a variable reference and
added a precondition to verify the variable is set.
**Why:** Credentials must never appear in plain text in task definitions.

### Missing Task Descriptions
**Severity:** MEDIUM
**Category:** Task Design
**File:** Taskfile.yaml
**What was changed:** Added `desc` fields to build, test, deploy, and lint tasks.
**Why:** Descriptions are required for `task --list` output and discoverability.

### No Dependency Between Build and Deploy
**Severity:** HIGH
**Category:** Dependencies
**File:** Taskfile.yaml
**Line:** 11
**What was changed:** Added `deps: [build]` to the deploy task.
**Why:** Deploying without building first can ship stale binaries.

## Validation
- `task --list`: PASS
```

## References

The agent uses these knowledge bases:

- `references/taskfile-best-practices.md` - Review criteria and anti-patterns
- `references/go-taskfile-standards.md` - Idiomatic Taskfile patterns
