---
name: changelog-standards
description: "Standards for writing and evaluating changelogs — Keep a Changelog structure, the six change categories, entry style, semantic versioning and breaking changes, release patterns, and the antsibull-changelog YAML format for Ansible collections. Use when writing a release entry, reviewing a CHANGELOG, or deciding which commits are user-facing. Also loaded by the changelog agent as its knowledge base."
---
# Changelog Standards

A comprehensive guide to writing and maintaining changelogs following the Keep a Changelog specification and semantic versioning best practices. This document serves as the knowledge base for the changelog pattern.

## Table of Contents

1. [Core Principles](#core-principles)
2. [Changelog Format](#changelog-format)
3. [Change Categories](#change-categories)
4. [Writing Guidelines](#writing-guidelines)
5. [Version Numbering](#version-numbering)
6. [Common Patterns](#common-patterns)
7. [Quality Checklist](#quality-checklist)

---

## Core Principles

### What is a Changelog?

A changelog is a file containing a curated, chronologically ordered list of notable changes for each version of a project.

### Why Keep a Changelog?

| Benefit | Description |
|---------|-------------|
| User awareness | Help users understand what changed |
| Upgrade decisions | Help users decide when to upgrade |
| Release tracking | Document release history |
| Team communication | Share changes across team |

### Guiding Principles

1. Changelogs are for **humans**, not machines
2. There should be an entry for **every version**
3. The same types of changes should be **grouped**
4. Versions and sections should be **linkable**
5. Latest version comes **first**
6. Release **date** of each version is displayed
7. Follow **Semantic Versioning**

---

## Changelog Format

### File Structure

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- New features not yet released

## [1.0.0] - 2026-01-10

### Added
- Initial release with core features

[Unreleased]: https://github.com/user/repo/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/user/repo/releases/tag/v1.0.0
```

### Version Header Format

```markdown
## [X.Y.Z] - YYYY-MM-DD
```

Components:

- `X.Y.Z` - Semantic version number
- `YYYY-MM-DD` - ISO 8601 date format
- Square brackets for linkability

---

## Change Categories

### Standard Categories

Use these categories in this order:

| Category | Description | Examples |
|----------|-------------|----------|
| **Added** | New features | New API endpoint, new command |
| **Changed** | Changes to existing functionality | Modified behavior, updated dependency |
| **Deprecated** | Features marked for removal | Deprecated function, deprecated flag |
| **Removed** | Removed features | Deleted endpoint, removed command |
| **Fixed** | Bug fixes | Corrected error, fixed crash |
| **Security** | Security fixes | Patched vulnerability, fixed auth issue |

### Category Guidelines

**Added:**

- New features, capabilities, or functionality
- New modules, commands, or API endpoints
- New configuration options

**Changed:**

- Modifications to existing functionality
- Updated dependencies (major versions)
- Changed default behaviors
- Renamed items

**Deprecated:**

- Features that will be removed in future versions
- Include migration path when possible
- Specify target removal version if known

**Removed:**

- Features that have been removed
- Only use after deprecation period (when possible)

**Fixed:**

- Bug corrections
- Error handling improvements
- Performance fixes

**Security:**

- Security vulnerability fixes
- Authentication/authorization fixes
- Data protection improvements
- Include CVE numbers when applicable

---

## Writing Guidelines

### Entry Format

**Good entries:**

```markdown
- Added `--verbose` flag to enable detailed output (#123)
- Fixed crash when processing empty files
- Changed default timeout from 30s to 60s
- Deprecated `OldFunction()` in favor of `NewFunction()`
```

**Bad entries:**

```markdown
- Fixed bug  # Too vague
- Various improvements  # Not specific
- Updated code  # Meaningless
- Bumped version  # Not user-relevant
```

### Style Guidelines

| Guideline | Example |
|-----------|---------|
| Use imperative mood | "Add feature" not "Added feature" in commits, but "Added" in changelog |
| Start with verb | "Fixed", "Added", "Removed" |
| Be specific | Name the function, command, or feature |
| Include references | Issue numbers, PR links |
| Keep entries concise | One line per change |

### What to Include

**Include:**

- User-facing changes
- API changes
- Breaking changes
- Security fixes
- Significant bug fixes
- Deprecation notices

**Exclude:**

- Internal refactoring (unless affecting performance)
- Development tooling changes
- Minor dependency updates
- Typo fixes (unless in user-facing content)
- CI/CD changes (unless affecting releases)

### Reference Linking

```markdown
- Fixed authentication bypass vulnerability ([CVE-2026-1234])
- Added new export command (#456)
- Changed configuration format (see [Migration Guide])

[CVE-2026-1234]: https://nvd.nist.gov/vuln/detail/CVE-2026-1234
[Migration Guide]: docs/migration.md
```

---

## Version Numbering

### Semantic Versioning (SemVer)

Format: `MAJOR.MINOR.PATCH`

| Component | When to Increment |
|-----------|-------------------|
| MAJOR | Breaking/incompatible API changes |
| MINOR | New functionality (backwards-compatible) |
| PATCH | Bug fixes (backwards-compatible) |

### Pre-release Versions

```markdown
## [1.0.0-alpha.1] - 2026-01-01
## [1.0.0-beta.1] - 2026-01-05
## [1.0.0-rc.1] - 2026-01-08
## [1.0.0] - 2026-01-10
```

### Breaking Changes

Always highlight breaking changes prominently:

```markdown
## [2.0.0] - 2026-01-10

### Changed

- **BREAKING:** Renamed `config.yaml` to `settings.yaml`
- **BREAKING:** Changed API response format for `/users` endpoint
```

---

## Common Patterns

### Initial Release

```markdown
## [1.0.0] - 2026-01-10

### Added

- Initial release
- Core functionality for X, Y, and Z
- Command-line interface with basic commands
- Configuration file support
- Documentation and examples
```

### Feature Release

```markdown
## [1.1.0] - 2026-02-15

### Added

- New `export` command for data export (#234)
- Support for YAML configuration files
- Plugin system for custom extensions

### Changed

- Improved error messages with more context
- Updated default timeout from 30s to 60s

### Fixed

- Fixed memory leak in long-running processes (#245)
```

### Bug Fix Release

```markdown
## [1.0.1] - 2026-01-15

### Fixed

- Fixed crash when input file is empty (#201)
- Fixed incorrect calculation in edge cases
- Fixed typo in error messages

### Security

- Fixed authentication bypass vulnerability ([CVE-2026-1234])
```

### Deprecation and Removal

```markdown
## [1.2.0] - 2026-03-01

### Deprecated

- `OldFunction()` is deprecated, use `NewFunction()` instead
  Will be removed in v2.0.0

## [2.0.0] - 2026-06-01

### Removed

- Removed `OldFunction()` (deprecated in v1.2.0)
```

---

## Special Formats

### Ansible/antsibull-changelog Format

For Ansible collections using antsibull-changelog:

```yaml
---
release_summary: "Brief 1-2 sentence overview of this release"
added:
  - "role_name - Added new feature X"
  - "module_name - Added Y capability"
changed:
  - "role_name - Enhanced Z functionality"
fixed:
  - "role_name - Fixed issue with W"
```

**Rules for antsibull-changelog:**

- `release_summary` is a single string, not a list
- All other categories are lists of strings
- Prefix changes with module/role/plugin name
- Use past tense: "Added", "Enhanced", "Fixed"
- Output only raw YAML content

---

## Quality Checklist

### Before Release

- [ ] All user-facing changes documented
- [ ] Changes grouped by category
- [ ] Categories in standard order
- [ ] Entries are specific and actionable
- [ ] Breaking changes highlighted
- [ ] Version follows SemVer
- [ ] Date in ISO 8601 format
- [ ] References linked (issues, PRs, CVEs)
- [ ] Unreleased section updated

### Entry Quality

- [ ] Starts with appropriate verb
- [ ] Specific about what changed
- [ ] Includes reference numbers
- [ ] Single change per entry
- [ ] Written for users, not developers

---

## Anti-Patterns

### Don't Do This

```markdown
# Bad Examples

## v1.0
- Various bug fixes
- Updated dependencies
- Code cleanup
- Misc improvements
```

### Do This Instead

```markdown
# Good Examples

## [1.0.0] - 2026-01-10

### Added
- New `export` command for CSV data export (#123)

### Fixed
- Fixed crash when processing files over 1GB (#456)

### Changed
- Updated authentication library to v2.0 for security improvements
```

---

## References

- [Keep a Changelog](https://keepachangelog.com/)
- [Semantic Versioning](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [antsibull-changelog](https://github.com/ansible-community/antsibull-changelog)

---

*Last updated: 2026-01-10*
