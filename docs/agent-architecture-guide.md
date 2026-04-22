# Agent Architecture Guide

A practical reference for designing, structuring, and composing
autonomous agents in this repository. Grounded in patterns from
[Anthropic's multi-agent research](https://www.anthropic.com/engineering/multi-agent-research-system),
[Microsoft's orchestration taxonomy](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns),
and lessons from production multi-agent systems.

---

## Table of Contents

- [Core Concepts](#core-concepts)
- [Agent Types](#agent-types)
- [File Structure](#file-structure)
- [Prompt Decomposition](#prompt-decomposition)
- [Composition Patterns](#composition-patterns)
- [Template System](#template-system)
- [Design Principles](#design-principles)
- [Anti-Patterns](#anti-patterns)
- [Scaling Guidance](#scaling-guidance)
- [References](#references)

---

## Core Concepts

### The Three-Layer Prompt Model

Every agent decomposes its prompt into three layers, each in its own
file. This separation is universal across agent frameworks (CrewAI,
AutoGen, LangGraph) and maps directly to how LLMs process instructions:

| Layer | File | Purpose | Analogy |
|-------|------|---------|---------|
| **Identity** | `system.md` | Who you are, what rules you follow, how you work | Job description |
| **Wrapper** | `agent.md` | Operational constraints, tool usage, budget rules | Standard operating procedures |
| **Task** | `task.md` | What to do right now | Today's assignment |

Each layer serves a distinct cognitive function:

- **system.md** establishes the agent's frame of reference _before_ it
  sees domain content. Front-loading identity and rules reduces drift.
- **agent.md** acts as a "last-mile reminder" of execution rules that
  might get buried in a large system prompt. Keep it under 50 lines.
- **task.md** should be readable as a standalone instruction to someone
  who hasn't read system.md. It's the "if you only read one thing" file.

### Progressive Disclosure

Inspired by
[Anthropic's Agent Skills architecture](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills),
agents load context in tiers to minimize token waste:

```
Tier 1 (always loaded):  agent.yaml metadata — name, description, version
Tier 2 (loaded at run):  system.md + agent.md + task.md — full instructions
Tier 3 (supplementary):  references/*.md — knowledge base documents
```

The `references/` directory holds domain knowledge (security guides,
review criteria, best-practice documents) that the agent needs for
analysis but that doesn't define its behavior. Reference documents are
injected into the system prompt automatically — agents should NOT try to
Read them as files.

### Declarative Manifests

The `agent.yaml` manifest is the single source of truth for an agent's
composition. It declares _what_ the agent needs (files, models,
references, gates) without encoding _how_ the runner executes it. This
keeps agent definitions portable across different runners and
environments.

---

## Agent Types

This repository supports three agent types, each suited to different
task structures.

### Leaf Agent

A single-purpose agent with its own prompt files. The simplest and most
common type.

```yaml
name: go-review
version: 0.3.0
description: Autonomous Go code review agent

entrypoint: system.md
wrapper: agent.md
task: task.md
references:
  - references/go-review-criteria.md
```

**When to use:** The task is self-contained — one domain, one workflow,
one output.

### Composed Agent

A multi-stage agent where each stage has inline prompt definitions. The
stages may run in parallel or sequentially. All prompt files live in the
same directory.

```yaml
name: go-security-audit
version: 0.3.0
description: Parallel security audit — injection + resources stages

stages:
  - name: injection
    entrypoint: injection-system.md
    wrapper: injection-agent.md
    task: injection-task.md
    references:
      - references/golang-security-guide.md
  - name: resources
    entrypoint: resources-system.md
    wrapper: resources-agent.md
    task: resources-task.md
    references:
      - references/golang-security-guide.md

gates:
  - after: injection
    command: "go build ./..."
    on_failure: stop
  - after: resources
    command: "go test ./..."
    on_failure: stop
```

**When to use:** The task naturally splits into independent domains that
can run concurrently (e.g., injection vs resource auditing), or into
sequential phases where each stage has fundamentally different
instructions.

### Pipeline Agent

An orchestrator that chains existing leaf agents. The pipeline itself has
no prompt files — it references other agents by name and defines
execution order.

```yaml
name: go-pipeline
version: 0.3.0
description: Sequential Go review pipeline

stages:
  - name: review
    agent: go-review
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
```

**When to use:** You want to chain existing agents into a workflow
without writing new prompts. Each referenced agent must exist as a
sibling directory.

### Choosing the Right Type

```
Is the task a single domain with one workflow?
  YES → Leaf Agent

Does it split into independent sub-domains?
  YES → Composed Agent (parallel stages)

Does it need sequential phases building on prior output?
  YES → Composed Agent (sequential stages with depends_on)
        or Pipeline Agent (if stages map to existing leaf agents)

Are you reusing existing leaf agents?
  YES → Pipeline Agent
  NO  → Composed Agent with inline stages
```

---

## File Structure

### Leaf Agent Layout

```
agent-name/
├── agent.yaml                  # Manifest
├── system.md                   # Identity, rules, workflow, output format
├── agent.md                    # Execution wrapper (~30 lines)
├── task.md                     # Task mission (~25 lines)
├── README.md                   # Human documentation (optional)
└── references/                 # Knowledge base (optional)
    └── criteria.md
```

### Composed Agent Layout (2 stages)

Use flat naming with stage prefixes. This keeps everything discoverable
at a glance without unnecessary directory nesting.

```
agent-name/
├── agent.yaml                  # Orchestrator manifest with stages + gates
├── README.md                   # Human documentation
├── <stage-a>-system.md         # Stage A identity + rules
├── <stage-a>-agent.md          # Stage A execution wrapper
├── <stage-a>-task.md           # Stage A task mission
├── <stage-b>-system.md         # Stage B identity + rules
├── <stage-b>-agent.md          # Stage B execution wrapper
├── <stage-b>-task.md           # Stage B task mission
└── references/                 # Shared knowledge base
    └── guide.md
```

### Composed Agent Layout (3+ stages)

At three or more stages, switch to subdirectories. Flat naming becomes
noisy and the directory listing gets hard to scan.

```
agent-name/
├── agent.yaml
├── README.md
├── stages/
│   ├── stage-a/
│   │   ├── system.md
│   │   ├── agent.md
│   │   └── task.md
│   ├── stage-b/
│   │   ├── system.md
│   │   ├── agent.md
│   │   └── task.md
│   └── stage-c/
│       ├── system.md
│       ├── agent.md
│       └── task.md
└── references/
    └── guide.md
```

Update `agent.yaml` paths accordingly:

```yaml
stages:
  - name: stage-a
    entrypoint: stages/stage-a/system.md
    wrapper: stages/stage-a/agent.md
    task: stages/stage-a/task.md
```

### Pipeline Agent Layout

Pipelines have no prompt files of their own — just the manifest.

```
pipeline-name/
└── agent.yaml                  # References other agents by name
```

---

## Prompt Decomposition

### system.md Structure

The system prompt is the heavyweight file. Order sections so the agent
establishes its frame before encountering domain-specific content:

```markdown
# IDENTITY and PURPOSE
Who you are, what you specialize in, what you explicitly ignore.

# KNOWLEDGE BASE
How to use reference documents (already in prompt, don't Read them).

# HARD RULES
Numbered, overrides everything. The agent's constitution.

# WORKFLOW
Phase 1-N sequence with concrete steps.

# YOUR CATEGORIES
Domain-specific checklist of what to look for.

# CATEGORIES TO IGNORE
Explicit non-overlap boundary for multi-stage agents.

{{include "severity/standard.md"}}

# WHAT TO FIX
Concrete vulnerable/incorrect patterns with code examples.

# WHAT NOT TO FIX
Guardrails against scope creep.

# HOW TO FIX
Correct replacement patterns with code examples.

# OUTPUT FORMAT
Mandatory report structure.

# INPUT
Anchor for user request.
```

**Section ordering rationale:**

1. **Identity first** — establishes the agent's frame before rules.
2. **Rules before workflow** — constraints override procedures.
3. **Categories before patterns** — know what to look for before seeing
   examples.
4. **Output format last** — the agent needs all prior context to
   produce the right output.

### agent.md Structure

Keep under 50 lines. This is an operational checklist, not a second
system prompt.

```markdown
# AGENT MODE
One-line identity reinforcement.

# EXECUTION RULES
- Discover first (Glob/Read)
- Tool usage constraints
- Efficiency requirements (iterations, batching)
- Termination conditions

# OUTPUT COMPLIANCE
Required sections checklist.

# INPUT
User request and constraints.
```

### task.md Structure

Keep under 30 lines. Readable standalone.

```markdown
[1-2 sentence mission statement with scope.]

[Discovery instructions — how to start.]

IMPORTANT CONSTRAINTS:
- Scope boundary — what to focus on
- Key operational rules — most critical subset
- Termination conditions — when to stop
```

### Hard Rules

Hard rules are the agent's constitution. They override everything else,
including reference documents. Effective hard rules share these traits:

- **Numbered** for easy citation ("violated rule 11")
- **Imperative** ("Do X", not "You should X")
- **Testable** ("Changes must compile" vs "Write good code")
- **Ordered by priority** (discovery rules first, wind-down last)

Common hard rule categories:

| Category | Example |
|----------|---------|
| Discovery | "Use Glob with `**/*.go` to find all source files" |
| Compilation | "Run `go build ./...` after every batch of edits" |
| Scope | "Security focus only. Skip code quality and style" |
| Dependencies | "No new dependencies. Do not add imports not in go.mod" |
| Safety | "Test-asserted behavior is UNFIXABLE" |
| Budget | "Produce the report before spending 60% of your cost budget" |
| Termination | "STOP after verification passes. No re-reading" |

### The "Categories to Ignore" Pattern

For multi-stage agents where stages run in parallel on overlapping
codebases, each stage must declare what it _ignores_:

```markdown
# CATEGORIES TO IGNORE (another agent handles these)

Do NOT report or fix issues in these categories:
- Command Injection
- SQL Injection
- XSS
```

This prevents duplicate work and conflicting fixes — the primary cause
of the
[17x error amplification problem](https://towardsdatascience.com/why-your-multi-agent-system-is-failing-escaping-the-17x-error-trap-of-the-bag-of-agents/)
in multi-agent systems.

---

## Composition Patterns

### Concurrent (Fan-Out / Fan-In)

Multiple stages process the same codebase simultaneously, each
specializing in different categories. Results are independent.

```
Stage A (injection)  ──┐
                       ├──→ Gates (build, test)
Stage B (resources)  ──┘
```

**When to use:**

- Sub-tasks are [embarrassingly parallel](https://en.wikipedia.org/wiki/Embarrassingly_parallel)
- Stages don't depend on each other's output
- Different domains can be audited independently

**Key requirements:**

- Each stage must declare non-overlapping scope
- Each stage must declare what it ignores
- Gates run after all stages complete to catch conflicts

### Sequential (Pipeline)

Stages run in order, each building on the previous stage's output.
Later stages see the full context of earlier stages.

```
Stage A (review) → Stage B (tests) → Stage C (docs)
```

**When to use:**

- Later stages depend on earlier output
- Progressive refinement (draft → review → polish)
- The order of operations matters

**Key requirements:**

- Use `depends_on` to declare ordering
- Gate after critical stages to prevent error propagation

### Hierarchical (Orchestrator + Workers)

A lead agent coordinates specialized worker agents, distributing
sub-tasks and synthesizing results. This is the pattern used by
[Anthropic's multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system).

```
Lead Agent
├── Worker A (3-10 tool calls)
├── Worker B (10-15 tool calls)
└── Worker C (10-15 tool calls)
```

**In this repo**, pipelines approximate this pattern: the pipeline
manifest acts as the orchestrator, and each referenced agent is a
worker.

### Quality Gates

Gates are verification checkpoints that run shell commands after stages.
They prevent broken output from propagating downstream.

```yaml
gates:
  - after: stage-name
    command: "go build ./..."    # Must exit 0
    on_failure: stop             # stop | continue
```

**Gate placement rules:**

- After every stage that modifies code: `go build ./...`
- After the final modifying stage: `go test ./...`
- After stages with high error potential: custom linters

Gates implement the "validate before propagating" principle from the
[Microsoft agent design patterns guide](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns):
agent output should be validated before passing it to the next agent.

---

## Template System

### Include Directives

The `{{include "path/to/file.md"}}` directive injects shared content
from `_templates/` into agent prompts at assembly time. Use includes for
content that is:

- Identical across 3+ agents
- Structural (severity definitions, output formats) rather than
  behavioral
- Stable (changes infrequently)

**Available templates:**

| Path | Content | Used by |
|------|---------|---------|
| `severity/standard.md` | Severity level definitions (CRITICAL/HIGH/MEDIUM/LOW/INFO) | Most agents |
| `output/edit-format.md` | Standardized output format for edit-mode agents | Review agents |
| `output/readonly-format.md` | Standardized output format for readonly-mode agents | Review agents |
| `hard-rules/universal.md` | 13 common hard rules for all review agents | As needed |
| `hard-rules/efficiency.md` | Iteration budgets and batching rules | Scrub/analysis agents |

### Conditional Directives

Use Go `text/template` conditionals for mode-dependent behavior:

```markdown
{{if eq .Mode "edit"}}
Fix issues directly using the Edit tool.
Run `go build ./...` after every batch of edits.
{{end}}
{{if eq .Mode "readonly"}}
Report issues but do NOT modify any files.
Use the output format for analysis-only reports.
{{end}}
```

### When to Create a Template vs Duplicate

| Scenario | Action |
|----------|--------|
| Identical content in 3+ agents | Create a template in `_templates/` |
| Identical content in 2 agents | Duplicate is fine — self-containment beats DRY |
| Similar but not identical content | Duplicate and specialize — don't over-abstract |
| Content that changes per-agent | Never template — embed directly |

Self-contained readability of each system.md is more valuable than
eliminating duplication at small scale.

---

## Design Principles

### 1. Single Responsibility per Stage

Each stage should have one clear domain. If you find yourself writing
"also check for X" in a stage prompt, X probably belongs in its own
stage.

> "A single agent's system prompt tends to bloat as task complexity
> grows, eventually devolving into unmaintainable 'Prompt Spaghetti.'"
> — [foojay.io](https://foojay.io/today/best-practices-for-working-with-ai-agents-subagents-skills-and-mcp/)

### 2. Coordination Topology Over Agent Count

Adding more agents doesn't improve results — proper coordination does.
The
[17x error trap](https://towardsdatascience.com/why-your-multi-agent-system-is-failing-escaping-the-17x-error-trap-of-the-bag-of-agents/)
shows that errors amplify exponentially in uncoordinated systems.
Effective coordination requires:

- **Non-overlapping scopes** — each stage owns distinct categories
- **Explicit ignore lists** — prevent duplicate work
- **Gates between stages** — contain errors before propagation
- **Shared knowledge base** — consistent reference material

### 3. Self-Contained Prompts

Each stage's system.md should be fully understandable in isolation.
Anthropic's research found that "short, generic instructions led
subagents to perform identical searches. Adding detailed task
descriptions solved this."

Practical implications:

- Duplicate common rules across stages rather than abstracting them
  into a separate file that breaks readability
- Include concrete code examples of vulnerable _and_ correct patterns
- Explicitly state what to ignore, not just what to look for

### 4. Budget Awareness

Agents must know their resource constraints and plan accordingly:

```markdown
# Budget Rules
- Phase 1+2 MUST complete in <=4 iterations
- Produce the report before spending 60% of your cost budget
- STOP after verification passes — no re-reading
```

Anthropic's research found that "token usage alone explains 80% of
performance variance in browsing tasks." Budget rules prevent runaway
execution while ensuring the agent produces output even when interrupted.

### 5. Proportionality

Not every finding warrants a fix:

```markdown
- Theoretical vulnerabilities in internal-only code are INFO, not fixes
- Ask: "Is this reachable from external input?"
- Skip fixes needing 50+ lines or new files — note in report
```

### 6. Trace Before Fix

For security agents especially, fixing the immediate site isn't enough:

```markdown
Before writing an Edit, trace how the fixed code is CONSUMED downstream.
If you sanitize input but the consumer re-parses it (e.g. shell-style
splitting), your fix may be ineffective.
```

---

## Anti-Patterns

### Bag of Agents

**Problem:** Throwing multiple agents at a task without defined
coordination.

**Symptom:** Agents produce conflicting fixes, duplicate findings, or
waste iterations on overlapping work.

**Fix:** Define non-overlapping scopes, explicit ignore lists, and
quality gates.

### Prompt Spaghetti

**Problem:** A single system.md that tries to cover every possible
scenario with increasingly complex conditional logic.

**Symptom:** The prompt exceeds 500 lines, contains nested conditionals,
and agents frequently misinterpret instructions.

**Fix:** Split into a composed agent with focused stages. Each stage's
system.md should be under 300 lines.

### Premature Abstraction

**Problem:** Creating shared templates and include files for content
that only appears in 1-2 agents.

**Symptom:** Understanding an agent requires reading 5+ files across
multiple directories. Changes require tracing include chains.

**Fix:** Duplicate content between 2 agents. Only create a template
when 3+ agents share identical content.

### Silent Scope Creep

**Problem:** An agent gradually accumulates categories beyond its
original purpose.

**Symptom:** A "Go review" agent also checks security, documentation,
test coverage, and CLI best practices.

**Fix:** Add a "CATEGORIES TO IGNORE" section. If you're adding a new
category, ask whether it warrants a new stage instead.

### Unbounded Execution

**Problem:** No iteration limits or wind-down protocol.

**Symptom:** Agent consumes entire token budget on discovery and
analysis, never producing a report.

**Fix:** Add explicit phase budgets ("Phase 1+2 in <=4 iterations"),
wind-down triggers ("report before 60% budget"), and hard stops ("STOP
after verification passes").

---

## Scaling Guidance

### When to Split a Leaf Agent into Stages

Split when any of these apply:

- The system.md exceeds 300 lines
- The agent covers 2+ independent domains (e.g., injection AND
  resource management)
- Runs frequently time out because the scope is too broad
- You need different models for different parts of the work

### When to Promote Stages to a Pipeline

Promote when:

- Individual stages are useful as standalone agents
- Other pipelines want to reuse one of the stages
- Stages need independent versioning

### Directory Threshold

| Stage count | Layout |
|-------------|--------|
| 1 (leaf) | Standard 4-file layout |
| 2 | Flat with stage-prefixed filenames |
| 3+ | `stages/` subdirectories |

### Adding a New Stage to a Composed Agent

1. Create the three prompt files (`<stage>-system.md`, `<stage>-agent.md`,
   `<stage>-task.md`)
2. Add the stage to `agent.yaml` under `stages:`
3. Add `references:` if the stage needs the shared knowledge base
4. Add appropriate gates after the new stage
5. Verify with `pre-commit run --all-files`

If this is the third stage, refactor to the `stages/` subdirectory layout.

---

## References

### Anthropic

- [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)
  — Orchestrator-worker pattern, prompt architecture, parallelization
  tiers
- [Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
  — Progressive disclosure, three-tier context loading, skill
  composition
- [Claude Code: Create custom subagents](https://code.claude.com/docs/en/sub-agents)
  — YAML frontmatter schema, tool restriction, model selection

### Microsoft

- [AI Agent Orchestration Patterns](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns)
  — Sequential, concurrent, group chat, handoff, and magentic patterns

### Industry Analysis

- [Why Your Multi-Agent System is Failing: The 17x Error Trap](https://towardsdatascience.com/why-your-multi-agent-system-is-failing-escaping-the-17x-error-trap-of-the-bag-of-agents/)
  — Error amplification in uncoordinated systems, functional planes
- [Multi-Agent Systems & AI Orchestration Guide 2026](https://www.codebridge.tech/articles/mastering-multi-agent-orchestration-coordination-is-the-new-scale-frontier)
  — Coordination as the scaling frontier
- [Best practices for building agentic systems](https://www.infoworld.com/article/4154570/best-practices-for-building-agentic-systems.html)
  — Plan-do-evaluate loop, model tiering

### Frameworks

- [CrewAI YAML Configuration](https://deepwiki.com/crewAIInc/crewAI/8.2-yaml-configuration)
  — Declarative agent/task definition, dynamic variables
- [AutoGen Agent Architecture](https://microsoft.github.io/autogen/stable//user-guide/core-user-guide/core-concepts/agent-and-multi-agent-application.html)
  — Layered design, async messaging, modular components
- [LangGraph Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api)
  — State graphs, nodes, edges, conditional routing
