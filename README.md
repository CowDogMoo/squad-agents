# Squad Agents

**Production-ready autonomous agents for code review, testing, and
documentation across Go, Python, Rust, and Ansible.**

[![License](https://img.shields.io/github/license/CowDogMoo/squad-agents?label=License&style=flat&color=blue&logo=github)](https://github.com/CowDogMoo/squad-agents/blob/main/LICENSE)
[![Pre-Commit](https://github.com/CowDogMoo/squad-agents/actions/workflows/pre-commit.yaml/badge.svg)](https://github.com/CowDogMoo/squad-agents/actions/workflows/pre-commit.yaml)
[![Validate Agents](https://github.com/CowDogMoo/squad-agents/actions/workflows/validate-agents.yaml/badge.svg)](https://github.com/CowDogMoo/squad-agents/actions/workflows/validate-agents.yaml)

---

## Overview

Official agent repository for
[Squad](https://github.com/cowdogmoo/squad) - an autonomous code review
and analysis CLI tool.

This repository provides production-ready agents that enable:

- **Autonomous code review** - Language-specific agents that discover issues,
  fix them, and verify compilation
- **Test coverage** - Agents that identify coverage gaps, write tests, and
  iterate to a target percentage
- **Documentation** - Agents that discover public declarations and add or
  improve doc comments
- **Security audits** - Vulnerability detection with CWE IDs and automated
  fixes
- **Composed pipelines** - Multi-agent pipelines that chain review, tests,
  and documentation with stages, dependency ordering, and gates

All agents use declarative YAML manifests and modular prompt architecture
following
[Anthropic's context engineering best practices](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents).

## Quick Start

```bash
# Install squad
go install github.com/cowdogmoo/squad/cmd/squad@latest

# Add this repository as an agent source
squad agents add official https://github.com/cowdogmoo/squad-agents.git

# List available agents
squad agents list

# Run an agent
squad run --agent go-review
```

### New to Squad?

Squad ships four concepts for composing AI work — **Agent**, **Skill**,
**Task tool**, and **Pipeline**. The canonical reference (with decision
flowcharts for which to reach for and when) is
[`squad/docs/agents-and-skills.md`](https://github.com/cowdogmoo/squad/blob/main/docs/agents-and-skills.md).
This repo ships agents and pipelines today; skills can live alongside
them in `.squad/skills/` per the open
[Agent Skills standard](https://agentskills.io).

## Available Agents

### Go Agents

| Agent                                    | Description                                                                    |
| ---------------------------------------- | ------------------------------------------------------------------------------ |
| [go-review](./go-review)                 | Code quality review - discovers issues, fixes violations, verifies compilation |
| [go-security-audit](./go-security-audit) | Security vulnerability detection with CWE IDs                                  |
| [go-cobra](./go-cobra)                   | Cobra/Viper CLI best practices                                                 |
| [go-doc-comments](./go-doc-comments)     | Go Doc Comments spec compliance                                                |
| [go-taskfile](./go-taskfile)             | Taskfile.yaml best practices                                                   |
| [go-tests](./go-tests)                   | Test coverage analysis and gap filling                                         |

### Python Agents

| Agent                                        | Description                               |
| -------------------------------------------- | ----------------------------------------- |
| [python-review](./python-review)             | Code quality and best practices           |
| [python-doc-comments](./python-doc-comments) | PEP 257 and Google Style docstrings       |
| [python-tests](./python-tests)               | pytest coverage with configurable targets |

### Rust Agents

| Agent                                    | Description                                 |
| ---------------------------------------- | ------------------------------------------- |
| [rust-review](./rust-review)             | Code quality review and best-practice fixes |
| [rust-doc-comments](./rust-doc-comments) | Rust doc comment conventions                |
| [rust-tests](./rust-tests)               | Test coverage analysis and gap filling      |

### Ansible Agents

| Agent                                  | Description                               |
| -------------------------------------- | ----------------------------------------- |
| [ansible-review](./ansible-review)     | Playbook/role best practices and security |
| [ansible-molecule](./ansible-molecule) | Molecule test verification depth          |

### Pipelines

Multi-stage orchestrators declared with `stages:` + `depends_on` + `gates:`
in `agent.yaml`. Each stage is a separate run with its own context; gates
verify before the next stage spends tokens. Use a pipeline when the
workflow is fixed and repeatable; reach for the Task tool from inside a
single agent when delegation is dynamic. See
[the decision guide](https://github.com/cowdogmoo/squad/blob/main/docs/agents-and-skills.md#decision-guide).

| Agent                                          | Description                                       | Children                                         |
| ---------------------------------------------- | ------------------------------------------------- | ------------------------------------------------ |
| [go-pipeline](./go-pipeline)                   | Full Go review pipeline                           | go-review, go-tests, go-doc-comments, go-cobra   |
| [python-pipeline](./python-pipeline)           | Full Python review pipeline                       | python-review, python-tests, python-doc-comments |
| [rust-pipeline](./rust-pipeline)               | Full Rust review pipeline                         | rust-review, rust-tests, rust-doc-comments       |
| [go-security-audit](./go-security-audit)       | Parallel injection + resources audit (inline)     | inline stages                                    |
| [nodejs-security-audit](./nodejs-security-audit) | Parallel injection + resources audit (inline)   | inline stages                                    |

### Specialized Agents

| Agent                                | Description                                                                       |
| ------------------------------------ | --------------------------------------------------------------------------------- |
| [degpt](./degpt)                     | Detects and rewrites LLM-generated prose to sound human-written                   |

### Agent Templates

Starter templates under [`_includes/`](./_includes/) that you copy into a new agent dir and customize. Unlike the agents above, these don't run as-is — they're parameterized scaffolds.

| Template                                                                  | Description                                                                                                                                                                                              |
| ------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [basic](./_includes/basic)                                                | Minimal three-file agent (system.md + agent.md + task.md) for a review-style workflow                                                                                                                    |
| [weekly-planner-template](./_includes/weekly-planner-template)            | Generic Google Doc planner → Google Calendar events; takes `PlannerDocId` / `CalendarId` / `AttendeeEmails` / `Timezone` as vars. Pairs with the personal-skills `bootstrap-weekly-planner-doc` skill to create the doc. |

### Skills

Skills live in the sibling
[squad-skills](https://github.com/cowdogmoo/squad-skills) repository —
see that repo for the catalog, authoring guide, and the open
[Agent Skills standard](https://agentskills.io). Agents here load them
via `Skill("<name>")` calls in their `system.md`. Current wirings:

- `degpt`, `go-scrub-comments`, `rust-scrub-comments` → `detect-llm-tells`
- `go-scrub-comments`, `rust-scrub-comments` → `comment-scrub-playbook`
- `go-doc-comments`, `python-doc-comments`, `rust-doc-comments`,
  `nodejs-doc-comments` → `doc-comments-discovery-and-fix-loop`
- `go-tests`, `python-tests`, `rust-tests`, `nodejs-tests` →
  `score-coverage-and-report-gaps`

## Features

| Feature                    | Description                                                                                 |
| -------------------------- | ------------------------------------------------------------------------------------------- |
| **Multi-Language**         | Go, Python, Rust, Node.js, and Ansible agents                                               |
| **Autonomous Fixing**      | Agents discover, fix, and verify in a single run                                            |
| **Mode Support**           | Edit mode (autonomous fixes) and readonly mode (analysis only)                              |
| **Pipeline Orchestration** | Multi-stage `stages:` + `depends_on` + `gates:` to chain agents and verify between them     |
| **Task Tool Delegation**   | Agents can spawn child agent runs via `Task(agent=..., prompt=...)` for isolated sub-jobs   |
| **Skills (open standard)** | Agents load on-demand playbooks via `Skill(name)` per [agentskills.io](https://agentskills.io) |
| **Modular Prompts**        | Composable system/agent/task prompt architecture (or single inline `prompt:` for one-shots) |
| **Budget Controls**        | Iteration limits, scale factors, and token budgets                                          |
| **CI/CD Validation**       | Automated agent structure and metadata validation                                           |
| **Template System**        | Scaffold new agents from built-in templates                                                 |

## Agent Structure

Most agents in this repo use the three-file split:

```text
agent-name/
├── agent.yaml      # Manifest with metadata, references, and budget
├── agent.md        # Agent-mode wrapper with execution rules
├── system.md       # Core system prompt (identity, hard rules, capabilities)
├── task.md         # Task instructions and constraints
└── references/     # Knowledge base documents (criteria, patterns, guides)
```

Self-contained one-shot agents can use an inline `prompt:` field in
`agent.yaml` instead — see the upstream `squad/docs/creating-agents.md`
for examples. Pipelines use a `stages:` block instead of
`entrypoint`/`wrapper` —
see [`go-pipeline/agent.yaml`](./go-pipeline/agent.yaml). The full
shape reference is upstream at
[`squad/docs/creating-agents.md`](https://github.com/cowdogmoo/squad/blob/main/docs/creating-agents.md).

### Agent Manifest (agent.yaml)

```yaml
name: go-review
version: 0.2.0
description: Autonomous Go code review agent
entrypoint: system.md
wrapper: agent.md
references:
  - references/go-review-criteria.md
task: task.md
budget:
  estimated_iterations: 30
  scale_factor: files
  files_per_iteration: 3
```

## Mode Support

Agents support multiple execution modes via Go `text/template` conditionals:

```bash
# Default edit mode - agent can make changes
squad run --agent go-review

# Readonly mode - agent only analyzes, no edits
squad run --agent go-review --mode readonly
```

### Conditional Block Syntax

```markdown
{{if eq .Mode "edit"}}
You are an autonomous agent. Fix issues and verify compilation.
{{end}}
{{if eq .Mode "readonly"}}
You are an analysis agent. Report issues but do NOT modify files.
{{end}}
```

Available template features:

- `{{if eq .Mode "value"}}...{{end}}` - include if mode matches
- `{{if ne .Mode "value"}}...{{end}}` - include if mode does NOT match
- `{{else}}` - alternative block
- Nesting is fully supported

## Usage Examples

```bash
# Run with default task instructions
squad run --agent go-review

# Add custom focus
squad run --agent go-review "Focus only on error handling in cmd/"

# Run security audit in readonly mode
squad run --agent go-security-audit --mode readonly

# Run a full pipeline
squad run --agent rust-pipeline
```

### How Prompts Work

The agent always receives its `task.md` instructions in the system bundle.
The CLI prompt (if any) becomes the user message:

| Command                                       | System Bundle              | User Message    |
| --------------------------------------------- | -------------------------- | --------------- |
| `squad run --agent go-review`                 | system.md + task.md + refs | "Begin."        |
| `squad run --agent go-review "Focus on cmd/"` | system.md + task.md + refs | "Focus on cmd/" |

## Agent Sources

Squad supports multiple agent sources:

```yaml
# ~/.config/squad/config.yaml
agents:
  repositories:
    official: https://github.com/cowdogmoo/squad-agents.git
    myorg: https://github.com/myorg/private-agents.git
  local_paths:
    - ~/dev/my-agents
```

```bash
# Manage sources via CLI
squad agents add <url>           # Add git repo
squad agents add <name> <url>    # Add with custom name
squad agents remove <name>       # Remove source
squad agents update              # Pull latest from all repos
```

## Creating Custom Agents

Use the `_includes/` directory as a starting point:

```bash
# Copy a template
cp -r _includes/basic my-agent

# Edit the manifest
vim my-agent/agent.yaml

# Customize prompts
vim my-agent/system.md
vim my-agent/task.md
```

Or scaffold a new agent:

```bash
squad init agent my-agent --from go-review
```

## Contributing

We welcome contributions! See [CONTRIBUTING.md](./CONTRIBUTING.md) for
guidelines on:

- Creating new agents
- Improving existing agents
- Prompt engineering best practices
- Testing guidelines

### Agent Validation

Before submitting an agent, ensure it passes validation:

```bash
# Validate locally with pre-commit
pre-commit run --all-files
```

The CI pipeline automatically validates:

- Required files exist (agent.yaml, agent.md, system.md, task.md)
- Metadata completeness (name, version, description, entrypoint, wrapper, task)
- Semantic version format
- Agent name matches directory name
- All referenced files exist
- Composed agent stages reference valid sub-agents

---

**Maintained by [Jayson Grace](https://github.com/CowDogMoo)** |
[Issues](https://github.com/cowdogmoo/squad-agents/issues) |
[Squad CLI](https://github.com/cowdogmoo/squad)
