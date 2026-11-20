---
name: golang-security-guide
description: "Go security guide: static-analysis tools, common vulnerabilities, memory safety, gRPC, cryptography, and a checklist. Use when security-auditing or hardening Go code."
---
# Go Security Guide

Go is memory-safe, garbage-collected, and strongly typed, so most Go
vulnerabilities come from how code uses the standard library, `unsafe`, cgo,
and external integrations. This file is the core: principles, tooling, a
checklist, and an index of topic files. Topic files hold the vulnerable and
secure patterns.

## Topic files (read-when index)

Topic files live in `references/` under this skill's base directory. To read
one, call `Skill("golang-security-guide")` first if you have not, then Read
the file from the skill's base directory. Read a file only when its condition
applies.

| File | Read when |
|------|-----------|
| `references/injection.md` | The code builds shell commands, SQL queries, or HTML/template output from input (command injection, SQL injection, XSS). |
| `references/resources.md` | The code handles user-supplied file paths, does size or offset arithmetic on input, uses `unsafe` or cgo, or does hashing, encryption, key or token generation. |
| `references/grpc.md` | The code imports `google.golang.org/grpc` (transport security, message size limits, stream limits, input validation at RPC boundaries). |

In the go-security-audit pipeline, squad injects this core plus the stage's
own topic file (injection stage: `references/injection.md`; resources stage:
`references/resources.md`). Other topic files still need the Skill-then-Read
step.

## Key Security Principles

- Keep Go updated. Security fixes are issued for the two most recent major
  releases only.
- Use the official tools (govulncheck, go vet) plus gosec.
- Validate and sanitize all input at system boundaries.
- Keep the dependency tree small.
- Never execute untrusted code during build or fetch.

## Security Tools

| Tool | What it catches | Command |
|------|-----------------|---------|
| govulncheck | Known vulnerabilities from the Go vulnerability database, reported only when your code reaches the vulnerable function | `govulncheck ./...` (`-json` for machine output) |
| gosec | Insecure code patterns by AST rule, mapped to CWE | `gosec ./...`; `gosec -fmt=json -out=results.json ./...`; `gosec -include=G401,G501 ./...` |
| go vet | Suspicious constructs (printf misuse, unreachable code, goroutine mistakes) | `go vet ./...` |
| Race detector | Data races that actually occur during a test or program run (64-bit only; misses races that do not execute) | `go test -race ./...` |
| staticcheck | Bugs and simplifications beyond vet | `staticcheck ./...` |
| golangci-lint | Aggregates many linters, including gosec | `golangci-lint run` |
| osv-scanner | Known vulnerabilities in go.mod dependencies from OSV | `osv-scanner --lockfile=go.mod` |
| go mod verify | Module cache contents that no longer match go.sum | `go mod verify` |

Install commands:

```bash
go install golang.org/x/vuln/cmd/govulncheck@latest
go install github.com/securego/gosec/v2/cmd/gosec@latest
go install honnef.co/go/tools/cmd/staticcheck@latest
go install github.com/google/osv-scanner/cmd/osv-scanner@latest
```

gosec rule IDs worth knowing when reading its output:

| Rule | Issue |
|------|-------|
| G101 | Hardcoded credentials |
| G102 | Binding to all interfaces |
| G103 | Use of `unsafe` |
| G201, G202 | SQL built with format strings or concatenation |
| G204 | `os/exec` command execution to audit |
| G301, G302, G306 | Loose directory or file permissions |
| G303 | Temp file at a predictable path |
| G304 | File path from tainted input |
| G305 | Path traversal when extracting a zip archive |
| G401 | MD5 or SHA-1 in use |
| G501, G502, G505 | Blocklisted imports `crypto/md5`, `crypto/des`, `crypto/sha1` |

gosec is static only: it misses runtime-dependent flaws and reports false
positives, so confirm every hit against the code.

A minimal CI job runs `govulncheck ./...`, `gosec ./...` (or golangci-lint
with gosec enabled), `go vet ./...`, `go test -race ./...`, and
`go mod verify`. Each catches a different class: known-vulnerable
dependencies, insecure patterns in your code, suspicious constructs, runtime
data races, and tampered modules.

## Security Checklist

### Tooling

- [ ] `govulncheck ./...` runs in CI
- [ ] `gosec ./...` (or golangci-lint with gosec) runs on all code
- [ ] `go vet ./...` and `go test -race ./...` run before merge
- [ ] `go mod verify` runs in CI; dependencies are pinned in go.mod

### Input Validation and Injection

- [ ] SQL uses parameterized queries, never string building
- [ ] HTML output uses `html/template`, never `text/template` or direct writes
- [ ] No `template.HTML`, `template.JS`, `template.URL`, `template.CSS`, or
      `template.HTMLAttr` conversions of user data
- [ ] No shell invocation (`sh -c`, `bash -c`) with input; allowlists, not
      denylists, where a command must vary
- [ ] Responses set an explicit Content-Type
- [ ] gRPC request messages are validated at the handler boundary

### Files and Paths

- [ ] User-supplied paths are confined (`os.OpenRoot`, `filepath.IsLocal`, or
      Clean + Join + prefix check)
- [ ] Temp files come from `os.CreateTemp`, not predictable names

### Memory Safety

- [ ] Every `unsafe` use is justified and never takes offsets from input
- [ ] Size and offset arithmetic on input is overflow-checked
- [ ] `C.CString` allocations are freed; cgo pointer-passing rules are followed

### Cryptography and Secrets

- [ ] `crypto/rand`, never `math/rand`, for tokens, keys, nonces, and IDs
- [ ] Passwords hashed with bcrypt, scrypt, or Argon2, never a plain hash
- [ ] Encryption uses an AEAD (AES-GCM) with a unique nonce per message
- [ ] TLS 1.2 or later; no `InsecureSkipVerify: true` outside tests
- [ ] No credentials in source; secrets come from the environment or a
      secret manager

### Network and Resources

- [ ] HTTP clients and servers set timeouts (no bare `http.DefaultClient` for
      external calls)
- [ ] gRPC connections use transport credentials, not plaintext
- [ ] `resp.Body`, `rows`, and files are closed

### Error Handling

- [ ] Internal errors and stack traces are not returned to clients
- [ ] Logs carry context but never secrets or credentials
- [ ] Error returns are checked, not discarded

## Official References

- [Go Security Policy](https://go.dev/doc/security/)
- [Security Best Practices for Go Developers](https://go.dev/doc/security/best-practices)
- [Go Vulnerability Database](https://pkg.go.dev/vuln/)
- [OWASP Go Secure Coding Practices Guide](https://owasp.org/www-project-go-secure-coding-practices-guide/)
- [gosec](https://github.com/securego/gosec)
