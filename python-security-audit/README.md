# Python Security Audit Agent

A parallel two-stage security audit agent for Python codebases.
Both stages run concurrently, each focusing on a non-overlapping set of
vulnerability classes.

## Pattern Structure

- **`agent.yaml`** — Orchestration with two parallel stages + gates
- **`injection-system.md`** / **`injection-agent.md`** / **`injection-task.md`** — Stage 1
- **`resources-system.md`** / **`resources-agent.md`** / **`resources-task.md`** — Stage 2
- **`references/python-security-guide.md`** — Comprehensive Python security guide

## Stages

### Stage 1: Injection

Focuses exclusively on:

- **Command Injection** — `subprocess` with `shell=True`, `os.system()`, `os.popen()` with user input
- **SQL Injection** — f-strings / `%` formatting / concatenation in database queries
- **XSS** — `Markup()` / `mark_safe()` on user data, `autoescape=False`
- **SSTI** — `render_template_string()` / `env.from_string()` with user-controlled template content; leads to RCE (CWE-94)
- **Insecure Deserialization** — `pickle.loads()`, `yaml.load()` without SafeLoader, `eval()` / `exec()`, `marshal.loads()`, `jsonpickle.decode()`, `shelve` with user keys, `torch.load()` without `weights_only=True`, `numpy.load(allow_pickle=True)` on untrusted data
- **XML / XXE** — `xml.etree`, `xml.sax`, `xml.dom.minidom`, `lxml.etree` on user-supplied XML; fix with `defusedxml`
- **Input Validation** — Missing validation at HTTP route handlers, CLI args, WebSocket messages, file-format parsers

### Stage 2: Resources

Focuses exclusively on:

- **Path Traversal** — User-controlled file paths without `Path.resolve()` + boundary validation
- **SSRF** — User-controlled URLs to `requests` / `urllib` / `httpx` / `aiohttp` without allowlist
- **Weak Cryptography** — `random` for security values, MD5/SHA-1 for passwords, `verify=False`, `CERT_NONE`
- **Hardcoded Secrets** — API keys, passwords, tokens, private keys in source code
- **Web Framework Misconfig** — Django `DEBUG=True` / hardcoded `SECRET_KEY`; Flask `debug=True` / hardcoded `secret_key`; FastAPI open CORS with credentials
- **Dependency Vulnerabilities** — Packages with known CVEs in requirements.txt, unpinned versions
- **Error Information Leaks** — Stack traces, internal errors, file paths in HTTP responses
- **Insecure Temp Files** — `tempfile.mktemp()` TOCTOU race (CWE-377); fix with `mkstemp()` or `NamedTemporaryFile()`
- **ReDoS** — Regex patterns with catastrophic backtracking on user-controlled input (CWE-1333)

## Gates

After each stage, the following checks run:

1. Syntax check: `python -m compileall -q .`
2. Test suite: `pytest -x --tb=no -q`

If a gate fails, the pipeline stops.

## Usage

```bash
squad run python-security-audit
```

## What Gets Fixed

Each stage applies fixes within its category scope only:

- Replaces `subprocess(cmd, shell=True)` with `subprocess.run([binary, arg1, arg2])`
- Parameterizes SQL queries replacing string interpolation
- Removes `Markup()` / `mark_safe()` on user-controlled data
- Replaces `pickle.loads()` with `json.loads()` where appropriate
- Replaces `yaml.load()` with `yaml.safe_load()`
- Replaces `eval()` with `ast.literal_eval()` for simple literals
- Validates file paths with `Path.resolve()` and base-dir boundary checks
- Replaces `random.*` with `secrets.token_hex()` / `secrets.token_urlsafe()`
- Replaces hardcoded secrets with `os.environ['KEY']`
- Removes `verify=False` from requests
- Moves `DEBUG` / `SECRET_KEY` out of source and into environment variables
- Replaces internal error details in HTTP responses with safe generic messages

## What Does NOT Get Fixed

- Code quality issues with no security impact
- Changes requiring new dependencies
- Test-asserted behavior
- Issues in the other stage's scope
- Fixes requiring 50+ lines of new code

## Related Agents

- **python-review** — General code quality review
- **python-tests** — Test coverage improvement
- **python-doc-comments** — Docstring generation

## References

- [Bandit — Python Static Security Analysis](https://bandit.readthedocs.io/)
- [pip-audit — Dependency Vulnerability Scanning](https://github.com/pypa/pip-audit)
- [OWASP Python Security Project](https://owasp.org/www-project-python-security/)
- [Python Cryptography Library](https://cryptography.io/)
- [OWASP Top 10](https://owasp.org/Top10/)
