#!/usr/bin/env python3
"""Shared post-processing filter for the text-transform agents' output.

Reads LLM output from stdin, cleans it up, and writes to stdout.

Usage:
    # Generic cleanup (strip fences, collapse blanks, remove preamble)
    echo "$output" | python3 scripts/filter.py

    # Section-based cleanup (merge duplicate sections, drop empty ones)
    echo "$output" | python3 scripts/filter.py --sections "Added,Changed,Removed"
    echo "$output" | python3 scripts/filter.py --sections "Key Changes,Added,Changed,Removed"

    # Max consecutive blank lines (default: 1)
    echo "$output" | python3 scripts/filter.py --max-blanks 2
"""

import argparse
import re
import sys
from collections.abc import Iterable


def looks_like_api_error(text: str) -> bool:
    """Report whether the input is a fabric/LLM API error, not model output.

    When the upstream API rejects a request, fabric prints the error to
    stdout, e.g.:

        POST "https://api.anthropic.com/v1/messages": 400 Bad Request
        (Request-ID: ...) {"type":"error","error":{...}}

    Passing that through produces a garbage commit message or PR body, so
    the filter must abort instead. Only the first non-blank line is
    checked — real output that merely discusses an API error elsewhere in
    the body is untouched.
    """
    first = next((ln for ln in text.split("\n") if ln.strip()), "")
    return bool(
        re.search(r'\b(GET|POST|PUT|PATCH|DELETE) "https?://\S+": \d{3} ', first)
        or re.search(r'"type"\s*:\s*"error"', first)
    )


def strip_wrapping_fences(text: str) -> str:
    """Remove code fences that wrap the entire output, preserving internal ones.

    Loops to handle models that double-wrap (emit two opening/closing fences)
    and tolerates blank lines between the fence and the content.
    """
    while True:
        lines = text.split("\n")
        # Find first and last non-blank lines
        first_idx = next((i for i, ln in enumerate(lines) if ln.strip()), None)
        last_idx = next(
            (len(lines) - 1 - i for i, ln in enumerate(reversed(lines)) if ln.strip()),
            None,
        )
        if first_idx is None or last_idx is None or first_idx >= last_idx:
            return text
        if re.match(r"^```\w*$", lines[first_idx].strip()) and lines[last_idx].strip() == "```":
            del lines[last_idx]
            del lines[first_idx]
            text = "\n".join(lines)
            continue
        return text


def strip_leading_trailing_blanks(text: str) -> str:
    """Remove leading and trailing blank lines."""
    lines = text.split("\n")
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines)


def remove_preamble(text: str) -> str:
    """Remove introductory 'Here is...' / 'Below is...' lines."""
    text = re.sub(
        r"^(Here is|Here's|Below is) (the|an?) .*:?\s*$",
        "",
        text,
        flags=re.MULTILINE,
    )
    return strip_leading_announcement(text)


def strip_leading_announcement(text: str) -> str:
    """Drop a leading narrative line that announces the real output.

    Models often prefix output with a sentence whose announcing clause is not
    at the start of the line, e.g. "Based on the git diff, this adds a single
    new file `x`. Here is the commit message:". The anchored pattern in
    remove_preamble only matches when the line *begins* with the clause, so
    such a line survives and merge_sections then promotes it to the title.

    Only the first non-blank line is considered, so body content that happens
    to end in a colon is never touched.
    """
    lines = text.split("\n")
    idx = next((i for i, ln in enumerate(lines) if ln.strip()), None)
    if idx is None:
        return text
    announce = re.compile(
        r"\b(here is|here's|below is|the following is)\b[^.]*:\s*$",
        re.IGNORECASE,
    )
    if announce.search(lines[idx]):
        del lines[idx]
    return "\n".join(lines)


