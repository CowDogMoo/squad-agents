Scan all documentation and text files for LLM-generated content and
{{if eq .Mode "edit"}}rewrite flagged paragraphs to sound human-written{{end}}{{if eq .Mode "readonly"}}report flagged paragraphs with confidence scores{{end}}.

Start by using Glob with '**/*.md', '**/*.txt', '**/*.rst', '**/*.adoc'.
Batch Read calls: 4-6 files per iteration.

IMPORTANT CONSTRAINTS:

- Score each prose paragraph (2+ sentences) against 7 tell categories
- Only flag paragraphs with 3+ distinct tell categories
- Skip code blocks, frontmatter, CLI examples, config snippets
- Never touch CHANGELOG, LICENSE, NOTICE, .github/, .claude/ files
- README headers ("Installation," "Usage") are NOT tells -- only flag prose under them
{{if eq .Mode "edit"}}- Preserve all technical content (commands, paths, URLs, versions)
- Re-score every rewrite -- revise if still 3+ categories
- Every rewrite must say the same thing as the original{{end}}
- Batch ALL edits per file, then emit report immediately
- Every file scanned must appear in the output report
