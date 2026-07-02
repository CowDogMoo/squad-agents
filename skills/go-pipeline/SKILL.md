---
name: go-pipeline
description: "Runs the full Go quality pipeline over a module by chaining the go-cobra, go-review, go-tests, and go-doc-comments subagents in sequence with build/test gates between stages. Use when asked to run the Go quality pipeline, or to review, test, and document a Go module end to end in one pass. Stops at the first failing gate."
argument-hint: "[path] (Go module dir or package; defaults to the repo root)"
---

# Go quality pipeline

Run a sequential, gated quality pass over a Go module by chaining specialized
subagents. This is a deterministic prompt-chaining workflow: each stage runs to
completion, returns its summary, and the next stage runs only if the preceding
gate passed.

**Target:** `$ARGUMENTS` — the Go module directory or package to operate on. If
empty, use the repository root (the current working directory).

## Before you start

- These stages **edit the working tree in place**. Confirm the target is a git
  repo on a clean (non-main) branch before running; if `git status` shows
  unrelated uncommitted changes, surface that and ask before proceeding.
- Run the stages **one at a time, in order**, using the Agent tool. Wait for
  each subagent to finish and read its returned summary before starting the
  next. Pass the target path to every subagent.

## Stages and gates (run in this exact order)

1. **go-cobra** — fix Cobra/Viper anti-patterns. If the module has no Cobra CLI,
   the agent will report nothing changed; that is fine — continue.
2. **go-review** — review and fix code-quality, correctness, and reliability
   issues.
3. **go-tests** — raise per-package coverage and add missing tests.
   - **GATE — `go test ./...`** (run from the target dir). If it FAILS: STOP the
     pipeline. Do not run stage 4. Report which test(s) failed with the output.
4. **go-doc-comments** — add and improve doc comments on exported declarations.
   - **GATE — `go build ./...`** (run from the target dir). If it FAILS: report
     the build error; the pipeline is incomplete.

## Reporting

After the pipeline stops (either all four stages completed and both gates
passed, or an earlier gate failed), emit one consolidated report:

- One line per stage: what it changed (taken from each subagent's summary), or
  `skipped/clean`.
- The status of each gate that ran (`go test ./...`, `go build ./...`): PASS /
  FAIL, with failing output if any.
- If a gate failed, name the stage it gated and state that later stages were not
  run.

Do not re-run stages or gates that already passed. Do not paste full file
contents back into the report — the edits are already on disk.
