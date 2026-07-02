Get this Python codebase to 75% test coverage.

Discover all source files with `Glob **/*.py`, measure baseline with
`pytest --cov=<pkg> --cov-branch --cov-report=term-missing -q || true`,
then write tests for each module below target.

IMPORTANT CONSTRAINTS:

- Target: 75% total coverage unless the caller specifies otherwise
- Only create/modify `test_*.py` files — never edit source code
- Place tests in `tests/` mirroring source structure. Check for existing files first
- Use `@pytest.mark.parametrize` for 2+ test cases
- Write conftest.py FIRST with module-level sys.modules stubs
- Use Write for genuinely new files only; Edit existing test files. MAXIMUM 2 pytest runs
- Interleave reads and writes: Read 2-3 -> Write tests -> repeat
- MANDATORY `autospec=True` on every patch/mock call
- Budget: <=15 files = 15 iter, 16-30 = 25, 30+ = 35
