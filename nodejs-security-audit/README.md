# Node.js / TypeScript Security Audit Agent

A parallel two-stage security audit agent for Node.js and TypeScript codebases.
Both stages run concurrently, each focusing on a non-overlapping set of
vulnerability classes.

## Pattern Structure

- **`agent.yaml`** — Orchestration with two parallel stages + gates
- **`injection-system.md`** / **`injection-agent.md`** / **`injection-task.md`** — Stage 1
- **`resources-system.md`** / **`resources-agent.md`** / **`resources-task.md`** — Stage 2
- **`references/nodejs-security-guide.md`** — Comprehensive Node.js security guide

## Stages

### Stage 1: Injection

Focuses exclusively on:

- **Command Injection** — `child_process.exec` with user input, `eval()`, `new Function(str)`
- **SQL Injection** — String template literals / concatenation in DB queries
- **XSS** — `innerHTML`, `document.write`, `dangerouslySetInnerHTML` with user data
- **Prototype Pollution** — `obj[userKey] = val`, unsafe `Object.assign` from user input
- **Input Validation** — Missing validation at route handlers, WebSocket messages, CLI args

### Stage 2: Resources

Focuses exclusively on:

- **Path Traversal** — User-controlled file paths without boundary validation
- **Weak Cryptography** — `Math.random()` for security, MD5/SHA-1 for sensitive hashing
- **Hardcoded Secrets** — API keys, passwords, tokens in source code
- **SSRF** — Server-side requests to user-controlled URLs
- **Insecure TLS** — `rejectUnauthorized: false`, plain HTTP for sensitive calls
- **ReDoS** — Catastrophic regex backtracking on user-controlled strings
- **Insecure Temp Files** — Predictable names, TOCTOU races
- **Error Info Leaks** — Stack traces / internal details in HTTP responses

## Gates

After each stage, the following checks run:

1. TypeScript compilation: `npx tsc --noEmit`
2. Test suite: `npm test -- --passWithNoTests`

If a gate fails, the pipeline stops.

## Usage

```bash
squad run nodejs-security-audit
```

## What Gets Fixed

Each stage applies fixes within its category scope only:

- Replaces `exec(cmd)` with `execFile(binary, args)`
- Parameterizes SQL queries
- Adds prototype pollution key guards
- Adds Zod/Joi validation at route entry points
- Replaces `Math.random()` with `crypto.randomBytes()`
- Replaces hardcoded secrets with `process.env.*`
- Adds path traversal boundary checks
- Removes `rejectUnauthorized: false`
- Fixes catastrophic regex patterns

## What Does NOT Get Fixed

- Code quality issues with no security impact
- Changes requiring new dependencies
- Test-asserted behavior
- Issues in the other stage's scope

## Related Agents

- **nodejs-review** — General code quality review
- **nodejs-tests** — Test coverage improvement

## References

- [OWASP Node.js Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Nodejs_Security_Cheat_Sheet.html)
- [Node.js Best Practices — Security](https://github.com/goldbergyoni/nodebestpractices#6-security-best-practices)
- [ESLint Plugin Security](https://github.com/eslint-community/eslint-plugin-security)
