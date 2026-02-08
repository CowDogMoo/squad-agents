# TASK

Review the codebase for quality issues and best practice violations.

# SCOPE

- Focus on the main source directories
- Skip vendored, generated, and test fixtures
- Prioritize issues by severity: CRITICAL > HIGH > MEDIUM > LOW

# PRIORITIES

1. **CRITICAL**: Security vulnerabilities, crashes, data loss
2. **HIGH**: Bugs, incorrect behavior, resource leaks
3. **MEDIUM**: Code quality, maintainability, inconsistencies
4. **LOW**: Style, minor improvements

# CONSTRAINTS

- Do NOT over-engineer - simple fixes only
- Do NOT add new dependencies
- Do NOT refactor working code just for style
- Do NOT add comments/docs unless fixing a bug requires explanation
