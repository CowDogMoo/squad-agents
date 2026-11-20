# Agent regression evals

Each directory here is one `claude plugin eval` case (see `claude plugin eval --help`): a
`case.yaml` and a `fixture` link to the codebase the agent works on. The
cases are seeded from failures the agents have actually had, so a prompt or
model change that brings one back shows up as a lower score.

| Case | Agent | What it pins |
| --- | --- | --- |
| `go-cobra-cobra-mini` | go-cobra | Fixes the one real violation (`Run` instead of `RunE`) and leaves both traps alone: a parent command with no `RunE`, and a flag already validated in `RunE`. Both were false positives on real codebases. |
| `go-tests-covmini` | go-tests | The incidents its prompt narrates: work only the queued packages, never rename existing tests, no `_2`-suffix duplicates, no field from the wrong struct, edit only `_test.go` files, report a pre-existing failure instead of gutting the test, and report coverage as measured numbers. |
| `go-review-lint-clean` | go-review | A vet- and staticcheck-clean module with full coverage. The right result is zero edits. |
| `go-review-readonly` | go-review | Readonly mode on a module with a real finding: a report, and no edits. |

Graders check outcomes first: file contents, files created, and, for the
no-edit cases, that no `Edit` or `Write` call appears anywhere in the trace,
including the subagent's calls. A `tool_used` grader on `Agent` shows whether
the main session delegated to the agent; it is display-only (`arm:
with-only`).

## Running

The agents load skills from the [squad-skills][squad-skills] plugin, so the
runner stages one plugin holding this repository's agents and every skill of
a squad-skills checkout, then runs the cases against it:

```bash
python3 scripts/agent_evals.py validate     # no model calls; also runs in pytest
python3 scripts/agent_evals.py run --skills-dir ~/cowdogmoo/squad-skills \
  --case go-cobra-cobra-mini --runs 1       # one case, one run
python3 scripts/agent_evals.py run --skills-dir ~/cowdogmoo/squad-skills   # every case, 3 runs
```

Results land in `agent-evals-results/` (`result.json` and an HTML report).
The runner generates each case's scaffold, which copies the fixture into the
run's working directory, commits it, and downloads Go modules before the
agent's sandbox starts; it also sets `GOPROXY=off` and `GOTOOLCHAIN=local`,
because a case may only set `EVAL_*` variables.

`claude plugin eval` refuses to grant Bash on a machine whose `~/.aws`
config uses `credential_process`. On such a machine add `--without-bash`:
the cases still run, but go-tests cannot build or measure coverage, so only
go-cobra and the readonly case are meaningful.

## Ablation and model choice

- `--ablation with-without` runs every case a second time without the plugin
  and reports the delta: what the agent and its skills add over plain Claude
  on the same task.
- Every agent says `model: inherit`, so a subagent runs on the model the case
  runs on, and `--model` compares models for all agents at once:

  ```bash
  for m in claude-haiku-5-5 claude-sonnet-5-5 claude-opus-5-5; do
    python3 scripts/agent_evals.py run --skills-dir ~/cowdogmoo/squad-skills \
      --model "$m" --runs 3 --out "agent-evals-results/$m"
  done
  ```

Change an agent's `model:` only when the results justify it: for example,
pin a cheaper model when its mean score on that agent's cases is within
0.05 of the default's at three or more runs per case and it fails no grader
the default passes, or pin a stronger one when it clears a grader the default
fails in at least two of three runs. Read the transcripts of any case whose
score moved before acting on it.

[squad-skills]: https://github.com/CowDogMoo/squad-skills
