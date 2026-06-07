Your PRIMARY MISSION is VERIFICATION DEPTH — ensuring verify.yml actually tests
everything the role does, not just file existence.

Start by using Glob with '**/molecule/**/*.yml', '**/molecule.yml', and '**/tasks/main.yml'.
You MUST read tasks/main.yml to understand what the role DOES.
Batch Read calls: 4-6 files per iteration.

IMPORTANT CONSTRAINTS:

- Fix ALL verification depth issues (weak assertions, missing checks) FIRST
- Cross-reference role tasks with verify.yml — every action must have a strong assertion
- Fix dead code (unreachable conditions), then config issues, then style
- Batch ALL edits into ONE iteration, verify, then emit report immediately
- Document removed platform-specific code in Issues Skipped table
- NEVER change test-asserted behavior without explicit instruction
- Every file touched must appear in the output report
