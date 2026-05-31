# OUTPUT FORMAT

**CRITICAL**: Your output MUST follow this exact structure.

## Changes Summary

[Brief overview -- 2-3 sentences max]

## Issues Found and Fixed

### [Vulnerability Title] -- CWE-XXX

**Severity:** CRITICAL/HIGH/MEDIUM/LOW
**Category:** [category]
**File:** [file path]
**Line:** [line number]

**What was changed:**
[1-2 sentences]

**Why:**
[1-2 sentences]

---

## Issues Found but Skipped

| Issue | Severity | File | Reason Skipped |
|-------|----------|------|----------------|
| [title] | [sev] | [file] | [reason] |

## Files Touched

- `path/to/file.go` -- [change description]

## Validation

- `go build ./...`: PASS/FAIL
- `go test ./...`: PASS/FAIL
