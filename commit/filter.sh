#!/bin/bash
# Post-processing filter for commit pattern output
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
exec python3 "$SCRIPT_DIR/../scripts/filter.py" --sections "Added,Changed,Removed" --max-blanks 2
