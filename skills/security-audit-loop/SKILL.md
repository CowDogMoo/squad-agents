---
name: security-audit-loop
description: "Use when running one of the six security stage agents (go, nodejs, or python security-injection and security-resources) or a scoped fix-in-place security audit: the shared loop of discovery, read-before-analyze, edit vs readonly mode, verify and revert, budget and wind-down, severity scale, and finding and report formats, with language, file globs, build/test commands and the category list supplied by the caller. Not a vulnerability knowledge base (those are the <lang>-security-guide skills) and not a general code review."
---
# Security Audit Loop

You are auditing a codebase for a fixed set of vulnerability categories.
This skill is the loop: the two modes, discovery, analysis, fixing,
verification, budget, severity, and the report shapes. The caller (a
language security stage agent) supplies everything that differs per
language and per category set. Where the caller's prompt and this skill
disagree, the caller wins. Where either disagrees with the language
security guide, the caller and this skill win.

## Inputs the caller supplies

- **Language** and its **knowledge skill** (`golang-security-guide`,
  `nodejs-security-guide`, `python-security-guide`). The guide holds the
  vulnerable and secure patterns; this skill does not restate them.
- **Source glob and exclusions**, e.g. `**/*.go` minus `_test.go` and
  `vendor/`.
- **Grep file filter**, e.g. `glob: "*.go"`.
- **Dependency manifest** to read in discovery (`go.mod`,
  `package.json`, `requirements.txt` or `pyproject.toml`). "No new
  dependencies" means nothing outside this manifest.
- **Optional scanner** whose output seeds the finding list (for example
  Bandit or pip-audit).
- **Verify command** (build, compile, lint, or type check) and **test
  command**.
- **Revert mechanism**: `git checkout -- <file>` unless the caller says
  otherwise.
- **Categories**: the caller's category list, the categories to ignore
  (another stage owns them), what to fix, what not to fix, and how to
  fix.
- **Language-specific hard rules**, e.g. never add `panic`, never
  swallow errors, never silence exceptions around security checks.

## Modes

The default is **edit mode**: apply fixes in place, verify, report what
changed.

If the caller's request contains "readonly", "report only", "analysis
only", or "do not modify", run in **readonly mode**: produce a
prioritized findings report and change nothing. Do not call Edit or
MultiEdit, and do not run commands that write files. If you modify any
file in readonly mode, the run is invalid.

## Rules for both modes

1. **Discover code yourself.** Find files with Glob and Grep, and Read
   each file before analyzing it. Never guess at file contents.
2. **Stay in scope.** Report and fix only the caller's categories. Skip
   everything in the caller's ignore list, and skip code quality, doc
   comments, import ordering, naming, whitespace, and performance issues
   with no security impact.
3. **No false positives.** Every finding cites real code with an exact
   file path and line number.
4. **Trace the call chain.** Before rating or fixing a finding, follow
   the input from its source to the sink and on to the next consumer.
   Confirm it is reachable from external input, and confirm a fix
   survives the next function in the chain (a value that is sanitized
   and then re-parsed or re-joined may be exploitable again).
5. **Proportionality.** A theoretical issue in internal-only code with
   no path from external input is INFO, not a fix and not an escalation.
6. **Justify severity.** Give each finding a severity from the scale
   below and a CWE where one applies.

## Edit-mode rules

1. **Changes must verify.** Run the caller's verify command after each
   batch of edits. If it fails, fix the error you introduced before
   continuing, or revert the file and skip the finding.
2. **Tests must pass.** Run the caller's test command after your edits.
   If tests fail because of a fix, revert that file with the revert
   mechanism and move the finding to the skipped table.
3. **Test-asserted behavior is unfixable.** Before any fix, Grep the
   tests for the function or type you are changing. If a test asserts
   the current behavior, do not fix it; move it to the skipped table.
   Never edit test files.
4. **No new dependencies.** Use only imports and packages already in the
   manifest. If the right fix needs a new dependency, skip it and say so.
5. **One fix per edit**, so each diff is focused and reviewable.
6. **Skip risky fixes.** If a fix needs more than 50 lines of new code
   or a new file, list it in the skipped table and move on.
7. **Follow existing conventions** for error messages, naming, and code
   organization. When the same fix pattern lands in several places, use
   the same variable names everywhere. Variables in separate functions
   have separate scopes, so never add `2` or `3` suffixes to avoid
   imaginary conflicts.
8. **Preserve backwards compatibility.** Do not rename exported or
   public functions or change their signatures.
9. **Do no harm.** Every fix must be strictly better than the original
   and preserve its behavior for legitimate input.
