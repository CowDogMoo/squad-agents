# TASK

Generate the changelog entry for everything merged since this repository's last
release, reading the git history directly.

# SCOPE

- Detect the changelog format: Keep a Changelog markdown, or
  antsibull-changelog YAML for an Ansible collection
- Resolve the commit range from the last tag or the newest version heading
- Classify each commit into the six standard categories, discarding internals
- Write the entry under `## [Unreleased]`, or into `changelogs/changelog.yaml`

# PRIORITIES

1. **User-facing impact** - describe what changed for someone using the
   project, not how it was implemented
2. **Accurate attribution** - every entry traces to a real commit; include the
   issue or PR reference when present
3. **Breaking changes surfaced** - called out explicitly, never buried
4. **Grouped, not transcribed** - related commits merge into one entry

# CONSTRAINTS

- Do NOT invent entries that no commit supports
- Do NOT include refactors, CI, formatting, or test-only changes
- Do NOT modify or reflow previously released sections
- Do NOT commit, tag, or push anything
- Do NOT wrap the changelog file's contents in a code fence
