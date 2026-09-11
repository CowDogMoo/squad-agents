Generate the commit text for the input in the User Message, following
system.md exactly.

If the User Message is empty and you can run commands, obtain the input once
with the staged diff via `git diff --staged` and continue. If no input can be obtained,
output exactly `NO INPUT` and nothing else.

CONSTRAINTS:

- Output only the generated text; no headings, fences, or explanations around it
- Do not modify any file or run any state-changing git or gh command
- Do not add attribution lines, trailers, or signatures
