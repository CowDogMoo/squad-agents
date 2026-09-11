"""Tests for scripts/filter.py — the shared text-transform output filter."""

import sys
from pathlib import Path
from typing import ClassVar

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from filter import (
    collapse_blank_lines,
    drop_empty_bold_sections,
    drop_empty_heading_sections,
    ensure_blank_after_title,
    filter_text,
    looks_like_api_error,
    merge_sections,
    normalize_heading,
    normalize_section_spacing,
    remove_placeholder_lines,
    remove_preamble,
    strip_attribution_lines,
    strip_leading_trailing_blanks,
    strip_trailing_whitespace,
    strip_wrapping_fences,
    truncate_pattern_boilerplate,
)


class TestStripWrappingFences:
    def test_removes_markdown_fence(self):
        text = "```markdown\n# Hello\nWorld\n```"
        assert strip_wrapping_fences(text) == "# Hello\nWorld"

    def test_removes_python_fence(self):
        text = "```python\nprint('hi')\n```"
        assert strip_wrapping_fences(text) == "print('hi')"

    def test_removes_bare_fence(self):
        text = "```\nsome content\n```"
        assert strip_wrapping_fences(text) == "some content"

    def test_preserves_internal_fences(self):
        text = "# Review\n\n```go\nfunc main() {}\n```\n\nDone."
        assert strip_wrapping_fences(text) == text

    def test_no_fences(self):
        text = "just plain text\nno fences here"
        assert strip_wrapping_fences(text) == text

    def test_only_opening_fence(self):
        text = "```go\nfunc main() {}\nno closing fence"
        assert strip_wrapping_fences(text) == text

    def test_empty_input(self):
        assert strip_wrapping_fences("") == ""

    def test_removes_doubled_fences(self):
        """Models sometimes double-wrap output; strip both layers."""
        text = "```\n```\nfeat: thing\n```\n```"
        assert strip_wrapping_fences(text) == "feat: thing"

    def test_removes_fence_with_blank_padding(self):
        """Tolerate blank lines between the wrapping fences and content."""
        text = "```\n\nfeat: thing\n\n```"
        assert strip_wrapping_fences(text) == "\nfeat: thing\n"

    def test_doubled_fences_with_language_tag(self):
        text = "```markdown\n```\ncontent\n```\n```"
        assert strip_wrapping_fences(text) == "content"


class TestStripLeadingTrailingBlanks:
    def test_strips_leading(self):
        assert strip_leading_trailing_blanks("\n\nhello") == "hello"

    def test_strips_trailing(self):
        assert strip_leading_trailing_blanks("hello\n\n") == "hello"

    def test_strips_both(self):
        assert strip_leading_trailing_blanks("\n\nhello\n\n") == "hello"

    def test_preserves_internal(self):
        text = "hello\n\nworld"
        assert strip_leading_trailing_blanks(text) == text

    def test_empty_input(self):
        assert strip_leading_trailing_blanks("") == ""


class TestRemovePreamble:
    def test_removes_here_is(self):
        text = "Here is the review:\n# Review\nContent"
        result = remove_preamble(text)
        assert "Here is" not in result
        assert "# Review" in result

    def test_removes_heres(self):
        text = "Here's an analysis:\n# Analysis"
        result = remove_preamble(text)
        assert "Here's" not in result

    def test_removes_below_is(self):
        text = "Below is the output:\nContent"
        result = remove_preamble(text)
        assert "Below is" not in result

    def test_preserves_non_preamble(self):
        text = "Here is where things get interesting in the code."
        # This should NOT be removed — doesn't match "Here is the/an/a ..."
        result = remove_preamble(text)
        assert result == text

    def test_no_preamble(self):
        text = "# Review\nLooks good."
        assert remove_preamble(text) == text


