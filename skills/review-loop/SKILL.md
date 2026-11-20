---
name: review-loop
description: "Shared fix-in-place review loop for the go-review, rust-review, python-review and nodejs-review agents: discovery, edit vs readonly mode, verify-after-edit, budget, severity scale and report formats, with language, globs, verify commands and categories supplied by the caller. Use when running one of those agents or a repo-scale review that fixes code in place. Not review criteria (those are the per-language review-criteria skills) and not security audits."
---
# Review Loop

You are running a code review over a codebase. This skill is the loop:
discovery, the two modes, batching, verification, budget, severity, and
the report shapes. The caller (a language review agent) supplies what
differs per language. Where the caller's prompt and this skill disagree,
the caller wins.

## Inputs the caller supplies

- **Language** and its **knowledge skill** (`go-review-criteria`,
  `rust-review-criteria`, `python-review-criteria`,
  `nodejs-review-criteria`). The knowledge skill holds the detailed
  criteria; this skill does not restate them.
- **Source glob and exclusions**, e.g. `**/*.go` minus `_test.go` and
  `vendor/`.
- **Lint command** and the name of the injected warnings block
  (`LINT_WARNINGS` by default; Rust uses `CLIPPY_WARNINGS`).
- **Verify commands**: build or compile check, lint, and test.
- **Revert mechanism**: `git checkout -- <file>` by default. A caller may
  forbid git and require Edit-to-undo instead.
- **Review categories**, what to fix, how to fix, and language-specific
  what-not-to-fix items.
- **Test-assertion markers** that make behavior unfixable (`wantPanic`,
  `#[should_panic]`, `pytest.raises`, asserted error messages).
- **Logger-consistency rule**: which logger counts as the house logger
  and which calls are the inconsistent ones.
- **Mode keywords**: "readonly", "report only", "analysis only", "do not
  modify" select readonly mode; otherwise edit mode applies.

Optional overrides a caller may declare (defaults in parentheses):
read batch size (3-5 files), allowed new dependencies (none), and
readonly report shape (the readonly-mode format below).

## Modes

**Edit mode** is the default: fix issues in place, verify, and report
what changed. **Readonly mode** is opt-in through the mode keywords:
make no Edit, MultiEdit, or Write calls at all. A readonly run that
modifies a file is invalid.

Both modes look for the same issues. Edit mode fixes them; readonly mode
reports them with a suggested fix.

## Scope and budget

The iteration cap and the edit deadline are not set here or in the
caller's prose: they live in the agent's `agent.yaml` (`max_iterations`,
`edit_deadline`). Keep a rough count of iterations so you can wind down
before the cap.

Review every file in scope before you conclude nothing is actionable. A
clean lint run or passing tests does not shrink the scope. Zero edits is
a valid outcome for clean code; never make a change just to show
progress. If the cap will not cover every file, start with entry points,
core logic and the public API, and list what you did not read.

**Read-then-edit cadence (edit mode).** Read a batch of files in
parallel, fix what you found in them, then read the next batch. Never
hold more than one unprocessed batch. Make the final verify and the
report in the same response.

## Phase 1: Discover

1. **Explicit file list first.** If the prompt names files or injects a
   `Pre-discovered source files` block, those files are the complete,
   frozen set. Skip Glob, do not Glob to double-check, and do not
   re-filter.
2. **Injected lint output.** If the prompt injects the caller's warnings
   block, use it verbatim as the lint result and skip the lint run.
3. Otherwise Glob the caller's pattern once from the repo root and apply
   the exclusions. In edit mode, run the lint command so lint findings
   come before subjective ones.
4. Reference documents already injected into the prompt are in context.
   Do not Read them as files.

## Phase 2: Analyze

- Read before analyzing. Never guess at file contents.
- Read files in parallel batches. Prioritize files with lint warnings
  and complex signatures or control flow.
- Read each file once and take notes. Use those notes for the skipped
  table later.
- Cross-reference types, functions, and error handling across package or
  module boundaries, not only within single files.
- Catalog each finding with severity, category, file, line, description,
  and proposed fix.

## Phase 3: Fix and verify (edit mode)

- Fix lint findings first, then by severity, highest first.
- **One fix per Edit call.** Keep diffs focused; do not bundle unrelated
  changes.
- **Batch edits per file.** All Edit calls for one file go in the same
  response.
- **Edit safety.** Include 2-3 lines of surrounding context in
  `old_string` so the match is unique.
- **Verify the API first.** Grep for a type, variant, or function before
  using it in an Edit, and match existing patterns.
- **Verify with the build, not a re-read.** The Edit result confirms the
  change; the caller's build, lint and test commands confirm it works.
  Re-read a file only when an Edit or a verify error points into it.
- **Verify after every batch** with the caller's build or lint command,
  and fix errors before continuing. After all fixes, run build and tests
  once. Prefer one Bash call that prints each exit code.
- **Revert on failure.** If verification fails and the fix cannot be
  corrected, revert the file with the caller's revert mechanism and move
  the finding to the skipped table. Never leave a failing build or
  failing tests behind.

## Edit-mode rules

1. **No cosmetic-only changes.** Skip doc comments, import ordering,
   naming style, and whitespace. Every edit fixes a functional or
   best-practice violation.
2. **No new dependencies** unless the caller allows specific ones. Note
   the finding and skip it.
3. **Skip risky fixes.** If a fix needs more than 50 lines or a new file,
   note it and move on.
4. **Follow existing conventions.** Match the surrounding style for error
   messages, naming, logging, and organization. Use packages already
   imported. When the codebase has a house logger, flag files that log
   through the caller's inconsistent calls as a MEDIUM consistency
   violation.
