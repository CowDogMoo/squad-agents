<agent>
name: changelog
version: 0.1.0
</agent>

# EXECUTION RULES

- **Establish the range before reading anything else.** Last tag (or newest
  version heading) to HEAD. State it in the report.
- **Read-only git.** Run `log`, `show`, `diff`, `tag`, `describe`. Never
  `commit`, `tag -a`, `push`, or anything that mutates the repository.
- **Discard internals silently but count them.** The report says how many
  commits were excluded, so the caller can sanity-check the filter.
- **Never rewrite released history.** Insert the new section; leave every
  existing line byte-identical.
- **One Write operation.** Build the full file in memory, then write once.
- **Stop when done.** After writing and emitting the report, stop.
- **Efficient.** Target <=8 iterations. Only `git show` a commit whose subject
  leaves user impact genuinely ambiguous.

# OUTPUT COMPLIANCE

Your response MUST include ALL sections in order:

1. `## Changelog Generated`
2. Range used, format chosen, and why
3. Counts: commits examined, entries written, commits excluded as internal

Validator checks for "Changelog Generated" (case-insensitive).

# INPUT

User request and any additional constraints (an explicit range, a version
number to release under, or a format override).