class TestRemovePlaceholderLines:
    def test_no_content(self):
        result = remove_placeholder_lines("No content")
        assert result.strip() == ""

    def test_nothing_added(self):
        result = remove_placeholder_lines("Nothing was added")
        assert result.strip() == ""

    def test_no_changes(self):
        result = remove_placeholder_lines("No changes")
        assert result.strip() == ""

    def test_bracket_findings(self):
        result = remove_placeholder_lines("[No CRITICAL findings]")
        assert result.strip() == ""

    def test_bracket_issues(self):
        result = remove_placeholder_lines("[No HIGH issues]")
        assert result.strip() == ""

    def test_none_found(self):
        result = remove_placeholder_lines("[None found]")
        assert result.strip() == ""

    def test_no_issues_found(self):
        result = remove_placeholder_lines("[No issues found]")
        assert result.strip() == ""

    def test_dash_none(self):
        result = remove_placeholder_lines("- None")
        assert result.strip() == ""

    def test_dash_no_issues(self):
        result = remove_placeholder_lines("- No issues found")
        assert result.strip() == ""

    def test_no_files_were_modified(self):
        result = remove_placeholder_lines(
            "- No existing files were modified; all additions introduce new functionality"
        )
        assert result.strip() == ""

    def test_no_files_were_removed(self):
        result = remove_placeholder_lines("- No files or functionality were removed in this update")
        assert result.strip() == ""

    def test_no_code_was_changed(self):
        result = remove_placeholder_lines("No existing code was modified")
        assert result.strip() == ""

    def test_preserves_real_content(self):
        text = "- SQL injection in handler.go"
        assert remove_placeholder_lines(text) == text

    def test_mixed_content(self):
        text = "- Real issue\n- None\n- Another issue"
        result = remove_placeholder_lines(text)
        assert "Real issue" in result
        assert "Another issue" in result
        lines = [line for line in result.split("\n") if line.strip()]
        assert len(lines) == 2

    def test_angle_bracket_placeholder(self):
        result = remove_placeholder_lines("- <most important change>")
        assert result.strip() == ""

    def test_multiple_angle_brackets_on_one_line(self):
        result = remove_placeholder_lines("- <what was added> - <file ref>")
        assert result.strip() == ""

    def test_bare_angle_placeholder(self):
        result = remove_placeholder_lines("<title>")
        assert result.strip() == ""

    def test_preserves_prose_containing_angle_brackets(self):
        text = "- <details> blocks are now escaped in generated output"
        assert remove_placeholder_lines(text) == text

    def test_preserves_generic_type_in_prose(self):
        text = "- Added Vec<String> handling to the parser"
        assert remove_placeholder_lines(text) == text


class TestTruncatePatternBoilerplate:
    def test_truncates_at_output_instructions(self):
        text = "feat: add thing\n\nReal body.\n\n# OUTPUT INSTRUCTIONS\n\n- Do the thing"
        result = truncate_pattern_boilerplate(text)
        assert "Real body." in result
        assert "OUTPUT INSTRUCTIONS" not in result
        assert "Do the thing" not in result

    def test_truncates_at_example_output(self):
        text = "fix: bug\n\nBody.\n\n## EXAMPLE OUTPUT\n\nfeat: sample"
        result = truncate_pattern_boilerplate(text)
        assert "EXAMPLE OUTPUT" not in result

    def test_preserves_lowercase_headings(self):
        """'## Steps to reproduce' is prose, not pattern scaffolding."""
        text = "feat: add thing\n\n## Steps to reproduce\n\n1. Run task test\n2. Observe"
        assert truncate_pattern_boilerplate(text) == text

    def test_preserves_title_cased_input_heading(self):
        text = "fix: parser\n\n## Input\n\nThe parser now accepts YAML."
        assert truncate_pattern_boilerplate(text) == text

    def test_keeps_boilerplate_when_no_content_precedes_it(self):
        """Truncating to nothing would be worse than leaving the boilerplate."""
        text = "# IDENTITY\n\nYou are a helpful assistant."
        assert truncate_pattern_boilerplate(text) == text

    def test_no_marker(self):
        text = "feat: thing\n\n- One\n- Two"
        assert truncate_pattern_boilerplate(text) == text


class TestTruncateAgentScaffolding:
    """The agent prompts use HARD RULES / WORKFLOW headings; echoing them is boilerplate too."""

    def test_truncates_at_echoed_hard_rules(self):
        text = "feat: x\n\n- did it\n\n# HARD RULES\n\n1. Output only the message"
        assert truncate_pattern_boilerplate(text) == "feat: x\n\n- did it\n"

    def test_truncates_at_echoed_workflow(self):
        text = "feat: x\n\n## WORKFLOW\n1. Analyze"
        assert truncate_pattern_boilerplate(text) == "feat: x\n"

    def test_prose_heading_survives(self):
        text = "feat: x\n\n## Workflow changes\n\n- reordered the steps"
        assert truncate_pattern_boilerplate(text) == text


