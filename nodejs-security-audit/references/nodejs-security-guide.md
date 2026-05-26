# Node.js / TypeScript Security: Comprehensive Guide to Identifying and Patching Vulnerabilities

## Table of Contents

1. [Introduction](#introduction)
2. [Security Tools and Analysis](#security-tools-and-analysis)
3. [Common Vulnerabilities](#common-vulnerabilities)
4. [Cryptography Best Practices](#cryptography-best-practices)
5. [Dependency Security](#dependency-security)
6. [Security Checklist](#security-checklist)

---

## Introduction

Node.js is widely deployed in production systems handling sensitive data. While
JavaScript's sandboxed execution prevents many low-level memory exploits, the
ecosystem has unique vulnerabilities: prototype pollution, unhandled Promise
rejections, and a rich dependency tree that expands the attack surface.

### Key Security Principles

- Validate all external input at system boundaries
- Never trust data from `req.body`, `req.params`, `req.query`, or `req.headers`
- Use parameterized queries for all database access
- Use `crypto.randomBytes()` for all security-sensitive random values
- Pin dependencies and run `npm audit` in CI
- Never expose internal error details or stack traces to clients

---

## Security Tools and Analysis

### 1. npm audit — Built-in Vulnerability Scanner

```bash
# Scan for known vulnerabilities
npm audit

# Fix automatically where possible
npm audit fix

# JSON output for CI
npm audit --json
```

### 2. Snyk — Deep Dependency Analysis

```bash
npm install -g snyk
snyk test
snyk monitor  # continuous monitoring
```

### 3. ESLint Security Plugins

```bash
npm install --save-dev eslint-plugin-security eslint-plugin-no-unsanitized

# .eslintrc.js
module.exports = {
  plugins: ['security', 'no-unsanitized'],
  extends: ['plugin:security/recommended'],
};
```

**Key rules:**
- `security/detect-non-literal-regexp` — dynamic regex from user input
- `security/detect-child-process` — exec/spawn with user input
- `security/detect-object-injection` — `obj[userKey]` prototype pollution
- `security/detect-possible-timing-attacks` — non-constant-time comparisons

### 4. SAST Tools

**Semgrep** for custom rules:

```bash
pip install semgrep
semgrep --config p/nodejs-security .
```

**CodeQL** (GitHub):
```yaml
# .github/workflows/codeql.yml
- uses: github/codeql-action/analyze@v3
  with:
    languages: javascript
```

---

## Common Vulnerabilities

### 1. Injection Attacks

#### Command Injection

**Vulnerable:**

```js
const { exec } = require('child_process');
exec('ls ' + req.query.dir, callback); // NEVER DO THIS
```

**Secure:**

```js
const { execFile } = require('child_process');
// Use execFile with separate args — never passes through shell
execFile('/bin/ls', ['-la', sanitizedDir], callback);

// Or use spawn:
const { spawn } = require('child_process');
const ls = spawn('/bin/ls', ['-la', sanitizedDir]);
```

**Prevention:**
1. Use `execFile` or `spawn` with explicit argument arrays
2. Never pass user input to `exec()`, `eval()`, or `new Function(str)`
3. Allowlist permitted values when possible

#### SQL Injection

**Vulnerable:**

```js
// NEVER DO THIS
const query = `SELECT * FROM users WHERE username='${username}'`;
db.query(query);
```

**Secure:**

```js
// node-postgres
db.query('SELECT * FROM users WHERE username = $1', [username]);

// mysql2
db.execute('SELECT * FROM users WHERE username = ?', [username]);

// Prisma (use typed methods)
prisma.user.findUnique({ where: { username } });

// Knex (avoid knex.raw with user input)
knex('users').where({ username });
```

#### eval() and Dynamic Code Execution

```js
// NEVER
eval(userCode);
new Function(userCode)();
setTimeout(userCode, 1000); // string form

// Safe alternatives
// Use a sandbox like vm2 if you MUST execute user code
const vm = require('vm2');
const sandbox = new vm.VM({ sandbox: {} });
sandbox.run(userCode);
```

### 2. Prototype Pollution

**Vulnerability:** Allows attackers to modify `Object.prototype`, affecting all objects.

**Vulnerable:**

```js
// NEVER merge user input directly onto objects
Object.assign(target, req.body);
_.merge(config, userInput);

// Vulnerable property assignment
const obj = {};
obj[req.body.key] = req.body.value; // key could be '__proto__'
```

**Secure:**

```js
// Validate keys before assignment
const ALLOWED_KEYS = new Set(['name', 'email', 'age']);
for (const [key, value] of Object.entries(userInput)) {
  if (ALLOWED_KEYS.has(key)) obj[key] = value;
}

// Use Object.create(null) for dictionaries (no prototype)
const safeDict = Object.create(null);

// Use schema validation (Zod/Joi) which strips unknown keys
const schema = z.object({ name: z.string(), email: z.string().email() });
const safe = schema.parse(req.body); // strips __proto__ etc.

// Check for polluted keys
function isSafeKey(key) {
  return key !== '__proto__' && key !== 'constructor' && key !== 'prototype';
}
```

**Detection:**

```js
// Test if prototype was polluted
const testObj = {};
console.log(testObj.polluted); // should be undefined
```

### 3. Path Traversal

**Vulnerable:**

```js
// NEVER DO THIS
app.get('/file', (req, res) => {
  const filePath = '/var/www/files/' + req.query.name;
  res.sendFile(filePath); // allows ../../etc/passwd
});
```

**Secure (Node 18+):**

```js
import path from 'path';

app.get('/file', (req, res) => {
  const BASE = path.resolve('/var/www/files');
  const requested = path.resolve(BASE, req.query.name);

  if (!requested.startsWith(BASE + path.sep)) {
    return res.status(403).json({ error: 'Access denied' });
  }

  res.sendFile(requested);
});
```

**Or use express.static with root option (handles this automatically):**

```js
app.use('/files', express.static('/var/www/files'));
```

### 4. Cross-Site Scripting (XSS)

**Vulnerability:** User content rendered as HTML/JS in browsers.

**Vulnerable (Server-side rendering):**

```js
// NEVER
res.send(`<div>${req.query.search}</div>`);

// NEVER (React)
<div dangerouslySetInnerHTML={{ __html: userContent }} />
```

**Secure:**

```js
// Use a template engine with auto-escaping
import nunjucks from 'nunjucks';
nunjucks.configure({ autoescape: true });
res.send(nunjucks.render('template.html', { search: req.query.search }));

// React — use expressions (auto-escaped):
<div>{userContent}</div>  // Safe — React escapes by default

// Client-side — use textContent, not innerHTML:
element.textContent = userInput; // Safe
element.innerHTML = userInput;   // DANGEROUS
```

**Content Security Policy:**

```js
import helmet from 'helmet';
app.use(helmet()); // Sets CSP and other security headers
```

### 5. SSRF (Server-Side Request Forgery)

**Vulnerability:** Server makes HTTP requests to attacker-controlled URLs.

**Vulnerable:**

```js
// NEVER
app.post('/fetch', async (req, res) => {
  const response = await fetch(req.body.url); // SSRF
  res.json(await response.json());
});
```

**Secure:**

```js
const ALLOWED_HOSTS = new Set(['api.example.com', 'cdn.example.com']);

app.post('/fetch', async (req, res) => {
  const url = new URL(req.body.url); // throws on invalid URL
  if (!ALLOWED_HOSTS.has(url.hostname)) {
    return res.status(400).json({ error: 'Host not allowed' });
  }
  const response = await fetch(url.toString());
  res.json(await response.json());
});
```

---

## Cryptography Best Practices

### 1. Secure Random Values

**NEVER use `Math.random()` for security:**

```js
// NEVER for tokens, nonces, session IDs, OTPs:
const token = Math.random().toString(36); // PREDICTABLE

// USE crypto.randomBytes:
import { randomBytes } from 'crypto';
const token = randomBytes(32).toString('hex'); // 256 bits of entropy
const otp = String(Math.floor(parseInt(randomBytes(3).toString('hex'), 16) % 1000000)).padStart(6, '0');
```

### 2. Hashing

**AVOID for password storage or security-sensitive checksums:**

- MD5 — broken, collision attacks known
- SHA-1 — deprecated, collision attacks demonstrated

**USE:**

```js
import { createHash, scrypt, randomBytes } from 'crypto';

// Non-password hashing (integrity checks):
const hash = createHash('sha256').update(data).digest('hex');

// Password hashing — use bcrypt or scrypt:
import bcrypt from 'bcrypt';
const passwordHash = await bcrypt.hash(password, 12);
const isValid = await bcrypt.compare(password, passwordHash);

// Or using built-in scrypt:
const salt = randomBytes(16);
const derivedKey = await new Promise((resolve, reject) =>
  scrypt(password, salt, 64, (err, key) => err ? reject(err) : resolve(key))
);
```

### 3. Encryption

**AES-GCM (authenticated encryption):**

```js
import { createCipheriv, createDecipheriv, randomBytes } from 'crypto';

function encrypt(plaintext, key) {
  const iv = randomBytes(12); // 96-bit IV for GCM
  const cipher = createCipheriv('aes-256-gcm', key, iv);
  const encrypted = Buffer.concat([cipher.update(plaintext), cipher.final()]);
  const tag = cipher.getAuthTag();
  return { iv, encrypted, tag };
}

function decrypt({ iv, encrypted, tag }, key) {
  const decipher = createDecipheriv('aes-256-gcm', key, iv);
  decipher.setAuthTag(tag);
  return Buffer.concat([decipher.update(encrypted), decipher.final()]);
}
```

**AVOID deprecated APIs:**

```js
// DEPRECATED — use createCipheriv instead:
crypto.createCipher('aes256', password); // no IV, weak KDF
```

### 4. TLS Configuration

```js
import https from 'https';
import fs from 'fs';

const server = https.createServer({
  key: fs.readFileSync('server.key'),
  cert: fs.readFileSync('server.crt'),
  minVersion: 'TLSv1.2',      // Require TLS 1.2+
  // rejectUnauthorized: true is the DEFAULT — never set false in production
});

// For outbound HTTPS requests — never disable verification:
const agent = new https.Agent({ rejectUnauthorized: true }); // This is the default
```

### 5. JWT Security

```js
import jwt from 'jsonwebtoken';

// NEVER use 'none' algorithm:
jwt.verify(token, secret, { algorithms: ['HS256'] }); // Explicit algorithm

// ALWAYS set expiry:
jwt.sign({ userId }, secret, { expiresIn: '1h', algorithm: 'HS256' });

// Use asymmetric keys for cross-service tokens:
jwt.sign(payload, privateKey, { algorithm: 'RS256' });
jwt.verify(token, publicKey, { algorithms: ['RS256'] });
```

---

## Dependency Security

### 1. Lock Files and Version Pinning

```json
// package.json — avoid ranges for critical packages
{
  "dependencies": {
    "express": "4.18.2",         // pinned
    "jsonwebtoken": "^9.0.0"    // minor-only updates
  }
}
```

### 2. CI Integration

```yaml
# .github/workflows/security.yml
name: Security Audit
on: [push, pull_request]
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - run: npm audit --audit-level=high
      - run: npx snyk test || true
```

### 3. Supply Chain Risks

- Check `postinstall` scripts in transitive dependencies
- Use `npm pack` to inspect what gets installed
- Use private registry mirrors for critical packages
- Review new dependencies before merging

---

## ReDoS (Regular Expression Denial of Service)

### Vulnerable Patterns

Catastrophic backtracking occurs with nested quantifiers on user-controlled input:

```js
// DANGEROUS — quadratic or exponential backtracking:
/^(a+)+$/.test(userInput)          // nested +
/(a|aa)+$/.test(userInput)         // alternation with overlap
/(\w+\s?)*$/.test(userInput)       // overlapping groups
```

### Detection

Use a tool like `safe-regex` or `redos-detector`:

```bash
npm install --save-dev safe-regex
```

### Fix

- Simplify regex to avoid nested quantifiers
- Use atomic groups or possessive quantifiers (Node 16+)
- Validate input length before applying complex regex
- Set a timeout using `AbortSignal`:

```js
import { setTimeout as setTimeoutPromise } from 'timers/promises';

async function safeMatch(regex, input) {
  if (input.length > 1000) throw new Error('Input too long');
  return regex.test(input);
}
```

---

## Security Checklist

### Input Handling

- [ ] All route handler inputs validated with Zod/Joi/Yup
- [ ] SQL queries use parameterized values (never string concat)
- [ ] File paths from user input validated against allowed base directory
- [ ] URL inputs for server-side requests validated against host allowlist
- [ ] `JSON.parse` results validated before use
- [ ] Object keys from user input checked for `__proto__`, `constructor`

### Cryptography

- [ ] `crypto.randomBytes()` used (never `Math.random()`) for tokens/nonces
- [ ] SHA-256+ used for checksums (never MD5, SHA-1)
- [ ] bcrypt/scrypt/argon2 used for password hashing
- [ ] AES-GCM used for encryption
- [ ] JWTs have explicit algorithm and expiry
- [ ] `rejectUnauthorized` is never `false` in production TLS

### Injection

- [ ] No `exec()`/`execSync()` with user-controlled strings
- [ ] No `eval()` / `new Function(str)` / `setTimeout(str)`
- [ ] HTML output uses template engine with auto-escaping
- [ ] React uses JSX expressions, not `dangerouslySetInnerHTML`
- [ ] No `innerHTML` assignments from user input (client-side)

### Infrastructure

- [ ] `npm audit` runs in CI, failing on high severity
- [ ] Dependencies pinned to specific versions for critical packages
- [ ] HTTP security headers set (Helmet for Express)
- [ ] No hardcoded secrets — use environment variables or secrets manager
- [ ] Error responses return generic messages, not stack traces

### Error Handling

- [ ] All Promise rejections handled (no fire-and-forget without `.catch`)
- [ ] Express async handlers wrapped in try/catch with `next(err)`
- [ ] Error responses in production never include stack traces
- [ ] Errors logged with context (structured logging)

---

## References

- [OWASP Node.js Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Nodejs_Security_Cheat_Sheet.html)
- [Node.js Best Practices — Security](https://github.com/goldbergyoni/nodebestpractices#6-security-best-practices)
- [ESLint Plugin Security](https://github.com/eslint-community/eslint-plugin-security)
- [Snyk Node.js Vulnerability Database](https://security.snyk.io/vuln/npm)
- [npm audit documentation](https://docs.npmjs.com/cli/v10/commands/npm-audit)
- [Node.js crypto module](https://nodejs.org/api/crypto.html)

---

**Document Version:** 1.0
**Last Updated:** May 2026
**Author:** Compiled from OWASP resources, Node.js docs, and community security research
