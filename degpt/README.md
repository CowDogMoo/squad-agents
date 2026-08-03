# DeGPT

Detects LLM-generated prose in documentation and text files, then rewrites
flagged paragraphs to sound human-written (edit mode) or reports them with
confidence scores (readonly mode).

## How It Works

The agent scans `*.md`, `*.txt`, `*.rst`, and `*.adoc` files and scores
each prose paragraph against 7 tell categories derived from corpus analysis
of human vs LLM-generated text:

| # | Category | What It Catches |
|---|----------|-----------------|
| 1 | Vocabulary | "delve," "crucial," "leverage," "ecosystem," etc. |
| 2 | Structure | Rule of Three, "not X but Y," false ranges |
| 3 | Punctuation | Em dash overuse, Markdown in non-Markdown contexts |
| 4 | Tone | HR-speak, hedging padding, overemphasis |
| 5 | Transitions | "Moreover," "Furthermore," "Additionally" |
| 6 | Tech-doc | Correct-but-useless descriptions, missing "why" |
| 7 | Model openers | "Certainly!," "I'd be happy to," meta-introductions |

A paragraph must trigger **3+ distinct categories** to be flagged. This
prevents false positives from individual words that humans also use.

### Document-level pass

Per-paragraph scoring is blind to tells that contribute only one instance per
paragraph — a file can score clean at every paragraph and still read as LLM
output. So each file is also scored once as a whole, against four patterns:

| Pattern | What It Catches |
|---------|-----------------|
| Promotional register | Diffuse sales vocabulary: "big win," "high-value," CTA closers |
| Pitch-deck arc | Problem, opportunity, wins, validation, ask — and no stated limitations |
| Templated hinges | 3+ sibling sections opening with the same syntactic frame |
| Punctuation density | Em-dash rate and bolding measured across the document, not per paragraph |

These are reported separately with measured rates. They never count toward a
paragraph's 3-category cluster, so they cannot weaken the false-positive guard.
Zero flagged paragraphs plus one document-level finding is a normal result.

In edit mode, document-level findings are fixed under a **subtractive-only**
lane: delete a hype word, swap an em dash for the punctuation the sentence
already implies, unbold a number. No rewording — deletion cannot flatten good
prose the way a rewrite can.

### Genre baselines

Scoring adjusts to what the text is. Talk scripts are judged as spoken delivery
(fragments and "So," openers are correct; unbreathable sentences are worse).
Marketing copy suppresses the promotional signal. Academic and ESL prose needs
4+ categories.

## Usage

```bash
# Edit mode: rewrite flagged paragraphs in place
squad run --agent degpt

# Readonly mode: report only, no modifications
squad run --agent degpt --mode readonly

# Preview the assembled prompt
squad run --agent degpt --print-bundle --dry-run
```

## What Gets Skipped

- Code blocks, CLI examples, config snippets, frontmatter
- `CHANGELOG.md`, `LICENSE`, `NOTICE`, `.github/`, `.claude/`
- Non-English files (tell categories are English-specific)
- Standard README headers ("Installation," "Usage," "Contributing")
- Paragraphs with fewer than 3 tell categories
- Single-sentence paragraphs (not enough signal)

## Edit-Mode Rewrite Rules

- Preserve all technical content (commands, paths, URLs, versions)
- Preserve document structure (headings, bullets, links)
- Match the project's existing voice and tone
- After each rewrite, re-score against all 7 categories to confirm the
  output no longer reads like LLM text

## Agent Files

| File | Purpose |
|------|---------|
| `agent.yaml` | Manifest |
| `system.md` | Core prompt with hard rules, workflow, detection guide, examples |
| `agent.md` | Execution wrapper with phase descriptions |
| `task.md` | Default task instructions |

The tell catalog and scoring rubric live in the `detect-llm-tells`
skill (see [squad-skills](https://github.com/cowdogmoo/squad-skills)),
loaded on demand via `Skill("detect-llm-tells")`.

## Example

### Input (README.md excerpt)

```markdown
## Overview

This library provides a comprehensive and robust solution for managing
network connections. It leverages cutting-edge technology to deliver
a seamless experience. Moreover, the architecture is designed to be
both scalable and maintainable, ensuring that your application can
grow with your needs. Additionally, the extensive documentation
makes it straightforward to get started.
```

### Edit-Mode Output

The paragraph is rewritten in place:

```markdown
## Overview

This library manages network connections with support for automatic
reconnection and connection pooling. See the quickstart guide below
for setup instructions.
```

### Readonly-Mode Output

```markdown
## Analysis Summary
**Files analyzed:** 3
**Paragraphs flagged:** 1
**Paragraphs clean:** 42

## Findings

### LLM-Generated Paragraph in README.md
**Confidence:** HIGH (5/7 categories triggered)
**File:** README.md:5-10
**Categories triggered:**
- Vocabulary: "comprehensive," "robust," "leverages," "cutting-edge," "seamless"
- Structure: false range ("scalable and maintainable")
- Tone: overemphasis ("both scalable and maintainable, ensuring")
- Transitions: "Moreover," "Additionally"
- Tech-doc: correct-but-useless ("designed to be scalable"), missing "why"

**Suggested rewrite:** Describe what the library concretely does and how to
get started, rather than making abstract claims about its qualities.
```

## Related

- [Agent Quality Rubric](../docs/agent-quality.md)
- [Creating Agents](../docs/creating-agents.md)