class TestCollapsBlankLines:
    def test_collapses_to_one(self):
        text = "a\n\n\n\nb"
        assert collapse_blank_lines(text, 1) == "a\n\nb"

    def test_collapses_to_two(self):
        text = "a\n\n\n\nb"
        assert collapse_blank_lines(text, 2) == "a\n\n\nb"

    def test_already_clean(self):
        text = "a\n\nb"
        assert collapse_blank_lines(text, 1) == text

    def test_no_blanks(self):
        text = "a\nb\nc"
        assert collapse_blank_lines(text, 1) == text


class TestEnsureBlankAfterTitle:
    def test_adds_blank_line(self):
        text = "title\nbody"
        assert ensure_blank_after_title(text) == "title\n\nbody"

    def test_collapses_multiple_blanks(self):
        text = "title\n\n\n\nbody"
        assert ensure_blank_after_title(text) == "title\n\nbody"

    def test_already_correct(self):
        text = "title\n\nbody"
        assert ensure_blank_after_title(text) == text

    def test_title_only(self):
        assert ensure_blank_after_title("just a title") == "just a title"


class TestDropEmptyHeadingSections:
    def test_drops_empty_section(self):
        text = "## CRITICAL\n\n## HIGH\n\n- Found an issue"
        result = drop_empty_heading_sections(text)
        assert "CRITICAL" not in result
        assert "HIGH" in result
        assert "Found an issue" in result

    def test_drops_section_with_only_separator(self):
        text = "## CRITICAL\n\n---\n\n## HIGH\n\n- Issue here"
        result = drop_empty_heading_sections(text)
        assert "CRITICAL" not in result
        assert "HIGH" in result

    def test_keeps_section_with_content(self):
        text = "## Summary\n\nTwo issues found."
        result = drop_empty_heading_sections(text)
        assert "Summary" in result
        assert "Two issues found" in result

    def test_preserves_pre_heading_content(self):
        text = "Intro text\n\n## Section\n\nContent"
        result = drop_empty_heading_sections(text)
        assert "Intro text" in result

    def test_multiple_empty_sections(self):
        text = "## A\n\n## B\n\n## C\n\nReal content"
        result = drop_empty_heading_sections(text)
        assert "A" not in result
        assert "B" not in result
        assert "C" in result
        assert "Real content" in result


class TestNormalizeSectionSpacing:
    def test_adds_blank_before_header(self):
        text = "content\n# Header"
        result = normalize_section_spacing(text)
        assert result == "content\n\n# Header"

    def test_adds_blank_before_separator(self):
        text = "content\n---"
        result = normalize_section_spacing(text)
        assert result == "content\n\n---"

    def test_no_double_blank(self):
        text = "content\n\n# Header"
        result = normalize_section_spacing(text)
        assert result == text

    def test_deduplicates_separators(self):
        text = "---\n---"
        result = normalize_section_spacing(text)
        assert result == "---"


class TestStripTrailingWhitespace:
    def test_strips_spaces(self):
        assert strip_trailing_whitespace("hello   ") == "hello"

    def test_strips_tabs(self):
        assert strip_trailing_whitespace("hello\t") == "hello"

    def test_multiline(self):
        text = "a  \nb \nc   "
        assert strip_trailing_whitespace(text) == "a\nb\nc"


