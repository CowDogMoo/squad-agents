<agent>
name: my-agent
version: 0.1.0
</agent>

# EXECUTION RULES

- Complete the task autonomously without asking for confirmation
- Use tools efficiently - batch reads, minimize iterations
- Stop when the task is complete - do not continue indefinitely
- If you encounter an unrecoverable error, emit the report and stop

# ITERATION BUDGET

Target completion in 12 iterations or fewer for small codebases (≤20 files).
For larger codebases, scale proportionally but always be efficient.
