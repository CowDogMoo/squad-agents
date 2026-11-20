"""Golden-diff tests for the commit, pr and branch text transforms.

Each case under tests/golden/<transform>/<case>/ holds the raw model output
for one input (raw.txt) and the text the transform's filter.sh must turn it
into (expected.txt). The "-real" cases are model outputs captured by running
the transform's system.md through `squad run --system` on the diff that the
case's `input` file names under tests/golden/inputs/. The other cases add the
failure modes the filter exists to remove (fences, preambles, attribution,
placeholders, false starts, echoed prompt scaffolding) to those captures.

An optional env.json supplies the environment filter.sh reads
(PR_REQUIRED_HEADINGS, PR_ALLOWED_TYPES), and an optional expected_exit holds
the exit status filter.sh must return (default 0).

Regenerate expected.txt after an intended filter change with
`UPDATE_GOLDEN=1 python3 -m pytest tests/test_golden.py`, then review the diff.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from filter import ATTRIBUTION_LINE_RES, CONVENTIONAL_COMMIT_RE, is_angle_placeholder

REPO = Path(__file__).parent.parent
GOLDEN = Path(__file__).parent / "golden"
TRANSFORMS = ("commit", "pr", "branch")
BRANCH_RE = re.compile(r"^[a-z0-9][a-z0-9._/-]*$")


def golden_cases() -> list[Path]:
    return sorted(p for t in TRANSFORMS for p in (GOLDEN / t).iterdir() if p.is_dir())


def case_env(case: Path) -> dict[str, str]:
    env = {
        k: v for k, v in os.environ.items() if k not in ("PR_REQUIRED_HEADINGS", "PR_ALLOWED_TYPES")
    }
    env_file = case / "env.json"
    if env_file.exists():
        env.update(json.loads(env_file.read_text()))
    return env


def run_filter(case: Path) -> subprocess.CompletedProcess:
    transform = case.parent.name
    return subprocess.run(  # noqa: S603 - fixed script path inside the repo
        ["bash", str(REPO / transform / "filter.sh")],  # noqa: S607
        input=(case / "raw.txt").read_bytes(),
        capture_output=True,
        env=case_env(case),
        check=False,
    )


def assert_well_formed(transform: str, text: str, env: dict[str, str]) -> None:
    """Invariants every transform output must hold, whatever the golden says."""
    lines = text.split("\n")
    for line in lines:
        assert not line.lstrip().startswith("```"), f"code fence survived: {line!r}"
        assert not any(rx.match(line) for rx in ATTRIBUTION_LINE_RES), f"attribution: {line!r}"
        assert not is_angle_placeholder(line), f"template placeholder: {line!r}"
        assert line == line.rstrip(), f"trailing whitespace: {line!r}"

    if transform == "branch":
        assert len(lines) == 1, "branch output must be one line"
        assert BRANCH_RE.match(lines[0]), f"not a branch name: {lines[0]!r}"
        return

    title = lines[0]
    assert CONVENTIONAL_COMMIT_RE.match(title), f"not a conventional title: {title!r}"
    assert len(title) <= 80, f"title over 80 characters: {title!r}"
    assert not text.startswith("#"), "output opens with a heading instead of a title"

    allowed = [t for t in env.get("PR_ALLOWED_TYPES", "").split("\n") if t]
    if allowed:
        assert title.split(":", 1)[0].split("(", 1)[0].rstrip("!") in allowed
    for heading in (h for h in env.get("PR_REQUIRED_HEADINGS", "").split("\n") if h):
        assert heading in lines, f"required heading missing: {heading!r}"

    if transform == "commit" and len(lines) > 1:
        assert lines[1] == "", "commit body must follow a blank line"
    if transform == "pr" and "PR_REQUIRED_HEADINGS" not in env and len(lines) > 1:
        assert lines[1].startswith("**"), "pr body must start right after the title"


@pytest.mark.parametrize("case", golden_cases(), ids=lambda p: f"{p.parent.name}/{p.name}")
def test_golden(case: Path):
    transform = case.parent.name
    result = run_filter(case)
    out = result.stdout.decode()

    expected_exit_file = case / "expected_exit"
    expected_exit = int(expected_exit_file.read_text()) if expected_exit_file.exists() else 0
    assert result.returncode == expected_exit, result.stderr.decode()

    expected_file = case / "expected.txt"
    if os.environ.get("UPDATE_GOLDEN"):
        expected_file.write_text(out)
    assert out == expected_file.read_text()

    if expected_exit == 0:
        assert_well_formed(transform, out.rstrip("\n"), case_env(case))
    else:
        assert not out.strip(), "a failed transform must print nothing"

    input_ref = case / "input"
    if input_ref.exists():
        assert (GOLDEN / "inputs" / input_ref.read_text().strip()).is_file()


def test_every_transform_has_golden_cases():
    for transform in TRANSFORMS:
        assert any((GOLDEN / transform).iterdir()), f"no golden cases for {transform}"


@pytest.mark.parametrize("transform", TRANSFORMS)
def test_transform_is_a_prompt_not_an_agent(transform: str):
    """The transforms are a system prompt plus a filter, run with no tools.

    No squad agent shell (agent.yaml, agent.md, task.md), no Claude Code
    subagent export, and no tool grant or model pin in the prompt frontmatter.
    """
    directory = REPO / transform
    assert (directory / "system.md").is_file()
    assert os.access(directory / "filter.sh", os.X_OK)
    for shell in ("agent.yaml", "agent.md", "task.md"):
        assert not (directory / shell).exists(), f"{transform}/{shell} is back"
    assert not (REPO / "agents" / f"{transform}.md").exists()

    text = (directory / "system.md").read_text()
    frontmatter = text.split("---", 2)[1] if text.startswith("---") else ""
    for key in ("tools", "model"):
        assert not re.search(rf"^{key}:", frontmatter, re.MULTILINE), f"{transform}: {key}"
