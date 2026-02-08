# Contributing to Squad Agents

Thank you for your interest in contributing to Squad Agents! This document
provides guidelines for creating and improving agents.

## Table of Contents

- [Creating a New Agent](#creating-a-new-agent)
- [Agent Structure](#agent-structure)
- [Prompt Engineering Guidelines](#prompt-engineering-guidelines)
- [Testing Agents](#testing-agents)
- [Submitting Changes](#submitting-changes)

## Creating a New Agent

### Quick Start

```bash
# Clone the repository
git clone https://github.com/cowdogmoo/squad-agents.git
cd squad-agents

# Copy a template
cp -r _templates/basic my-agent

# Or fork an existing agent
cp -r go-review my-agent
```

### Required Files

Every agent must have:

| File | Purpose |
|------|---------|
| `agent.yaml` | Manifest with name, version, description, and file references |
| `system.md` | Core system prompt (identity, rules, capabilities) |
| `agent.md` | Agent-mode wrapper with execution rules |
| `task.md` | Task instructions included in every run |

Optional:

| File | Purpose |
|------|---------|
| `references/` | Knowledge base documents (criteria, examples, patterns) |

## Agent Structure

### agent.yaml

```yaml
name: my-agent
version: 0.1.0
description: Short description of what the agent does
entrypoint: system.md
wrapper: agent.md
references:
  - references/my-criteria.md
task: task.md
```

### system.md

The system prompt defines identity and capabilities:

```markdown
# IDENTITY

You are a [role description]. Your mission is to [primary goal].

# HARD RULES

1. Rule one - most important constraint
2. Rule two - another constraint
...

# CAPABILITIES

You have access to these tools:
- Glob: Find files by pattern
- Grep: Search file contents
- Read: Read file contents
...

# WORKFLOW

1. First step
2. Second step
...
```

### agent.md

The wrapper adds execution context:

```markdown
<agent>
name: my-agent
version: 0.1.0
</agent>

# EXECUTION RULES

- Complete the task autonomously
- Use tools efficiently
- Stop when done
```

### task.md

Default task instructions:

```markdown
# TASK

Review the codebase and [specific action].

# OUTPUT FORMAT

Emit a markdown report with:
- Summary of findings
- Table of issues
- Recommendations
```

## Prompt Engineering Guidelines

### Do

1. **Be specific** - Concrete rules beat vague guidelines
2. **Use examples** - Show correct and incorrect patterns
3. **Prioritize** - Number rules by importance
4. **Test iteratively** - Run, observe, adjust
5. **Document lessons** - Add comments for future maintainers

### Don't

1. **Over-engineer** - Simple prompts often work better
2. **Assume context** - The model doesn't know your codebase
3. **Use jargon** - Plain language is clearer
4. **Write walls of text** - Concise rules are followed better

### Mode Support

Use conditional blocks for mode-specific behavior:

```markdown
{{if eq .Mode "edit"}}
Fix issues directly using the Edit tool.
{{end}}
{{if eq .Mode "readonly"}}
Report issues but do NOT modify any files.
{{end}}
```

### Efficiency Rules

Agents should be efficient:

```markdown
# EFFICIENCY

1. Read each file ONCE - catalog issues in memory
2. Batch edits - multiple fixes per Edit call
3. Target ≤12 iterations for small codebases (≤20 files)
4. Do NOT re-read files after editing
```

### Proportionality

Avoid over-engineering:

```markdown
# PROPORTIONALITY

Before making a fix, ask: "Does this prevent a real bug or fix a
meaningful inconsistency?"

Skip:
- Micro-optimizations (strings.Builder for 3-element loops)
- Stylistic preferences without functional impact
- Changes that add complexity without clear benefit
```

## Testing Agents

### Manual Testing

```bash
# Run against a test codebase
cd /path/to/test/codebase
squad run --agent my-agent --print

# Test readonly mode
squad run --agent my-agent --mode readonly

# Check bundle output
squad run --agent my-agent --print-bundle --dry-run
```

### Grading Runs

Compare agent output against expert review:

1. Run agent on test codebase
2. Have expert review same codebase
3. Compare findings (coverage, accuracy, false positives)
4. Grade: A (expert-level) to F (unusable)
5. Iterate on prompts

### Metrics to Track

- **Iterations** - Fewer is better (target: ≤12 for small codebases)
- **Coverage** - Did it find all issues?
- **Accuracy** - Were findings correct?
- **False positives** - Did it report non-issues?

## Submitting Changes

### Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b my-agent`
3. Make changes
4. Test thoroughly
5. Submit PR with:
   - Description of the agent
   - Test results (iterations, findings)
   - Any known limitations

### Commit Messages

Use conventional commits:

```
feat(my-agent): add initial agent for X review
fix(go-review): reduce false positives for logging
docs(python-review): add examples to task.md
```

### Review Criteria

PRs are evaluated on:

- **Usefulness** - Does the agent solve a real problem?
- **Quality** - Are prompts well-structured and tested?
- **Efficiency** - Does it complete in reasonable iterations?
- **Documentation** - Is usage clear?

## Questions?

Open an issue or start a discussion in the
[Squad repository](https://github.com/cowdogmoo/squad/discussions).
