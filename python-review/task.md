Review and fix all Python code quality issues in this codebase.

Discover with Glob `**/*.py`, batch Read 4-6 files per iteration,
cross-reference for consistency, apply fixes highest severity first,
run `ruff check .` after edits (py_compile if ruff unavailable).

IMPORTANT CONSTRAINTS:

- No cosmetic changes (docstrings, import ordering, naming style)
- No new dependencies
- Skip fixes needing 50+ lines or new files
- Preserve backwards compatibility — no API surface changes
- NEVER change test-asserted behavior (pytest.raises)
- NEVER remove intentional raise statements
- ZERO new functions/methods — fix within existing functions only
- Do NOT auto-fix security-annotated code (# nosec, # noqa: S602)
- Every fix must be PROPORTIONAL
- Flag inconsistent logging (print() vs logging module)
- Batch ALL edits per file in ONE iteration
- After verification passes, emit report IMMEDIATELY
- Every file touched must appear in the output report