class TestMergeSections:
    def test_merges_duplicate_added(self):
        text = "feat: add auth\n\n**Added:**\n- Login\n\n**Added:**\n- Signup"
        result = merge_sections(text, ["Added", "Changed", "Removed"])
        assert result.count("**Added:**") == 1
        assert "Login" in result
        assert "Signup" in result

    def test_drops_empty_sections(self):
        text = "fix: bug\n\n**Added:**\n\n**Changed:**\n- Fixed mutex\n\n**Removed:**\n"
        result = merge_sections(text, ["Added", "Changed", "Removed"])
        assert "**Added:**" not in result
        assert "**Removed:**" not in result
        assert "**Changed:**" in result
        assert "Fixed mutex" in result

    def test_preserves_section_order(self):
        text = "feat: update\n\n**Removed:**\n- Old code\n\n**Added:**\n- New code"
        result = merge_sections(text, ["Added", "Changed", "Removed"])
        added_pos = result.index("**Added:**")
        removed_pos = result.index("**Removed:**")
        assert added_pos < removed_pos

    def test_preserves_other_content(self):
        text = "feat: thing\n\nSome description here.\n\n**Added:**\n- Stuff"
        result = merge_sections(text, ["Added", "Changed", "Removed"])
        assert "Some description here." in result

    def test_key_changes_section(self):
        text = "feat: api\n\n**Key Changes:**\n- New endpoints\n\n**Added:**\n- GET /users"
        result = merge_sections(text, ["Key Changes", "Added", "Changed", "Removed"])
        assert "**Key Changes:**" in result
        assert "**Added:**" in result

    def test_keeps_content_on_the_header_line(self):
        text = "feat: add auth\n\n**Added:** login handler in auth.go\n**Changed:** tweaked mutex"
        result = merge_sections(text, ["Added", "Changed", "Removed"])
        assert "login handler in auth.go" in result
        assert "tweaked mutex" in result

    def test_drops_false_start_title_and_self_correction(self):
        # Observed failure: the model emits a wrong (even conventional-commit
        # formatted) title, corrects itself in prose, then writes the real
        # output. The last conventional-commit line before the sections wins.
        text = (
            "**feat: add unrelated hallucinated capability**\n\n"
            "Wait — that's not right. Let me actually do the job I was given.\n\n"
            "refactor: use the real title\n\n"
            "**Added:**\n- Real content"
        )
        result = merge_sections(text, ["Added", "Changed", "Removed"])
        assert result.startswith("refactor: use the real title")
        assert "hallucinated" not in result
        assert "Wait — that's not right" not in result
        assert "Real content" in result

    def test_unwraps_bold_title(self):
        text = "**fix: bold-wrapped title**\n\n**Added:**\n- Stuff"
        result = merge_sections(text, ["Added", "Changed", "Removed"])
        assert result.startswith("fix: bold-wrapped title")

    def test_non_conventional_title_keeps_first_line(self):
        text = "A plain descriptive title\n\nBody text.\n\n**Added:**\n- Stuff"
        result = merge_sections(text, ["Added", "Changed", "Removed"])
        assert result.startswith("A plain descriptive title")
        assert "Body text." in result

    def test_header_with_trailing_whitespace(self):
        text = "feat: x\n\n**Added:**   \n- Login"
        result = merge_sections(text, ["Added", "Changed", "Removed"])
        assert "**Added:**" in result
        assert "Login" in result

    def test_blank_between_preamble_and_first_section(self):
        """Preamble content and the first section must have a blank line between them."""
        text = "fix: bug\n\nSummary line.\n\n**Changed:**\n- Did a thing"
        result = merge_sections(text, ["Added", "Changed", "Removed"])
        lines = result.split("\n")
        # title, blank, preamble, blank, **Changed:**, blank, content
        assert lines[0] == "fix: bug"
        assert lines[1] == ""
        assert lines[2] == "Summary line."
        assert lines[3] == ""
        assert lines[4] == "**Changed:**"