def remove_placeholder_lines(text: str) -> str:
    """Remove lines with placeholder text.

    Handles:
    - 'No content', 'Nothing added', etc. (commit/pr patterns)
    - '[No CRITICAL findings]', '[None found]', '[No issues found]' (audit patterns)
    - '- None', '- No issues found' (list-style placeholders)
    """
    patterns = [
        # "No content", "Nothing was removed", etc.
        r"^\s*(No |Nothing )(content|features|code|changes|added|was added|"
        r"changed|was changed|removed|was removed).*$",
        # "No existing files were modified", "No files or functionality were removed", etc.
        r"^\s*-?\s*No [\w ]+ (?:was|were) "
        r"(?:modified|removed|changed|added|updated|deleted|introduced)\b.*$",
        # "[No CRITICAL findings]", "[None found]", "[No issues found]"
        r"^\s*\[No \w+ (issues|findings)\]\s*$",
        r"^\s*\[(None found|No issues found)\]\s*$",
        # "- None", "- No issues found"
        r"^\s*- (None|No issues found)\s*$",
    ]
    for pattern in patterns:
        text = re.sub(pattern, "", text, flags=re.MULTILINE | re.IGNORECASE)
    return "\n".join("" if is_angle_placeholder(ln) else ln for ln in text.split("\n"))


def is_angle_placeholder(line: str) -> bool:
    """Report whether a line is only angle-bracket placeholders and punctuation.

    Catches echoed template lines like "- <most important change>" and
    "- <what was added> - <file ref>", where nothing outside the brackets
    carries meaning. A line that says something of its own — e.g.
    "- <details> blocks are now escaped" — keeps word characters after the
    brackets are removed, so it survives.
    """
    if "<" not in line:
        return False
    return not re.search(r"\w", re.sub(r"<[^>]*>", "", line))


ATTRIBUTION_LINE_RES = [
    # "🤖 Generated with [Claude Code](https://claude.com/claude-code)" and the
    # plain-text variant. Anchored so a bullet that *talks about* the footer
    # ("- Strip the Generated with Claude Code footer") is left alone.
    re.compile(
        r"^\s*(?:🤖\s*)?Generated with (?:\[Claude Code\]\([^)]*\)|Claude Code)"
        r"[\s.!]*$",
        re.IGNORECASE,
    ),
    # Co-Authored-By trailers for AI assistants, in either capitalisation.
    re.compile(
        r"^\s*Co-Authored-By:\s*(?:Claude|Antigravity|Gemini)\b.*$",
        re.IGNORECASE,
    ),
    # Any trailer pointing at the assistants' no-reply mailboxes.
    re.compile(r"^\s*[\w-]+:\s*.*<[^>]*@(?:anthropic\.com|google\.com)>\s*$"),
    # Session-link trailers and bare session URLs.
    re.compile(r"^\s*Claude-Session:\s*https?://\S+\s*$", re.IGNORECASE),
    re.compile(r"^\s*https?://claude\.ai/code/session_\S+\s*$"),
]


def strip_attribution_lines(text: str) -> str:
    """Drop AI-assistant attribution footers and trailers.

    Claude Code tells the model it drives to end pull request descriptions with
    "🤖 Generated with [Claude Code](...)" and commit messages with a
    `Co-Authored-By: Claude ...` trailer. When a pattern runs through that CLI
    the model appends the line to its answer, and `squad_pr` then ships it
    straight into the PR body. The forbidden-content hooks only inspect the
    literal command string, so the footer sails past them.

    Every pattern is anchored to a whole line, so prose that merely mentions
    the footer survives.
    """
    return "\n".join(
        "" if any(rx.match(ln) for rx in ATTRIBUTION_LINE_RES) else ln for ln in text.split("\n")
    )


def truncate_pattern_boilerplate(text: str) -> str:
    """Drop echoed instructional sections from the agent's own prompt.

    Some models regurgitate the prompt's own scaffolding (HARD RULES, OUTPUT FORMAT,
    TITLE OUTPUT, EXAMPLE OUTPUT, and so on). These ALL-CAPS instructional
    headers never belong in real output, so cut everything from the first
    one onward.

    The match is case-sensitive on purpose: "## Steps to reproduce" is
    ordinary prose in a PR body, while "## STEPS" is pattern scaffolding.
    A marker before any real content is left alone — echoed boilerplate is a
    better outcome than an empty commit message.
    """
    marker = re.compile(
        r"^#{1,6}\s+(IDENTITY|STEPS|WORKFLOW|HARD RULES|CONVENTIONAL COMMITS|OUTPUT INSTRUCTIONS|"
        r"OUTPUT FORMAT|TITLE OUTPUT|EXAMPLE OUTPUT|INPUT)\b"
    )
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if marker.match(line):
            if not any(ln.strip() for ln in lines[:i]):
                return text
            return "\n".join(lines[:i])
    return text


