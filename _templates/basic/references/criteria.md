# Review Criteria

This document defines what issues the agent should look for.

## What TO Fix

- Bugs that cause incorrect behavior
- Security vulnerabilities
- Resource leaks (unclosed files, connections, etc.)
- Error handling gaps (swallowed errors, missing checks)
- Inconsistent patterns (e.g., using different logging packages)

## What NOT to Fix

- Stylistic preferences without functional impact
- Micro-optimizations (e.g., strings.Builder for 3-element loops)
- Adding type annotations where inference is clear
- Documentation/comments (unless required to explain a bug fix)
- Test code (unless explicitly requested)

## Severity Levels

### CRITICAL
- Security vulnerabilities (injection, path traversal, etc.)
- Crashes or panics in normal operation
- Data corruption or loss

### HIGH
- Bugs that cause incorrect behavior
- Resource leaks
- Missing error handling that could cause failures

### MEDIUM
- Code quality issues that hurt maintainability
- Inconsistent patterns within the codebase
- Dead code or unreachable conditions

### LOW
- Minor style inconsistencies
- Opportunities for minor improvements
- Non-blocking suggestions