class TestFilterTextIntegration:
    """End-to-end tests for the full filter pipeline."""

    def test_commit_filter(self):
        text = (
            "```\n"
            "feat: add user auth\n\n"
            "**Added:**\n- Login endpoint\n\n"
            "**Changed:**\nNo changes\n\n"
            "**Removed:**\nNothing was removed\n\n"
            "**Added:**\n- Signup endpoint\n"
            "```"
        )
        result = filter_text(text, section_names=["Added", "Changed", "Removed"], max_blanks=2)
        assert result.startswith("feat: add user auth")
        assert "**Added:**" in result
        assert result.count("**Added:**") == 1
        assert "Login endpoint" in result
        assert "Signup endpoint" in result
        assert "**Changed:**" not in result
        assert "**Removed:**" not in result
        assert "```" not in result

    def test_commit_filter_drops_verbose_placeholders(self):
        """Commit filter should drop verbose LLM placeholders and have blank after title."""
        text = (
            "feat: add GitHub Actions workflows\n\n"
            "**Added:**\n\n"
            "- New workflow files\n\n"
            "**Changed:**\n\n"
            "- No existing files were modified; all additions introduce new functionality\n\n"
            "**Removed:**\n\n"
            "- No files or functionality were removed in this update"
        )
        result = filter_text(
            text,
            section_names=["Added", "Changed", "Removed"],
            max_blanks=2,
        )
        assert "**Changed:**" not in result
        assert "**Removed:**" not in result
        assert "**Added:**" in result
        # Commit messages need a blank line after title
        lines = result.split("\n")
        assert lines[0] == "feat: add GitHub Actions workflows"
        assert lines[1] == ""
        assert lines[2] == "**Added:**"

    def test_pr_filter(self):
        text = (
            "feat: new API\n\n"
            "**Key Changes:**\n- New endpoints\n\n"
            "**Added:**\n- GET /users\n\n"
            "**Changed:**\nNo changes\n\n"
            "**Removed:**\nNothing removed\n\n"
            "**Added:**\n- POST /users"
        )
        result = filter_text(
            text,
            section_names=["Key Changes", "Added", "Changed", "Removed"],
        )
        assert "**Key Changes:**" in result
        assert result.count("**Added:**") == 1
        assert "GET /users" in result
        assert "POST /users" in result
        assert "**Changed:**" not in result
        assert "**Removed:**" not in result

    def test_generic_filter_with_preamble(self):
        text = (
            "```markdown\n"
            "Here is the review:\n\n"
            "# Summary\n\n"
            "Code looks good.\n\n\n\n"
            "# Details\n\n"
            "Minor issues.\n"
            "```"
        )
        result = filter_text(text)
        assert "```" not in result
        assert "Here is" not in result
        assert "# Summary" in result
        assert "Code looks good." in result
        assert "# Details" in result

    def test_audit_filter_drops_empty_severity(self):
        text = (
            "# Security Audit\n\n"
            "## CRITICAL\n\n"
            "[No CRITICAL findings]\n\n"
            "## HIGH\n\n"
            "- SQL injection in handler.go\n\n"
            "## MEDIUM\n\n"
            "[None found]\n\n"
            "## LOW\n\n"
            "- None\n\n"
            "## Summary\n\n"
            "One high severity issue."
        )
        result = filter_text(text)
        assert "CRITICAL" not in result
        assert "MEDIUM" not in result
        assert "LOW" not in result
        assert "HIGH" in result
        assert "SQL injection" in result
        assert "Summary" in result
        assert "One high severity" in result

    def test_preserves_internal_code_blocks(self):
        text = (
            "# Review\n\n"
            "Bad code:\n\n"
            "```go\n"
            "func bad() {}\n"
            "```\n\n"
            "Good code:\n\n"
            "```go\n"
            "func good() {}\n"
            "```"
        )
        result = filter_text(text)
        assert "```go" in result
        assert "func bad()" in result
        assert "func good()" in result
        assert result.count("```go") == 2
        assert result.count("```") == 4  # 2 openers + 2 closers

    def test_empty_input(self):
        assert filter_text("") == ""

    def test_title_only(self):
        result = filter_text("feat: small fix", section_names=["Added", "Changed", "Removed"])
        assert result == "feat: small fix"

    def test_pr_filter_drops_verbose_placeholders(self):
        """Placeholder lines like 'No existing files were modified' should be removed."""
        text = (
            "feat: add GitHub Actions workflows\n\n"
            "**Key Changes:**\n\n"
            "- Introduced GitHub Actions workflows\n\n"
            "**Added:**\n\n"
            "- New labeler config\n\n"
            "**Changed:**\n\n"
            "- No existing files were modified; all additions introduce new functionality\n\n"
            "**Removed:**\n\n"
            "- No files or functionality were removed in this update"
        )
        result = filter_text(
            text,
            section_names=["Key Changes", "Added", "Changed", "Removed"],
            blank_after_title=False,
        )
        assert "**Changed:**" not in result
        assert "**Removed:**" not in result
        assert "**Key Changes:**" in result
        assert "**Added:**" in result
        # No blank line between title and first section for PR
        lines = result.split("\n")
        assert lines[0] == "feat: add GitHub Actions workflows"
        assert lines[1] == "**Key Changes:**"

    def test_doubled_fence_with_preamble_regression(self):
        """Regression: doubled fences + preamble before sections produced a `` ` `` title
        and jammed preamble against the first section header (commit df9e2be)."""
        text = (
            "```\n"
            "```\n"
            "fix: update attack operation id filtering\n"
            "**Changed:**\n"
            "- Refined Prometheus query\n"
            "- Modified Tempo query\n"
            "```\n"
            "```"
        )
        result = filter_text(
            text,
            section_names=["Added", "Changed", "Removed"],
            max_blanks=2,
        )
        assert "```" not in result
        lines = result.split("\n")
        assert lines[0] == "fix: update attack operation id filtering"
        assert lines[1] == ""
        assert lines[2] == "**Changed:**"
        assert "Refined Prometheus query" in result
        assert "Modified Tempo query" in result

    def test_no_trailing_whitespace_in_output(self):
        text = "# Review   \n\nContent here   \n\nMore content  "
        result = filter_text(text)
        for line in result.split("\n"):
            assert line == line.rstrip(), f"Trailing whitespace in: {line!r}"

    def test_branch_filter(self):
        text = "feature/auth-123-login-page\n"
        result = filter_text(text)
        assert result == "feature/auth-123-login-page"

    def test_branch_filter_with_fences_and_preamble(self):
        text = "```bash\nHere is the branch name:\nfeature/ui-89-dark-mode-toggle\n```"
        result = filter_text(text)
        assert result == "feature/ui-89-dark-mode-toggle"