5. **Preserve backwards compatibility.** Do not rename exported or public
   items, change signatures, or alter the public API. If something
   published is wrong, report it instead.
6. **Test-asserted behavior is unfixable.** Before any fix, Grep for
   tests that reference the code. If a test asserts the current behavior,
   do not change it: move the finding to the skipped table with reason
   "test asserts current behavior". Test files are not edited.
7. **Do no harm.** Every fix must be strictly better than the original.
   If a fix changes control flow, justify why the new behavior is
   correct. Skip lateral moves.
8. **Think before fixing a silenced error.** Ask what the caller would do
   with the error. If nothing useful, leave it alone. The caller lists
   its language's accepted patterns.
9. **Understand the caller's contract.** Callbacks, middleware, iterator
   adaptors, and framework hooks give return values special meaning.
   Read the calling code before changing error returns or control flow
   inside them.
10. **Proportionality.** Ask whether the fix prevents a real bug or adds
    complexity for a theoretical gain. Skip micro-optimizations on small
    loops.
11. **Report every change.** Every file touched appears in the report.

## Readonly-mode rules

1. Make no Edit, MultiEdit, or Write calls.
2. Inspect actual code with Read and Grep. Do not guess.
3. No cosmetic findings: doc comments, import ordering, naming style,
   whitespace, one-off magic numbers.
4. Every finding names an exact file path and line number.
5. Cross-reference files for consistent types, functions, and error
   handling.
6. Justify severity with the scale below.
7. Suggest fixes that obey the caller's hard rules. Never suggest a fix
   the caller bans in edit mode.
8. Apply the same proportionality and contract checks as edit mode.
9. Flag logger inconsistency at MEDIUM, as in edit mode.

## Efficiency and wind-down

- One Glob or Grep on the repo root, not one per directory.
- Use Read to inspect files, never `cat`, `head`, or `tail` through Bash.
  Always pass Bash a non-empty command.
- No post-fix exploration. After verification passes, write the report
  in the same response. Do not re-read files or run extra searches to
  fill in the skipped table.
- **Wind-down.** When approaching the iteration cap, stop new fixes, run
  final verification, and produce the report, listing unread files and
  unapplied fixes as skipped with reason "budget". A partial report
  beats no report.
- In readonly mode, emit the report and stop. No tool calls after it.

## Severity levels

- **CRITICAL**: affects correctness or security, or causes crashes or
  data loss.
- **HIGH**: significant reliability or maintainability issue.
- **MEDIUM**: best-practice violation with real impact.
- **LOW**: minor improvement.
- **INFO**: optimization suggestion (readonly reports only).

The caller may pin specific findings to a level; those calibrations win.

## What not to fix or report (shared defaults)

Callers add language-specific items to this list.

- Doc comments, import ordering, naming style (unless misleading).
- Whitespace, formatting, and magic numbers or strings that occur once
  (unless they cause a real bug).
- Test files, opinion-based organization, and changes that need a new
  dependency.
- Trivial getters and setters, delegation-only wrappers.
- Speculative abstractions with a single implementation.
- Any behavior asserted by tests you cannot modify.

## Report formats

Sorting: findings by severity (CRITICAL first), then by category.
Category names come from the caller's review categories. The section
headings below are required, in order, at the heading level the caller's
OUTPUT COMPLIANCE list shows (level 2 when it shows none).

### Edit-mode report

```markdown
## Changes Summary

[What was changed and why, 2-3 sentences]

## Issues Found and Fixed

### [Issue Title]

**Severity:** CRITICAL/HIGH/MEDIUM/LOW
**Category:** [category from review categories]
**File:** [file path]
**Line:** [line number]

**What was changed:** [1-2 sentences]
**Why:** [1-2 sentences referencing best practices or standards]

---

## Issues Found but Skipped

| Issue | Severity | File | Reason Skipped |
|-------|----------|------|----------------|
| [title] | [sev] | [file] | [too risky, needs new dep, test-asserted, budget, etc.] |

## Files Touched

- `path/to/file` — [specific change]

## Validation

- `[build or lint command]`: PASS/FAIL
- `[test command]`: PASS/FAIL/SKIPPED (not available)
```

### Readonly-mode report

```markdown
## Analysis Summary

**Files analyzed:** [N]
**Total findings:** [N]
**By severity:** CRITICAL: [N], HIGH: [N], MEDIUM: [N], LOW: [N], INFO: [N]

## Findings

### [Issue Title]

**Severity:** CRITICAL/HIGH/MEDIUM/LOW/INFO
**Category:** [category from review categories]
**File:** [file path]
**Line:** [line number]

**What is wrong:** [1-2 sentences]
**Suggested fix:** [1-2 sentences or code snippet]

---

## Priority Order

1. **[Issue title]** — [severity], [file]

## Recommendations

[2-3 sentences on the most impactful improvements to make first]
```

A caller may override the readonly shape. python-review does: it emits
the edit-mode structure with every finding under `Issues Found but
Skipped` (reason "readonly mode"), `Issues Found and Fixed` empty, and
`Files Touched: none`.

## Boundary: what stays in the caller

- Review categories, what to fix, how to fix, and language-specific
  what-not-to-fix items.
- Accepted silenced-error patterns and their single canonical statement
  (for example Go's `_ =` rule, Rust's blessed `let _ =` patterns).
- Bans on specific constructs (adding `panic`, `unwrap()`, bare
  `except`, empty `.catch`), and contract examples (`filepath.WalkFunc`,
  Express `next()`).
- Exact commands, revert mechanism, and the overrides listed above.
