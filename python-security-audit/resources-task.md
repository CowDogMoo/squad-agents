Audit and fix all RESOURCE and CONFIGURATION vulnerabilities in this Python codebase.
Your scope: path traversal, SSRF, weak crypto, hardcoded secrets, web
framework misconfig, dependency CVEs, error info leaks ONLY.
Another agent handles injection, SQL injection, XSS, and deserialization —
do NOT overlap.

Start by using Glob with '**/*.py' to discover all Python source files.
Filter out __pycache__/, .venv/, venv/, test_*.py, *_test.py.
Read requirements.txt or pyproject.toml for dependency and package context.
For files over 500 lines, use Read with offset/limit to cover the ENTIRE file.
Grep for ALL occurrences of a pattern before fixing — fix ALL instances.
Apply fixes via Edit tool, highest severity first.
Run 'python -m compileall -q .' after each batch of edits.

IMPORTANT CONSTRAINTS:

- RESOURCE/CONFIG FOCUS ONLY — path traversal, SSRF, crypto, secrets, framework config, deps, error leaks
- Grep for ALL occurrences of a vulnerable pattern before fixing — fix ALL instances
- No new dependencies
- Skip fixes needing 50+ lines or new files
- Preserve backwards compatibility
- NEVER change functions whose behavior is asserted by tests
- Every fix must be PROPORTIONAL — internal-only code with no external input path is INFO only
- Phase 1+2 MUST complete in ≤4 iterations
- Produce the report before spending 60% of your cost budget
- STOP after compileall + pytest BOTH pass — emit report IMMEDIATELY
