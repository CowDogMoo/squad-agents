---
name: rust-pipeline
description: "Runs the full Rust quality pipeline over a crate or workspace by chaining the rust-review, rust-tests, and rust-doc-comments subagents in sequence with clippy/test/build gates between stages. Use when asked to run the Rust quality pipeline, or to review, test, and document a Rust crate end to end in one pass. Stops at the first failing gate."
argument-hint: "[path] (Rust crate or workspace dir; defaults to the repo root)"
---

# Rust quality pipeline

Run a sequential, gated quality pass over a Rust crate or workspace by
chaining specialized subagents. This is a deterministic prompt-chaining
workflow: each stage runs to completion, returns its summary, and the next
stage runs only if the preceding gate passed.

**Target:** `$ARGUMENTS` — the Rust crate or workspace directory to operate
on. If empty, use the repository root (the current working directory).

## Before you start

- These stages **edit the working tree in place**. Confirm the target is a
  git repo on a clean (non-main) branch before running; if `git status` shows
  unrelated uncommitted changes, surface that and ask before proceeding.
- Run the stages **one at a time, in order**, using the Agent tool. Wait for
  each subagent to finish and read its returned summary before starting the
  next. Pass the target path to every subagent.

## Stages and gates (run in this exact order)

1. **rust-review** — review and fix code-quality, correctness, safety, and
   reliability issues.
   - **GATE — `cargo clippy -- -D warnings`** (run from the target dir). If
     it FAILS: STOP the pipeline. Do not run stage 2. Report the clippy
     output.
2. **rust-tests** — raise per-module coverage and add missing tests.
   - **GATE — `cargo test`** (run from the target dir). If it FAILS: STOP the
     pipeline. Do not run stage 3. Report which test(s) failed with the
     output.
3. **rust-doc-comments** — add and improve doc comments on public
   declarations.
   - **GATE — `cargo build`** (run from the target dir). If it FAILS: report
     the build error; the pipeline is incomplete.

## Reporting

After the pipeline stops (either all three stages completed and all gates
passed, or an earlier gate failed), emit one consolidated report:

- One line per stage: what it changed (taken from each subagent's summary),
  or `skipped/clean`.
- The status of each gate that ran (`cargo clippy -- -D warnings`,
  `cargo test`, `cargo build`): PASS / FAIL, with failing output if any.
- If a gate failed, name the stage it gated and state that later stages were
  not run.

Do not re-run stages or gates that already passed. Do not paste full file
contents back into the report — the edits are already on disk.
