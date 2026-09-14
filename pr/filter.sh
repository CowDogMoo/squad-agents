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

if [ -n "${PR_ALLOWED_TYPES:-}" ]; then
	# The repo's PR-title check accepts only these conventional-commit types.
	# Telling the model is not enough -- a test-only diff still comes back as
	# `test:` -- so the filter rewrites anything off the list.
	while IFS= read -r type_name; do
		[ -n "$type_name" ] && args+=(--allowed-type "$type_name")
	done <<<"$PR_ALLOWED_TYPES"
fi

exec python3 "$SCRIPT_DIR/../scripts/filter.py" "${args[@]}"
