Review and fix all Python code quality issues in this codebase.

Start by using Glob with '**/*.py' to discover all Python source files.
Batch Read calls: read 4-6 files per iteration. Do NOT read one file per iteration.
Cross-reference between files for consistency issues.
Apply fixes via Edit tool, highest severity first.
Run 'ruff check .' after edits. If ruff is NOT installed, use py_compile only.

ANALYSIS CHECKLIST (check each file for these):

- Method calls self.x() — is the method actually defined? (CRITICAL if not)
- Every name used — is it imported or defined? (CRITICAL if missing import)
- if/else branches — do they do different things or identical code? (HIGH if dead code)
- HTTP calls — inside context managers? (HIGH if httpx.get without Client())
- Public functions — return type annotations? (but NEVER add -> None, it's inferable)

PRIORITY (mandatory order):

- Fix ALL CRITICAL before ANY HIGH. Fix ALL HIGH before ANY MEDIUM.
- Do NOT skip CRITICAL/HIGH to fix easier MEDIUM issues.

ABSOLUTE PROHIBITIONS (violating these is a pipeline failure):

- You are a REVIEWER, not a feature developer. ZERO NEW FUNCTIONS OR METHODS
  ALLOWED — do not create any new def/async def declarations. Also forbidden:
  no new config options, no new parameters, no new exception classes, no new
  env var overrides, no new type aliases, no new named types, no refactoring
  that splits one function into multiple. If you see a gap, note it in the
  skipped table as "feature request" — do NOT implement it. Every line you
  add must fit within an existing function and fix a specific bug.
- Do NOT touch lines annotated with # nosec, # noqa: S602, # noqa: S604 or
  similar security suppressions. Report them in the skipped table as HIGH with
  a warning, but do NOT edit them. The developer already evaluated the risk.
- NEVER replace shell=True with ["bash", "-lc", command_string] — that is
  equally unsafe and provides zero security benefit. If you cannot eliminate
  the shell entirely (split into a proper argv list with no shell), skip it.
- Do NOT replace asyncio.gather(return_exceptions=True) with TaskGroup — they
  have different cancellation semantics. gather collects partial results;
  TaskGroup cancels remaining tasks on first exception.
- Do NOT add, remove, or reword docstrings — that is the doc-comments agent's
  job. Zero docstring edits allowed from this agent.
- Do NOT add type annotations to local variables (e.g., results: list[str] = [])
  — if the type is inferable, adding it is cosmetic.
- Do NOT restructure equivalent syntax — async with A, B: is identical to
  nested async with A:\n  async with B:. Splitting them is cosmetic churn.
- Do NOT replace safe error returns (return None, return {error_dict}) with
  raise/re-raise. Callers depend on the return value contract.
- Do NOT add post-use variable clearing (var = None after use) as "security
  hardening" — that is new behavior, not a bug fix.

CONSTRAINTS:

- No cosmetic changes (docstrings, import ordering, naming style)
- No new dependencies
- Skip fixes needing 50+ lines or new files
- Preserve backwards compatibility — no API surface changes
- NEVER change functions whose behavior is asserted by tests (pytest.raises)
- NEVER remove intentional raise statements — they are precondition guards
- Every fix must be PROPORTIONAL — no micro-optimizations for small loops
- NEVER change identifier/correlation ID assignments (job_id=x.project may be intentional)
- When fixing UnboundLocalError, use None as fallback, NOT another variable's value
- Flag inconsistent imports (e.g. print() when codebase uses logging)
- NEVER add -> None return annotations — they are always inferable

ITERATION BUDGET — scales with codebase size (count after Glob):

- Small (≤20 files): 12 iterations max
- Medium (21-50 files): 20 iterations max
- Large (50+ files): 25 iterations max

Phase allocation:

- Phase 1 (1 iter): Glob + Read pyproject.toml in parallel, COUNT source files
  (reference is already in your system prompt — do NOT Read it)
- Phase 2 (varies): Read files with 6-10 parallel Reads per iteration
  - Small: 2-3 iters to read ALL
  - Medium: 4-5 iters to read ALL
  - Large: prioritize entry points + core modules
- Phase 3 (2-4 iter): ALL Edit calls batched (10 fixes = 10 Edit calls in ONE response)
- Phase 4 (1 iter): Verify + report in SAME response

Do NOT hardcode directory names like app/, src/, lib/ — use Glob output.
COVERAGE IS MANDATORY for small/medium. For large codebases, document sampling.

HARD REQUIREMENTS:

- Do NOT read one file per iteration — batch 6-10 Read calls per iteration
- Do NOT edit-wait-edit-wait — batch ALL edits into ONE iteration
- Do NOT re-read files after editing — trust Edit output
- STOP after verification — emit report in SAME response, NO more iterations
- If ruff not installed, proceed with py_compile only
- Every file touched must appear in the output report
