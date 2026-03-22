Scan all documentation and text files in this codebase for LLM-generated content
and {{if eq .Mode "edit"}}rewrite flagged paragraphs to sound human-written{{end}}{{if eq .Mode "readonly"}}report flagged paragraphs with confidence scores{{end}}.

Start by using Glob with '**/*.md', '**/*.txt', '**/*.rst', '**/*.adoc' to
discover all text files. Batch Read calls: read 4-6 files per iteration.

DETECTION RULES:

- Score each prose PARAGRAPH (2+ sentences) independently against 7 tell
  categories (vocabulary, structure, punctuation, tone, transitions, tech-doc
  tells, model openers)
- Only flag paragraphs with 3+ distinct tell categories
- Skip code blocks, frontmatter, CLI examples, config snippets
- Never touch CHANGELOG, LICENSE, NOTICE, .github/, or .claude/ files
- Standard README headers ("Installation," "Usage," "Contributing") are NOT
  tells — only flag the prose content under them
- Skip files written in non-English languages (tell categories are English-specific)

{{if eq .Mode "edit"}}
REWRITE RULES:

- Preserve all technical content (commands, paths, URLs, version numbers)
- Preserve document structure (headings, bullets, links)
- Replace LLM vocabulary with concrete, specific words
- Cut filler transitions and hedging padding
- Vary sentence length — break the robotic cadence
- Match the project's existing voice and tone
- Every rewrite must say the same thing as the original
- If you cannot rewrite without risking accuracy, skip it
- After each rewrite, RE-SCORE the new text against all 7 categories — if it
  still triggers 3+, revise again. Your rewrites must not read like LLM output.
{{end}}

ABSOLUTE PROHIBITIONS:

- Do NOT flag paragraphs with fewer than 3 tell categories
- Do NOT flag files solely for having standard README section headers
- Do NOT modify code blocks or technical content
- Do NOT change the meaning of any rewritten paragraph
- Do NOT touch exempt files (changelogs, licenses, .github/, .claude/)
- Do NOT scan or modify non-English files
- Do NOT re-read files after editing — trust Edit output
- Do NOT make additional tool calls after emitting the report

{{include "hard-rules/efficiency.md"}}

Phase allocation:

- Phase 1 (1 iter): Glob all text file patterns in parallel, COUNT files
  (reference is already in your system prompt — do NOT Read it)
- Phase 2 (varies): Read files with 4-6 parallel Reads per iteration
- Phase 3 (2-4 iter): ALL Edit calls batched per file, re-score each rewrite
- Phase 4 (1 iter): Emit report in SAME response as last edit, NO more iterations

AGENT-SPECIFIC REQUIREMENTS:

- Every file scanned must appear in the output report
- Every rewrite must pass re-score validation (<3 tell categories)
