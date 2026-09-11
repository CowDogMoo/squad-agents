#!/bin/bash
# Post-processing filter for PR pattern output
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

args=(--no-blank-after-title)
if [ -n "${PR_REQUIRED_HEADINGS:-}" ]; then
	# The repo ships a PR template whose required headings a CI check greps for.
	# Those headings own the body's structure, so the default section merging is
	# dropped here: it reorders every named section to the end and would strand
	# the bullets under whichever heading happens to come last.
	while IFS= read -r heading; do
		[ -n "$heading" ] && args+=(--required-heading "$heading")
	done <<<"$PR_REQUIRED_HEADINGS"
else
	args+=(--sections "Key Changes,Added,Changed,Removed")
fi

exec python3 "$SCRIPT_DIR/../scripts/filter.py" "${args[@]}"
