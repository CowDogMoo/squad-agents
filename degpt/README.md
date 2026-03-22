# LLM-Junk

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

## Usage

```bash
# Edit mode: rewrite flagged paragraphs in place
squad run --agent llm-junk

# Readonly mode: report only, no modifications
squad run --agent llm-junk --mode readonly

# Preview the assembled prompt
squad run --agent llm-junk --print-bundle --dry-run
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
| `references/llm-tells.md` | Full tell catalog with tiered word lists and thresholds |

## Related

- [Agent Quality Rubric](../docs/agent-quality.md)
- [Creating Agents](../docs/creating-agents.md)
