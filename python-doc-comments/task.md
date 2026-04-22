Add or improve docstrings on all public Python declarations in this codebase.

Start by using Glob with '**/*.py' to discover all Python source files.
Batch Read calls: read 4-6 files per iteration.
Catalog every public declaration missing or having a deficient docstring.

IMPORTANT CONSTRAINTS:

- ONLY modify docstrings -- never change code logic, signatures, or imports
- Triple double quotes (`"""`), imperative mood ("Return X" not "Returns X")
- No redundant docstrings -- skip trivial functions (close, get_value, wrappers)
- Do NOT rewrite adequate existing docstrings -- lateral rewrites are FORBIDDEN
- Public declarations only -- skip ALL private names (`_foo`)
- NEVER add `-> None` -- it's always inferable
- Proportional: one-line getter = one-line docstring, complex = multi-paragraph
- Match existing style (NumPy/Sphinx if present, else Google style)
- Read each file ONCE, catalog all findings, then fix
- Batch ALL edits into ONE iteration
- After verification passes, emit report IMMEDIATELY -- no post-fix exploration
- Every file touched must appear in the output report