class TestStripAttributionLines:
    """Attribution footers Claude Code instructs its model to append."""

    def test_removes_claude_code_markdown_footer(self):
        text = (
            "feat: x\n\n- a change\n\n"
            "🤖 Generated with [Claude Code](https://claude.com/claude-code)"
        )
        assert strip_attribution_lines(text) == "feat: x\n\n- a change\n\n"

    def test_removes_plain_text_footer(self):
        assert strip_attribution_lines("Generated with Claude Code") == ""

    def test_removes_footer_without_emoji(self):
        text = "Generated with [Claude Code](https://claude.com/claude-code)"
        assert strip_attribution_lines(text) == ""

    def test_removes_co_authored_by_claude_trailer(self):
        text = "fix: y\n\nCo-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
        assert strip_attribution_lines(text) == "fix: y\n\n"

    def test_removes_lowercase_co_authored_by(self):
        text = "Co-authored-by: Claude <noreply@anthropic.com>"
        assert strip_attribution_lines(text) == ""

    def test_removes_claude_code_co_author_variant(self):
        text = "Co-Authored-By: Claude Code <noreply@anthropic.com>"
        assert strip_attribution_lines(text) == ""

    def test_removes_antigravity_and_gemini_trailers(self):
        text = (
            "Co-Authored-By: Antigravity <noreply@google.com>\n"
            "Co-Authored-By: Gemini <x@google.com>"
        )
        assert strip_attribution_lines(text) == "\n"

    def test_removes_session_trailer_and_bare_url(self):
        text = (
            "Claude-Session: https://claude.ai/code/session_012abc\n"
            "https://claude.ai/code/session_012abc"
        )
        assert strip_attribution_lines(text) == "\n"

    def test_keeps_bullet_that_mentions_the_footer(self):
        text = "- Strip the 🤖 Generated with Claude Code footer from PR bodies"
        assert strip_attribution_lines(text) == text

    def test_keeps_prose_mentioning_co_authored_by(self):
        text = "- Reject commits whose Co-Authored-By: Claude trailer slipped past the hook"
        assert strip_attribution_lines(text) == text

    def test_keeps_human_co_author(self):
        text = "Co-Authored-By: Jane Doe <jane@example.com>"
        assert strip_attribution_lines(text) == text

    def test_empty_input(self):
        assert strip_attribution_lines("") == ""


class TestFilterTextAttribution:
    """End-to-end: the PR 68 shape, footer after the last section."""

    def test_pr_body_footer_removed_through_pr_filter(self):
        text = (
            "docs: split measurement takes into their own Live set\n\n"
            "**Key Changes:**\n\n- documented the split\n\n"
            "**Removed:**\n\n- the old instruction\n\n"
            "🤖 Generated with [Claude Code](https://claude.com/claude-code)\n"
        )
        result = filter_text(
            text,
            section_names=["Key Changes", "Added", "Changed", "Removed"],
            blank_after_title=False,
        )
        assert "Generated with" not in result
        assert "🤖" not in result
        assert result.endswith("- the old instruction")

    def test_commit_message_trailer_removed_through_commit_filter(self):
        text = (
            "fix: thing\n\n**Changed:**\n\n- did it\n\n"
            "Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>\n"
        )
        result = filter_text(text, section_names=["Added", "Changed", "Removed"], max_blanks=2)
        assert "Co-Authored-By" not in result
        assert "anthropic.com" not in result
        assert result.endswith("- did it")


