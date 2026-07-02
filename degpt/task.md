Scan all documentation and text files for LLM-generated content and
rewrite flagged paragraphs to sound human-written (edit mode, the
default) or report flagged paragraphs with confidence scores (readonly
mode — caller said "readonly" / "report only").

Start by using Glob with '**/*.md', '**/*.txt', '**/*.rst', '**/*.adoc'
ALL FOUR in parallel in iteration 1. Empty results for `.txt`/`.rst`/`.adoc`
are normal and FINAL -- do NOT re-Glob in iter 2+ to verify. The union of
those four Glob results is the COMPLETE, FROZEN file set. Do not infer or
guess additional paths -- if Glob did not return it, it does not exist.
Batch Read calls: 4-6 files per iteration. Read each file exactly once.

When the last globbed file has been Read, Phase 2 is over. On the next
iteration: if 0 paragraphs cross threshold, emit the no-findings report
immediately -- do NOT Bash/Grep/Read to fish for tells you missed. 0
findings is a correct outcome on clean codebases. Reports must include
the literal markers "Files touched: none" and "No changes" verbatim.

IMPORTANT CONSTRAINTS:

- Score each prose paragraph (2+ sentences) against 7 tell categories
- Only flag paragraphs with 3+ distinct tell categories
- Skip code blocks, frontmatter, CLI examples, config snippets
- Never touch CHANGELOG, LICENSE, NOTICE, .github/, .claude/ files
- README headers ("Installation," "Usage") are NOT tells -- only flag prose under them
- Edit mode: preserve all technical content (commands, paths, URLs, versions)
- Edit mode: re-score every rewrite -- revise if still 3+ categories
- Edit mode: every rewrite must say the same thing as the original
- Batch ALL edits per file, then emit report immediately
- Every file scanned must appear in the output report
