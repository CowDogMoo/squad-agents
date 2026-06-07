Review and fix all Ansible code quality issues in this codebase.

Start by using Glob with '**/*.yml' and '**/*.yaml' to discover all YAML files.
Filter to Ansible-relevant files (playbooks, tasks, handlers, vars, defaults, meta, molecule).
Batch Read calls: 4-6 files per iteration.

IMPORTANT CONSTRAINTS:

- Fix ALL CRITICAL (security, correctness) before HIGH, all HIGH before MEDIUM
- No cosmetic changes (whitespace, comment style, import ordering)
- Preserve backwards compatibility — no variable renames or role restructuring
- NEVER change behavior asserted by Molecule tests
- NEVER remove changed_when — fix `false` to `true` on state-changing commands
- Every fix must be PROPORTIONAL — no theoretical improvements
- Batch ALL edits into ONE iteration, verify, then emit report immediately
- Every file touched must appear in the output report