10. **Fix every occurrence.** When you find a vulnerable pattern, Grep
    the whole repo for it (with the caller's file filter) and fix all
    instances, not only the first.
11. **Report every change.** Every file you touch appears in the report.

## Workflow

### Phase 1: Discover

1. Glob the caller's source pattern and apply its exclusions.
2. Confirm the knowledge skill and this skill are in context. If the
   host injected them (look for "Reference:" sections), do not load or
   Read them again. Otherwise load each with `Skill()` once.
3. Read the dependency manifest.
4. If the caller names a scanner, run it and treat its output as a
   prioritized lead list. Confirm each lead by reading the code; never
   fix from scanner output alone.

### Phase 2: Analyze

1. Read each source file once, in parallel batches. Files over 500
   lines are truncated to head and tail by Read, so read them in
   sections with `offset` and `limit` until the whole file is covered.
2. Check each file against the caller's categories and per-category
   questions only.
3. Cross-reference files for the same pattern handled inconsistently.
4. Catalog every finding with severity, CWE, file:line, the proposed
   fix, and the call-chain check from rule 4.

### Phase 3: Fix and verify (edit mode) or prioritize (readonly mode)

**Readonly mode:** sort findings by severity (CRITICAL first), then by
category. Make no edits.

**Edit mode:**

1. Grep for all occurrences of each pattern before fixing.
2. Apply fixes highest severity first, grouping all edits for one file
   into one iteration.
3. After each batch, Read only the edited lines to confirm the result.
4. After all fixes, run the verify and test commands once. Revert and
   skip any file whose fix breaks them.

### Phase 4: Report

Emit the report in the caller's mode format immediately. Build the
skipped table from Phase 2 notes; do not re-explore.

## Budget and wind-down

- Batch Read calls and track your iteration count.
- Read each file once: analyze everything first, then fix.
- Target 12 iterations or fewer for 20 or fewer files. Finish Phases 1
  and 2 within 4 iterations.
- Always pass the caller's file filter to Grep. If Grep fails with
  "token too long", skip it and use your Read-phase notes.
- Use Read and Glob, not Bash `cat`, `find`, or `head`, to explore.
- Produce the report before spending 60% of the cost budget. If a budget
  warning appears, stop and emit the report at once; a partial report
  beats none.
- If you find no actionable issue in your categories, skip Phase 3 and
  report. Zero findings is a correct outcome on clean code.
- Once verification passes, emit the report in the same response. No
  re-reading and no extra tool calls.

## Severity levels

- **CRITICAL**: affects correctness or security, or causes crashes or
  data loss
- **HIGH**: significant reliability or maintainability issue
- **MEDIUM**: best-practice violation with real impact
- **LOW**: minor improvement
- **INFO**: suggestion, or a theoretical issue with no external input
  path (rule 5)

The caller may pin specific findings to a level (for example, SSTI is
always CRITICAL).

## What not to fix (all callers)

- Missing or incomplete doc comments
- Import ordering, naming style, whitespace
- General code quality with no security impact
- Test files
- Changes requiring new dependencies
- Performance changes with no security relevance
- Anything in the caller's ignore list

## Output format

Use the format for the active mode exactly. Add "— CWE-XXX" to each
finding title where a CWE applies. The caller supplies the source-file
extension for the Files Touched example and the command lines for
Validation.

### Edit-mode report

```markdown
### Changes Summary

[Brief overview, 2-3 sentences]

### Issues Found and Fixed

#### [Vulnerability Title] — CWE-XXX

**Severity:** CRITICAL/HIGH/MEDIUM/LOW
**Category:** [category]
**File:** [file path]
**Line:** [line number]

**What was changed:** [1-2 sentences]
**Why:** [1-2 sentences]

---

### Issues Found but Skipped

| Issue | Severity | File | Reason Skipped |
|-------|----------|------|----------------|
| [title] | [sev] | [file] | [reason] |

### Files Touched

- `path/to/file.<ext>` — [change description]

### Validation

- `<verify command>`: PASS/FAIL
- `<test command>`: PASS/FAIL/SKIPPED (not available)
```

### Readonly-mode report

```markdown
### Analysis Summary

**Files analyzed:** [N]
**Total findings:** [N]
**By severity:** CRITICAL: [N], HIGH: [N], MEDIUM: [N], LOW: [N], INFO: [N]

### Findings

#### [Issue Title] — CWE-XXX

**Severity:** CRITICAL/HIGH/MEDIUM/LOW/INFO
**Category:** [category from the caller's list]
**File:** [file path]
**Line:** [line number]

**What is wrong:** [1-2 sentences]
**Suggested fix:** [1-2 sentences or code snippet]

---

### Priority Order

Findings ranked by impact (fix in this order):

1. **[Issue title]** — [severity], [file]
2. ...

### Recommendations

[2-3 sentences on the most impactful improvements to make first]
```

## Example

Caller: `go-security-injection`, readonly request. Inputs: `**/*.go`
minus `_test.go` and `vendor/`; Grep filter `*.go`; manifest `go.mod`;
verify `go build ./...`; test `go test ./...`.

Phase 1 finds 6 files. Phase 2 reads them in two batches and catalogs
one finding: `handler.go:42` passes a query parameter into
`exec.Command("sh", "-c", ...)`. The call chain shows the parameter
comes straight from the HTTP request, so it is CRITICAL, CWE-78. A
`math/rand` token in `session.go` is out of scope for this stage and is
not reported. Phase 3 sorts the single finding; no Edit is called.
Phase 4 emits the readonly-mode report with one finding and a
suggested fix (`exec.Command` with separate arguments and no shell).
