# cobra-mini — go-cobra regression fixture

A minimal Cobra CLI used to regression-test the **go-cobra** agent. It pins
down two false positives the agent produced against real codebases (a no-op
`RunE` added to a parent command; a redundant `MarkFlagRequired` on a flag
already validated in `RunE`) while confirming it still applies a genuine fix.

## What's in here

| File | Role | Correct agent behavior |
| ---- | ---- | ---------------------- |
| `cmd/version.go` | **Real violation** — uses `Run:` instead of `RunE` | **Fix it** → convert to `RunE` returning `nil` |
| `cmd/init.go` | **Trap 1** — `initCmd` is a parent/container command with neither `Run` nor `RunE` (only its `agent` subcommand has `RunE`) | **Leave untouched** — Cobra prints help; a no-op `RunE` would silence it |
| `cmd/grade.go` | **Trap 2** — `--agent` presence is already validated inside `runGrade` | **Leave untouched** — `MarkFlagRequired` would be redundant duplicate validation |
| `cmd/root.go` | Root command + `Execute()`, wires subcommands | No change expected |

## Running the regression check

Point the go-cobra agent at this directory and inspect the resulting diff:

```bash
squad run --agent go-cobra --working-dir go-cobra/testdata/cobra-mini \
  --provider openai --base-url <endpoint>/v1 --api-key local \
  --model <model> --openai-compat-max-tokens
```

**Pass criteria:**

- `git diff` touches **only** `cmd/version.go` (`Run` → `RunE`).
- `cmd/init.go` and `cmd/grade.go` are unchanged.
- `go build ./...` still passes.

Reset between runs with `git checkout -- go-cobra/testdata/cobra-mini`.

This is a self-contained Go module (its own `go.mod`); it lives under
`testdata/`, so Go tooling for the parent repo ignores it.
