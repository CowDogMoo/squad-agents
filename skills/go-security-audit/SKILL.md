---
name: go-security-audit
description: "Runs a parallel Go security audit by fanning out two specialized subagents at once — go-security-injection (command/SQL injection, XSS, input validation) and go-security-resources (temp files, path traversal, crypto, secrets, HTTP/TLS, unsafe, error leaks) — then verifies the build and tests. Use when asked to security-audit, harden, or scan a Go codebase for vulnerabilities. Say \"readonly\" or \"report only\" to audit without applying fixes."
argument-hint: "[path] (Go module dir or package; defaults to the repo root)"
---

# Go security audit (parallel)

Audit a Go codebase for security vulnerabilities using parallel sectioning: two
focused subagents review disjoint vulnerability classes concurrently, then a
gate verifies nothing broke. Splitting the work keeps each reviewer's context
narrow and lets the two passes run at the same time.

**Target:** `$ARGUMENTS` — the Go module directory or package to audit. If empty,
use the repository root (the current working directory).

**Mode:** Default is **fix in place**. If the caller's request says "readonly",
"report only", "analysis only", or "do not modify", pass that instruction
through to both subagents so they report findings without editing, and skip the
gates (nothing changed).

## Step 1 — Fan out (run BOTH in parallel)

In a **single message**, launch both subagents with the Agent tool so they run
concurrently. Give each the target path (and the readonly instruction if the
caller asked for it):

- **go-security-injection** — command injection, SQL injection, XSS, input
  validation.
- **go-security-resources** — insecure temp files, path traversal, weak crypto,
  hardcoded secrets, HTTP client misconfig, TLS issues, unsafe code, error
  information leaks.

Wait for both to finish and collect their findings.

## Step 2 — Gate (skip in readonly mode)

After both subagents complete, run from the target dir, in order:

1. **`go build ./...`** — if it FAILS, report the build error and stop.
2. **`go test ./...`** — if it FAILS, report the failing tests.

A failing gate means a fix introduced a regression; surface it clearly rather
than reporting the audit as clean.

## Step 3 — Consolidated report

Merge both subagents' results into one report:

- Findings grouped by **severity** (CRITICAL → HIGH → MEDIUM → LOW), each line:
  `file:line — CWE-id — what — fix applied / reported-only`.
- Note which subagent found each issue (injection vs resources) where useful.
- Gate status: `go build ./...` and `go test ./...` — PASS / FAIL (with output
  on failure), or `skipped (readonly)`.

Do not paste full file contents — applied fixes are already on disk.
