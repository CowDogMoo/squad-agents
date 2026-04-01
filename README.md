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
- **Pipeline orchestration** - Multi-agent pipelines that chain review, tests,
  and documentation with context passing

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

### Pipeline Agents

Orchestrators that chain multiple agents sequentially with context passing:

| Agent                                | Description                 | Children                                         |
| ------------------------------------ | --------------------------- | ------------------------------------------------ |
| [go-pipeline](./go-pipeline)         | Full Go review pipeline     | go-review, go-tests, go-doc-comments, go-cobra   |
| [python-pipeline](./python-pipeline) | Full Python review pipeline | python-review, python-tests, python-doc-comments |
| [rust-pipeline](./rust-pipeline)     | Full Rust review pipeline   | rust-review, rust-tests, rust-doc-comments       |

### Specialized Agents

| Agent            | Description                                                     |
| ---------------- | --------------------------------------------------------------- |
| [degpt](./degpt) | Detects and rewrites LLM-generated prose to sound human-written |

## Features

| Feature                    | Description                                                    |
| -------------------------- | -------------------------------------------------------------- |
| **Multi-Language**         | Go, Python, Rust, and Ansible agents                           |
| **Autonomous Fixing**      | Agents discover, fix, and verify in a single run               |
| **Mode Support**           | Edit mode (autonomous fixes) and readonly mode (analysis only) |
| **Pipeline Orchestration** | Chain agents with context passing to avoid redundant work      |
| **Modular Prompts**        | Composable system/agent/task prompt architecture               |
| **Budget Controls**        | Iteration limits, scale factors, and token budgets             |
| **CI/CD Validation**       | Automated agent structure and metadata validation              |
| **Template System**        | Scaffold new agents from built-in templates                    |

## Agent Structure

Each agent directory contains:

```text
agent-name/
├── agent.yaml      # Manifest with metadata, references, and budget
├── agent.md        # Agent-mode wrapper with execution rules
├── system.md       # Core system prompt (identity, hard rules, capabilities)
├── task.md         # Task instructions and constraints
└── references/     # Knowledge base documents (criteria, patterns, guides)
```

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

Use the `_templates/` directory as a starting point:

```bash
# Copy a template
cp -r _templates/basic my-agent

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
- Orchestrator children point to valid agents

## License

This repository is licensed under the MIT License - see [LICENSE](./LICENSE)
for details.

---

**Maintained by [CowDogMoo](https://github.com/CowDogMoo)** |
[Issues](https://github.com/cowdogmoo/squad-agents/issues) |
[Squad CLI](https://github.com/cowdogmoo/squad)