def collapse_blank_lines(text: str, max_consecutive: int = 1) -> str:
    """Collapse runs of blank lines to at most max_consecutive."""
    lines = text.split("\n")
    result = []
    blank_count = 0
    for line in lines:
        if not line.strip():
            blank_count += 1
            if blank_count <= max_consecutive:
                result.append(line)
        else:
            blank_count = 0
            result.append(line)
    return "\n".join(result)


def ensure_blank_after_title(text: str, blank_after_title: bool = True) -> str:
    """Normalize spacing between the first line and the body.

    Args:
        blank_after_title: If True, insert one blank line after the title (for
            git commit messages). If False, place the body immediately after
            the title with no blank line (for PR descriptions).
    """
    lines = text.split("\n")
    if len(lines) < 2:
        return text
    title = lines[0]
    rest = lines[1:]
    # Strip leading blanks from rest
    while rest and not rest[0].strip():
        rest.pop(0)
    if rest:
        sep = "\n\n" if blank_after_title else "\n"
        return title + sep + "\n".join(rest)
    return title


BOLD_SECTION_RE = re.compile(r"^\*\*[^*]+:\*\*\s*$")


def drop_empty_bold_sections(text: str) -> str:
    """Drop "**Name:**" sub-section headers that ended up with no content.

    remove_placeholder_lines() deletes the "No content was removed" line but
    leaves the header that introduced it. merge_sections() hides that, because
    it re-emits only sections that have content; the heading path does not, so
    an empty header survives into the body as a dangling label.
    """
    lines = text.split("\n")
    keep = [True] * len(lines)
    for i, line in enumerate(lines):
        if not BOLD_SECTION_RE.match(line):
            continue
        nxt = i + 1
        while nxt < len(lines) and not lines[nxt].strip():
            nxt += 1
        if nxt >= len(lines) or BOLD_SECTION_RE.match(lines[nxt]) or lines[nxt].startswith("#"):
            keep[i] = False
    return "\n".join(line for line, kept in zip(lines, keep, strict=True) if kept)


def normalize_heading(heading: str) -> str:
    """Reduce a heading to a form that compares stably across minor edits."""
    return re.sub(r"\s+", " ", heading.strip().lstrip("#").strip()).casefold()


def drop_empty_heading_sections(text: str, keep_headings: Iterable[str] = ()) -> str:
    """Remove markdown heading sections that have no content.

    A section is empty if it contains only blank lines or separators (---)
    before the next heading of equal or higher level, or end of text.

    Headings in keep_headings survive even when empty. A PR template check
    greps the body for its required headings, so dropping one as "empty"
    turns a thin section into a failed build rather than a tidier body.
    """
    kept = {normalize_heading(h) for h in keep_headings}
    lines = text.split("\n")
    # Parse into (heading_level, heading_line, content_lines) groups
    sections: list[tuple[int, str, list[str]]] = []
    current_heading = ""
    current_level = 0
    current_content: list[str] = []

    for line in lines:
        heading_match = re.match(r"^(#{1,6})\s+", line)
        if heading_match:
            sections.append((current_level, current_heading, current_content))
            current_level = len(heading_match.group(1))
            current_heading = line
            current_content = []
        else:
            current_content.append(line)
    sections.append((current_level, current_heading, current_content))

    # Rebuild, skipping sections with no substantive content
    result_lines: list[str] = []
    for level, heading, content in sections:
        substantive = any(line.strip() and line.strip() != "---" for line in content)
        if level == 0:
            # Pre-heading content, always keep
            result_lines.extend(content)
        elif substantive or normalize_heading(heading) in kept:
            result_lines.append(heading)
            result_lines.extend(content)

    return "\n".join(result_lines)


def normalize_section_spacing(text: str) -> str:
    """Ensure one blank line before markdown headers and HR separators."""
    lines = text.split("\n")
    result = []
    for i, line in enumerate(lines):
        is_header = line.startswith("#")
        is_separator = line.strip() == "---"
        # Skip duplicate separators
        if is_separator and result:
            prev_non_blank = next((ln for ln in reversed(result) if ln.strip()), None)
            if prev_non_blank == "---":
                continue
        if i > 0 and (is_header or is_separator):
            # Add blank line before if previous line isn't already blank
            if result and result[-1].strip():
                result.append("")
        result.append(line)
    return "\n".join(result)


