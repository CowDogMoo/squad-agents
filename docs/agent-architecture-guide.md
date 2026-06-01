# Agent Architecture Guide

The canonical reference for designing Squad agents lives upstream in the
[`squad`](https://github.com/cowdogmoo/squad) repo, not here. This file
used to maintain its own taxonomy; it now points at the source of truth
so guidance doesn't drift.

## Where to go

| Topic | Upstream doc |
|---|---|
| Four-concept model (Agent / Skill / Task tool / Pipeline) and decision flowcharts | [`squad/docs/agents-and-skills.md`](https://github.com/cowdogmoo/squad/blob/main/docs/agents-and-skills.md) |
| Agent directory layout, template variables, mode conditionals | [`squad/docs/creating-agents.md`](https://github.com/cowdogmoo/squad/blob/main/docs/creating-agents.md) |
| Composed pipeline manifest reference | [`squad/docs/pipelines.md`](https://github.com/cowdogmoo/squad/blob/main/docs/pipelines.md) |
| Pipeline engineering depth, artifact handoff, anti-patterns | [`squad/docs/agents-engineering-pipeline-basics.md`](https://github.com/cowdogmoo/squad/blob/main/docs/agents-engineering-pipeline-basics.md) |
| MCP server configuration and Skills-vs-MCP boundary | [`squad/docs/mcp-servers.md`](https://github.com/cowdogmoo/squad/blob/main/docs/mcp-servers.md) |

## Quick orientation for this repo

- **Leaf agents** (e.g. [`go-review`](../go-review)) — `agent.yaml` +
  `system.md` + `agent.md` + `task.md`. The standard shape.
- **Pipelines** (e.g. [`go-pipeline`](../go-pipeline),
  [`go-security-audit`](../go-security-audit)) — `agent.yaml` with a
  `stages:` block, `depends_on` ordering, and `gates:` for verification
  between stages.
- **Inline-prompt agents** — `agent.yaml` with a top-level `prompt:`
  field instead of the three-file split. A supported leaf-agent shape
  for self-contained one-shot agents.
- **Pipelines with `pre_gates:` and `mcp_servers:`** — supported
  per-stage fields for deterministic preludes and stage-scoped MCP
  servers.

For when to pick each, follow the decision flowchart in
[`agents-and-skills.md`](https://github.com/cowdogmoo/squad/blob/main/docs/agents-and-skills.md#decision-guide).