class TestLooksLikeApiError:
    def test_anthropic_400_error(self):
        text = (
            'POST "https://api.anthropic.com/v1/messages": 400 Bad Request '
            '(Request-ID: req_x) {"type":"error","error":'
            '{"type":"invalid_request_error","message":"`temperature` is deprecated"}}'
        )
        assert looks_like_api_error(text)

    def test_bare_json_error_first_line(self):
        text = '{"type":"error","error":{"type":"overloaded_error"}}'
        assert looks_like_api_error(text)

    def test_error_after_blank_lines(self):
        text = '\n\nPOST "https://api.openai.com/v1/chat": 503 Service Unavailable'
        assert looks_like_api_error(text)

    def test_normal_commit_message(self):
        text = "fix: handle union type\n\n**Changed:**\n\n- Updated extraction"
        assert not looks_like_api_error(text)

    def test_error_mentioned_in_body_only(self):
        text = 'fix: retry on 400 Bad Request\n\nPOST "https://x.example": 400 handling'
        assert not looks_like_api_error(text)

    def test_empty_input(self):
        assert not looks_like_api_error("")


class TestNormalizeHeading:
    def test_ignores_level_and_case_and_spacing(self):
        assert normalize_heading("##   AI / LLM   Assistance ") == normalize_heading(
            "### ai / llm assistance"
        )

    def test_keeps_trailing_colon_significant(self):
        assert normalize_heading("## Testing") != normalize_heading("## Testing:")


class TestDropEmptyBoldSections:
    def test_drops_header_followed_by_another_header(self):
        text = "**Added:**\n\n**Changed:**\n\n- a real change"
        assert drop_empty_bold_sections(text) == "\n**Changed:**\n\n- a real change"

    def test_drops_header_at_end_of_text(self):
        assert drop_empty_bold_sections("- a change\n\n**Removed:**\n") == "- a change\n\n"

    def test_drops_header_followed_by_markdown_heading(self):
        text = "**Removed:**\n\n## Next section\n\nbody"
        assert drop_empty_bold_sections(text) == "\n## Next section\n\nbody"

    def test_keeps_header_with_content(self):
        text = "**Added:**\n\n- a real addition"
        assert drop_empty_bold_sections(text) == text


class TestRequiredHeadings:
    HEADINGS: ClassVar[list[str]] = [
        "## What this PR does / why we need it:",
        "## Which issue(s) this PR fixes:",
        "## AI / LLM Assistance",
    ]

    def test_keeps_required_heading_left_empty(self):
        # The template check greps for the heading, so dropping it as "empty"
        # turns a thin section into a red build.
        text = "## AI / LLM Assistance\n\n"
        assert "## AI / LLM Assistance" in drop_empty_heading_sections(
            text, keep_headings=self.HEADINGS
        )

    def test_still_drops_headings_that_are_not_required(self):
        text = "## Testing\n\n\n## AI / LLM Assistance\n\nDisclosed."
        result = drop_empty_heading_sections(text, keep_headings=self.HEADINGS)
        assert "## Testing" not in result
        assert "## AI / LLM Assistance" in result

    def test_filter_text_preserves_headings_and_order(self):
        text = (
            "feat: add a thing\n"
            "## What this PR does / why we need it:\n\n"
            "**Key Changes:**\n\n- did a thing\n\n"
            "**Removed:**\n\n- No content was removed\n\n"
            "## Which issue(s) this PR fixes:\n\nNo issue is linked.\n\n"
            "## AI / LLM Assistance\n\nGenerated by an LLM from the diff.\n"
        )
        result = filter_text(text, required_headings=self.HEADINGS)

        assert result.splitlines()[0] == "feat: add a thing"
        # Required headings survive in template order...
        assert [ln for ln in result.splitlines() if ln.startswith("## ")] == self.HEADINGS
        # ...the bullets stay under the heading that owns them, rather than being
        # merged to the end of the body the way --sections would move them...
        assert result.index("- did a thing") < result.index("## Which issue(s)")
        # ...and the header whose only line was a stripped placeholder goes too.
        assert "**Removed:**" not in result

    def test_required_headings_suppress_section_merging(self):
        text = (
            "feat: add a thing\n"
            "## What this PR does / why we need it:\n\n"
            "**Added:**\n\n- an addition\n\n"
            "## AI / LLM Assistance\n\nGenerated by an LLM from the diff.\n"
        )
        result = filter_text(
            text,
            section_names=["Key Changes", "Added", "Changed", "Removed"],
            required_headings=self.HEADINGS,
        )
        # merge_sections would have relocated "Added" past the disclosure heading.
        assert result.index("- an addition") < result.index("## AI / LLM Assistance")