def strip_trailing_whitespace(text: str) -> str:
    """Remove trailing whitespace from each line."""
    return "\n".join(line.rstrip() for line in text.split("\n"))


def merge_sections(text: str, section_names: list[str]) -> str:
    """Parse bold section headers, merge duplicates, drop empty sections.

    Handles sections like **Added:**, **Changed:**, **Removed:**, **Key Changes:**

    Content on the same line as a header (**Added:** a new module) is kept as
    that section's first line rather than dropped with the header.
    """
    lines = text.split("\n")

    # Build header patterns
    header_pattern = re.compile(
        r"^\*\*(" + "|".join(re.escape(s) for s in section_names) + r"):\*\*(.*)$"
    )

    title = ""
    sections: dict[str, list[str]] = {name: [] for name in section_names}
    other_lines: list[str] = []
    current_section: str | None = None
    title_found = False

    for line in lines:
        # First non-empty line is the title
        if not title_found:
            if line.strip():
                title = line
                title_found = True
            continue

        # Check for section header
        match = header_pattern.match(line)
        if match:
            current_section = match.group(1)
            inline = match.group(2).strip()
            if inline:
                sections[current_section].append(inline)
            continue

        # Accumulate into the right bucket
        if current_section:
            sections[current_section].append(line)
        else:
            other_lines.append(line)

    # Build output
    parts = [title]

    # Non-section content (between title and first section)
    other_text = "\n".join(other_lines).strip()
    if other_text:
        parts.append("")
        parts.append(other_text)

    # Sections with content
    for name in section_names:
        content = "\n".join(sections[name]).strip()
        if content:
            parts.append("")
            parts.append(f"**{name}:**")
            parts.append("")
            parts.append(content)

    return "\n".join(parts)


def filter_text(
    text: str,
    section_names: list[str] | None = None,
    max_blanks: int = 1,
    blank_after_title: bool = True,
    required_headings: list[str] | None = None,
) -> str:
    """Apply all filter steps to the input text."""
    text = strip_wrapping_fences(text)
    text = strip_leading_trailing_blanks(text)
    text = truncate_pattern_boilerplate(text)
    text = remove_preamble(text)
    text = strip_attribution_lines(text)
    text = remove_placeholder_lines(text)

    if required_headings:
        # Section merging reorders every named section to the end of the body, which
        # would pull bullets out from under the template headings they belong to, so
        # required headings and section merging are mutually exclusive.
        text = drop_empty_bold_sections(text)
        text = drop_empty_heading_sections(text, keep_headings=required_headings)
        text = normalize_section_spacing(text)
    elif section_names:
        text = merge_sections(text, section_names)
        text = ensure_blank_after_title(text, blank_after_title=blank_after_title)
    else:
        text = drop_empty_heading_sections(text)
        text = normalize_section_spacing(text)

    text = collapse_blank_lines(text, max_blanks)
    text = strip_leading_trailing_blanks(text)
    text = strip_trailing_whitespace(text)
    return text


def main():
    parser = argparse.ArgumentParser(description="Post-process fabric pattern output")
    parser.add_argument(
        "--sections",
        help="Comma-separated bold section names to merge/filter (e.g. 'Added,Changed,Removed')",
    )
    parser.add_argument(
        "--max-blanks",
        type=int,
        default=1,
        help="Maximum consecutive blank lines (default: 1)",
    )
    parser.add_argument(
        "--required-heading",
        action="append",
        dest="required_headings",
        metavar="HEADING",
        help="Markdown heading the body must keep even when empty; repeatable. "
        "Suppresses --sections merging, which would reorder content out from "
        "under these headings.",
    )
    parser.add_argument(
        "--no-blank-after-title",
        action="store_true",
        help="Do not insert a blank line between title and body (useful for PR descriptions)",
    )
    args = parser.parse_args()

    section_names = None
    if args.sections:
        section_names = [s.strip() for s in args.sections.split(",")]

    text = sys.stdin.read()
    if looks_like_api_error(text):
        print(f"filter.py: input is an API error, not model output:\n{text}", file=sys.stderr)
        sys.exit(1)
    result = filter_text(
        text,
        section_names=section_names,
        max_blanks=args.max_blanks,
        blank_after_title=not args.no_blank_after_title,
        required_headings=args.required_headings,
    )
    print(result)


if __name__ == "__main__":
    main()
