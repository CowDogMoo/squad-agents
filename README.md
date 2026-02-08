# Squad Agents

**Official agent repository for [Squad](https://github.com/cowdogmoo/squad) -
autonomous code review and analysis agents.**

[![License](https://img.shields.io/github/license/CowDogMoo/squad-agents?label=License&style=flat&color=blue&logo=github)](https://github.com/CowDogMoo/squad-agents/blob/main/LICENSE)

---

## Overview

This repository contains production-ready agents for the Squad CLI. Each agent
is a self-contained prompt bundle that can autonomously review code, fix
issues, and verify results.

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

| Agent | Description |
|-------|-------------|
| [go-review](./go-review) | Autonomous Go code review - discovers issues, fixes them, verifies compilation |
| [go-security-audit](./go-security-audit) | Security vulnerability detection with CWE IDs |
| [go-cobra](./go-cobra) | Cobra/Viper CLI best practices |
| [go-doc-comments](./go-doc-comments) | Go documentation comments |
| [go-taskfile](./go-taskfile) | Taskfile.yaml best practices |
| [go-tests](./go-tests) | Go test coverage and quality |

### Python Agents

| Agent | Description |
|-------|-------------|
| [python-review](./python-review) | Python code quality and best practices |
| [python-doc-comments](./python-doc-comments) | Python docstring quality |
| [python-tests](./python-tests) | Python test coverage |

### Ansible Agents

| Agent | Description |
|-------|-------------|
| [ansible-review](./ansible-review) | Ansible playbook/role best practices |
| [ansible-molecule](./ansible-molecule) | Molecule test verification depth |

### Specialized Agents

| Agent | Description |
|-------|-------------|
| [recon](./recon) | Codebase reconnaissance and analysis |

## Agent Structure

Each agent directory contains:

```text
agent-name/
├── agent.yaml      # Manifest with metadata and references
├── agent.md        # Agent-mode wrapper instructions
├── system.md       # Core system prompt (identity, rules)
├── task.md         # Task instructions (always included)
└── references/     # Knowledge base documents
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
```

## Prompt Architecture

Following [Anthropic's context engineering best practices](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents),
prompts are modular:

```
System Bundle (always included):
├── agent.md     - wrapper with execution rules
├── system.md    - core identity and capabilities
├── references/  - knowledge base
└── task.md      - task instructions

User Message:
└── CLI prompt   - additional instructions (default: "Begin.")
```

## Mode Support

Agents support multiple execution modes via conditional blocks:

```bash
# Default edit mode - agent can make changes
squad run --agent go-review

# Readonly mode - agent only analyzes, no edits
squad run --agent go-review --mode readonly
```

### Conditional Block Syntax

Use Go `text/template` conditionals in prompt files:

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

# Run Python review
squad run --agent python-review
```

### How Prompts Work

The agent always receives its `task.md` instructions in the system bundle.
The CLI prompt (if any) becomes the user message:

| Command | System Bundle | User Message |
|---------|---------------|--------------|
| `squad run --agent go-review` | system.md + task.md + refs | "Begin." |
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

See [CONTRIBUTING.md](./CONTRIBUTING.md) for detailed guidelines.

## Contributing

We welcome contributions! See [CONTRIBUTING.md](./CONTRIBUTING.md) for:

- Creating new agents
- Improving existing agents
- Prompt engineering best practices
- Testing guidelines

## License

MIT License - see [LICENSE](./LICENSE) for details.

---

**Maintained by [CowDogMoo](https://github.com/CowDogMoo)** |
**Main Project: [Squad](https://github.com/cowdogmoo/squad)**
