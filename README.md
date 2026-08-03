# Squad Agents

**Production-ready autonomous agents for code review, testing, security
auditing, and documentation across Go, Python, Rust, Node.js, and Ansible.**

[![License](https://img.shields.io/github/license/CowDogMoo/squad-agents?label=License&style=flat&color=blue&logo=github)](https://github.com/CowDogMoo/squad-agents/blob/main/LICENSE)
[![Pre-Commit](https://github.com/CowDogMoo/squad-agents/actions/workflows/pre-commit.yaml/badge.svg)](https://github.com/CowDogMoo/squad-agents/actions/workflows/pre-commit.yaml)
[![Validate Agents](https://github.com/CowDogMoo/squad-agents/actions/workflows/validate-agents.yaml/badge.svg)](https://github.com/CowDogMoo/squad-agents/actions/workflows/validate-agents.yaml)

---

## Overview

Official agent repository for [Squad](https://github.com/cowdogmoo/squad) — an
autonomous code review and analysis CLI tool.

Agents here are drop-in extensions: point Squad at this repo, pick an agent,
and it autonomously discovers issues, fixes them, and verifies the result
compiles or passes tests — no scripting required. Multi-stage pipelines chain
agents with dependency ordering and verification gates so a single command
runs a complete quality workflow.

## Features

| Feature | Description |
|---------|-------------|
| **Multi-Language** | Go, Python, Rust, Node.js, and Ansible agents |
| **Autonomous Fixing** | Agents discover, fix, and verify in a single run |
| **Edit / Readonly Modes** | Autonomous fixes or analysis-only reporting |
| **Multi-Provider Models** | Agents support Anthropic, Google, and OpenAI providers |
| **Pipeline Orchestration** | `stages:` + `depends_on` + `gates:` to chain agents and verify between them |
| **Task Tool Delegation** | Agents spawn child runs via `Task(agent=..., prompt=...)` for isolated sub-jobs |
| **Skills (open standard)** | Load on-demand playbooks via `Skill(name)` per [agentskills.io](https://agentskills.io) |
| **Modular Prompts** | Composable system/agent/task architecture, or inline `prompt:` for one-shots |
| **Budget Controls** | Iteration limits, scale factors, and per-stage cost caps |
| **CI/CD Validation** | Automated structure and metadata validation on every PR |
| **Template System** | Scaffold new agents from built-in starter templates |

## Quick Start

```bash
# Install Squad
go install github.com/cowdogmoo/squad/cmd/squad@latest

# Add this repository as an agent source
squad agents add official https://github.com/cowdogmoo/squad-agents.git

# List available agents
squad agents list

# Run an agent against your codebase
squad run --agent go-review
```

### First run in under 60 seconds

```bash
cd /path/to/your/go/project

# Autonomous code review — discovers issues, fixes them, verifies compilation
squad run --agent go-review

# Analysis only — reports issues without modifying files
squad run --agent go-review --mode readonly

# Full quality pipeline — review → tests → doc comments
squad run --agent go-pipeline
```

## Available Agents

### Go Agents

| Agent | Description |
|-------|-------------|
| [go-review](./go-review) | Code quality review — discovers issues, fixes violations, verifies compilation |
| [go-security-audit](./go-security-audit) | Parallel injection + resource vulnerability detection with CWE IDs |
| [go-cobra](./go-cobra) | Cobra/Viper CLI best practices |
| [go-doc-comments](./go-doc-comments) | Go Doc Comments spec compliance |
| [go-tests](./go-tests) | Test coverage analysis and gap filling |

### Python Agents

| Agent | Description |
|-------|-------------|
| [python-review](./python-review) | Code quality and best practices |
| [python-security-audit](./python-security-audit) | Parallel injection + resource vulnerability detection |
| [python-doc-comments](./python-doc-comments) | PEP 257 and Google Style docstrings |
| [python-tests](./python-tests) | pytest coverage with configurable targets |

### Rust Agents

| Agent | Description |
|-------|-------------|
| [rust-review](./rust-review) | Code quality review and best-practice fixes |
| [rust-doc-comments](./rust-doc-comments) | Rust doc comment conventions |
| [rust-tests](./rust-tests) | Test coverage analysis and gap filling |

### Node.js / TypeScript Agents

| Agent | Description |
|-------|-------------|
| [nodejs-review](./nodejs-review) | Code quality review — discovers issues, fixes violations, verifies lint and type checks |
| [nodejs-security-audit](./nodejs-security-audit) | Parallel injection + resource vulnerability detection |
| [nodejs-doc-comments](./nodejs-doc-comments) | JSDoc compliance on exported declarations |
| [nodejs-tests](./nodejs-tests) | Test coverage analysis and gap filling |

### Ansible Agents

| Agent | Description |
|-------|-------------|
| [ansible-review](./ansible-review) | Playbook/role best practices and security |
| [ansible-molecule](./ansible-molecule) | Molecule test verification depth |

### Pipelines

Multi-stage orchestrators declared with `stages:` + `depends_on` + `gates:`.
Each stage is a separate run with its own context; gates verify before the next
stage spends tokens. Use a pipeline when the workflow is fixed and repeatable.
See the [decision guide](https://github.com/cowdogmoo/squad/blob/main/docs/agents-and-skills.md#decision-guide).

| Pipeline | Description | Stages |
|----------|-------------|--------|
| [go-pipeline](./go-pipeline) | Full Go quality pipeline | go-cobra → go-review → go-tests → go-doc-comments |
| [python-pipeline](./python-pipeline) | Full Python quality pipeline | python-review → python-tests → python-doc-comments |
| [rust-pipeline](./rust-pipeline) | Full Rust quality pipeline | rust-review → rust-tests → rust-doc-comments |
| [go-security-audit](./go-security-audit) | Parallel Go security audit | injection ∥ resources |
| [nodejs-security-audit](./nodejs-security-audit) | Parallel Node.js security audit | injection ∥ resources |
| [python-security-audit](./python-security-audit) | Parallel Python security audit | injection ∥ resources |

### Specialized Agents

| Agent | Description |
|-------|-------------|
| [degpt](./degpt) | Detects and rewrites LLM-generated prose to sound human-written |
| [readme](./readme) | Analyzes project structure and generates a comprehensive README.md following progressive disclosure best practices |
| [taskfile-review](./taskfile-review) | go-task Taskfile best practices, security, and maintainability — language-agnostic |

### Agent Templates

Starter templates under [`_includes/`](./_includes/) — copy and customize,
they don't run as-is.

| Template | Description |
|----------|-------------|
| [basic](./_includes/basic) | Minimal three-file agent (system.md + agent.md + task.md) for a review-style workflow |

## Usage

```bash
# Run with default task instructions
squad run --agent go-review

# Narrow the scope with a custom prompt
squad run --agent go-review "Focus only on error handling in cmd/"

# Security audit, analysis only
squad run --agent go-security-audit --mode readonly

# Full pipeline
squad run --agent rust-pipeline

# Inspect the assembled prompt bundle without running
squad run --agent go-review --print-bundle --dry-run
```

### How Prompts Work

The agent always receives its `task.md` in the system bundle. A CLI prompt
becomes the user message:

| Command | System Bundle | User Message |
|---------|---------------|--------------|
| `squad run --agent go-review` | system.md + task.md + refs | `"Begin."` |
| `squad run --agent go-review "Focus on cmd/"` | system.md + task.md + refs | `"Focus on cmd/"` |

### Mode Support

Every agent defaults to edit mode and switches to readonly when asked:

```bash
# Edit mode (default) — agent fixes issues autonomously
squad run --agent go-review

# Readonly mode — agent reports issues, no file modifications
squad run --agent go-review --mode readonly
```

Mode is dispatched at runtime, not render time. Each `system.md` describes
both modes in prose (edit default; readonly opt-in on phrases like
"readonly" or "report only"), squad injects a literal `Mode: readonly` line
into the assembled prompt, and readonly runs additionally reject
Write/Edit/MultiEdit at the tool layer. In Claude Code, put the keyword in
the task prompt: `"readonly — review the crate at ..."`.

### Model Providers

Agents declare supported models in `agent.yaml`. Squad selects the active
provider from your config:

```yaml
models:
  - model: claude-sonnet-4-6
    provider: anthropic
  - model: gemini-2.5-flash
    provider: google
  - model: gpt-4.1-mini
    provider: openai
```

## Agent Structure

Most agents use the three-file split:

```text
agent-name/
├── agent.yaml      # Manifest: metadata, model list, references, budget
├── agent.md        # Agent-mode wrapper with execution rules
├── system.md       # Core system prompt: identity, hard rules, capabilities
├── task.md         # Default task instructions included in every run
└── references/     # Knowledge base: criteria, patterns, guides
```

Self-contained one-shot agents use an inline `prompt:` field in `agent.yaml`
instead. Pipelines replace `entrypoint`/`wrapper` with a `stages:` block.
The full shape reference is at
[`squad/docs/creating-agents.md`](https://github.com/cowdogmoo/squad/blob/main/docs/creating-agents.md).

### Claude-Native Format (dual-host)

Every `system.md` in this repo starts with a YAML frontmatter block
(`name`, `description`, `tools`, `model`) and contains **no Go-template
syntax**. The same file works in two hosts:

- **squad** detects the frontmatter, strips it (its metadata comes from
  `agent.yaml`), and delivers the body verbatim — no template rendering.
- **Claude Code** loads the file directly as a custom agent. Register with
  a symlink:

  ```bash
  ln -s "$(pwd)/go-review/system.md" ~/.claude/agents/go-review.md
  ```

There is no converted copy to drift: edit the file once, both hosts pick it
up. Authoring rules for the format (mode prose, dual-host reference
loading, no includes) are in
[`squad/docs/creating-agents.md`](https://github.com/cowdogmoo/squad/blob/main/docs/creating-agents.md#systemmd-main-prompt).

### agent.yaml Reference

```yaml
name: go-review
version: 0.3.0
description: Autonomous Go code review agent
models:
  - model: claude-sonnet-4-6
    provider: anthropic
  - model: gemini-2.5-flash
    provider: google
entrypoint: system.md
wrapper: agent.md
references:
  - references/go-review-criteria.md
task: task.md
budget:
  estimated_iterations: 20
  scale_factor: files
  files_per_iteration: 3
```

### Pipeline manifest

```yaml
name: go-pipeline
version: 0.3.0
description: Sequential Go quality pipeline

stages:
  - name: cobra
    agent: go-cobra
  - name: review
    agent: go-review
    depends_on: [cobra]
  - name: tests
    agent: go-tests
    depends_on: [review]
  - name: docs
    agent: go-doc-comments
    depends_on: [tests]

gates:
  - after: tests
    command: "go test ./..."
    on_failure: stop
  - after: docs
    command: "go build ./..."
    on_failure: stop
```

## Agent Sources

Squad supports multiple agent sources in `~/.config/squad/config.yaml`:

```yaml
agents:
  repositories:
    official: https://github.com/cowdogmoo/squad-agents.git
    myorg: https://github.com/myorg/private-agents.git
  local_paths:
    - ~/dev/my-agents
```

```bash
squad agents add <url>           # Add git repo
squad agents add <name> <url>    # Add with custom name
squad agents remove <name>       # Remove source
squad agents update              # Pull latest from all repos
```

## Creating Custom Agents

Copy a template and customize:

```bash
# Clone the repo
git clone https://github.com/cowdogmoo/squad-agents.git
cd squad-agents

# Start from the minimal template
cp -r _includes/basic my-agent

# Or fork an existing agent
cp -r go-review my-agent
```

Or use the Squad scaffold command:

```bash
squad init agent my-agent --from go-review
```

Then edit `my-agent/agent.yaml` to set name, version, description, and budget;
update `system.md` with identity and hard rules; and update `task.md` with
default task instructions.

## Skills

Agents load skills via `Skill("<name>")` calls in their `system.md`,
following the open [Agent Skills standard](https://agentskills.io).
The skills come from two collections, split by coupling:

- **[`skills/`](./skills) (this repo)** — reference knowledge bases
  coupled to exactly one agent (`go-review-criteria`,
  `ansible-standards`, `rust-testing-patterns`, …), plus the
  orchestration skills that chain this repo's agents (`go-pipeline`,
  `rust-pipeline`, `go-security-audit`). Each agent's `references/`
  entries are symlinks into this directory, so an agent and its
  reference docs always change in the same commit. Naming follows the
  agent (`go-review` → `go-review-criteria`). Each one is also a
  standalone knowledge base a human can call directly — see below.
- **[squad-skills](https://github.com/cowdogmoo/squad-skills) (sibling
  repo)** — reusable, host-portable procedures shared across agents and
  hosts. See that repo for the catalog and authoring guide.

Rule of thumb: a skill that exists for one agent lives in `skills/`
here; a skill reusable across agents or hosts lives in squad-skills.
The split is about **coupling**, not how broad the topic is — "how to
review Go code" is a universal topic and still belongs here, because
exactly one agent loads it.

### Calling reference skills directly

Whether a human can invoke a skill is a property of the skill, not of
which repo holds it. Every skill in `skills/` states what it covers and
when to reach for it, so any of them can be called on its own. Symlink
the ones you want into your host's skills directory:

```bash
# One skill
ln -s "$PWD/skills/readme-standards" ~/.claude/skills/readme-standards

# Or all of them
for d in "$PWD"/skills/*/; do
    ln -sfn "$d" ~/.claude/skills/"$(basename "$d")"
done
```

Then `Skill("readme-standards")` works in any project — useful for
reviewing a README by hand without running the full `readme` agent.

When writing a new reference skill, make the `description` say what the
skill covers and when to use it. Do not write it as "internal to agent
X" — that hides the skill from the host's routing, which is what decides
whether it ever gets loaded at all.

### Shared-skill wirings

These agents load squad-skills skills at runtime, so squad-skills must
be installed alongside this plugin — `squad-agents` declares it as a
plugin dependency and will not enable without it:

| squad-skills skill | Loaded by |
|--------------------|-----------|
| `detect-llm-tells` | degpt, go-scrub-comments, rust-scrub-comments |
| `comment-scrub-playbook` | go-scrub-comments, rust-scrub-comments |
| `doc-comments-discovery-and-fix-loop` | go-, python-, rust-, nodejs-doc-comments |
| `score-coverage-and-report-gaps` | go-, python-, rust-, nodejs-tests |
| `test-writer-honesty` | go-, python-, rust-, nodejs-tests |
| `enqueue-coverage-targets-<lang>` | the matching `<lang>-tests` agent |

### Installing in Claude Code

Both collections ship as plugins from the `cowdogmoo` marketplace
defined in this repo (`.claude-plugin/marketplace.json`). Dependencies
are not auto-installed, so install both:

```text
/plugin marketplace add cowdogmoo/squad-agents
/plugin install squad-skills@cowdogmoo
/plugin install squad-agents@cowdogmoo
```

## Contributing

We welcome contributions. See [CONTRIBUTING.md](./CONTRIBUTING.md) for the
full guide on creating agents, prompt engineering best practices, and testing.

### Validation

Every agent is validated by CI. Before submitting, run pre-commit locally:

```bash
pre-commit run --all-files
```

CI checks:

- Required files exist (`agent.yaml`, `agent.md`, `system.md`, `task.md`)
- Metadata completeness (`name`, `version`, `description`, `entrypoint`, `wrapper`, `task`)
- Semantic version format
- Agent name matches directory name
- All referenced files exist
- Pipeline stages reference valid sub-agents

### Commit Style

Use conventional commits:

```
feat(my-agent): add initial agent for X review
fix(go-review): reduce false positives for logging
docs(python-review): add examples to task.md
```

---

**Maintained by [Jayson Grace](https://github.com/CowDogMoo)** |
[Issues](https://github.com/cowdogmoo/squad-agents/issues) |
[Squad CLI](https://github.com/cowdogmoo/squad)
