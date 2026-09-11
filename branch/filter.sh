#!/bin/bash
# Post-processing filter for branch pattern output.
#
# The pattern emits exactly one line — a git branch name — but models
# occasionally prepend narration ("I'll analyze this diff...") despite the
# instructions. The shared filter only strips "Here is..."-style
# announcements, so instead of trusting position, reduce the output to the
# last line that is a plausible git ref. Narration never survives the
# character class (it contains spaces), and the branch name is always the
# final matching line. Empty output (no plausible ref) exits non-zero so
# callers detect the failed generation.
set -o pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
python3 "$SCRIPT_DIR/../scripts/filter.py" |
	grep -E '^[A-Za-z0-9][A-Za-z0-9._/-]*$' |
	tail -n 1
