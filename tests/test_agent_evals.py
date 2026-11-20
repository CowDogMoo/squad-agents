"""Tests for scripts/agent_evals.py: case validation and plugin staging.

No model is called. The paid runs are `agent_evals.py run`; these tests pin
what that command stages and passes to `claude plugin eval`.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import agent_evals  # noqa: E402


def run_args(**overrides) -> argparse.Namespace:
    values = {
        "ablation": "none",
        "model": agent_evals.DEFAULT_MODEL,
        "judge_model": agent_evals.DEFAULT_JUDGE,
        "runs": 3,
        "concurrency": 1,
        "case": None,
        "max_cost_usd": None,
        "without_bash": False,
    }
    values.update(overrides)
    return argparse.Namespace(**values)


@pytest.fixture
def case_copy(tmp_path: Path) -> Path:
    """A copy of the cobra-mini case whose fixture link points at the real fixture."""
    case_dir = tmp_path / "go-cobra-cobra-mini"
    case_dir.mkdir()
    shutil.copyfile(agent_evals.EVALS / case_dir.name / "case.yaml", case_dir / "case.yaml")
    (case_dir / "fixture").symlink_to(ROOT / "go-cobra" / "testdata" / "cobra-mini")
    return case_dir


def edit_case(case_dir: Path, change) -> None:
    """Apply change to the parsed case.yaml and write it back.

    Editing the parsed data, not the text, keeps these tests independent of
    how the file is formatted (quoting, flow vs block style).
    """
    path = case_dir / "case.yaml"
    case = yaml.safe_load(path.read_text(encoding="utf-8"))
    change(case)
    path.write_text(yaml.safe_dump(case, sort_keys=False), encoding="utf-8")


def grader(case: dict, name: str) -> dict:
    return next(g for g in case["graders"] if g["name"] == name)


def test_every_case_in_the_repo_is_valid() -> None:
    agents = agent_evals.agent_names()
    cases = agent_evals.case_dirs()
    assert cases, "no cases under evals/"
    for case_dir in cases:
        assert agent_evals.check_case(case_dir, agents) == [], case_dir.name


def test_validate_command_passes() -> None:
    assert agent_evals.main(["validate"]) == 0


def _prompt(case: dict, old: str, new: str) -> None:
    case["execution"]["prompt"] = case["execution"]["prompt"].replace(old, new)


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (lambda c: c.update(name="other"), "does not match the directory"),
        (
            lambda c: _prompt(c, "squad-agents:go-cobra", "squad-agents:no-such-agent"),
            "not in agents/",
        ),
        (lambda c: _prompt(c, "squad-agents:go-cobra", "go-cobra"), "must name the agent"),
        (lambda c: c["context"].update(scaffold_script="setup.sh"), "stage generates it"),
        (
            lambda c: grader(c, "grade-adds-no-markflagrequired")["target"].update(
                path="cmd/missing.go"
            ),
            "is not a file in the fixture",
        ),
        (lambda c: c["execution"]["allowed_tools"].remove("Bash"), "must include"),
        (lambda c: c["execution"].update(env={"GOPROXY": "off"}), "accepts only EVAL_* keys"),
        (
            lambda c: grader(c, "grade-adds-no-markflagrequired").update(pattern="Mark(Flag"),
            "does not compile",
        ),
    ],
)
def test_problems_are_caught(case_copy: Path, change, message: str) -> None:
    edit_case(case_copy, change)
    errors = agent_evals.check_case(case_copy, agent_evals.agent_names())
    assert any(message in e for e in errors), errors


def test_only_tool_used_graders_are_refused(case_copy: Path) -> None:
    edit_case(
        case_copy,
        lambda c: c.update(graders=[{"name": "delegated", "type": "tool_used", "tool": "Agent"}]),
    )
    errors = agent_evals.check_case(case_copy, agent_evals.agent_names())
    assert any("grade outcomes" in e for e in errors), errors


def test_checked_in_scaffold_is_refused(case_copy: Path) -> None:
    (case_copy / "scaffold.sh").write_text("#!/bin/sh\n", encoding="utf-8")
    errors = agent_evals.check_case(case_copy, agent_evals.agent_names())
    assert any("must not be checked in" in e for e in errors), errors


def fake_squad_skills(root: Path) -> Path:
    skills = root / "squad-skills"
    (skills / ".claude-plugin").mkdir(parents=True)
    (skills / ".claude-plugin" / "plugin.json").write_text(
        json.dumps({"name": "squad-skills", "skills": ["./engineering"]}), encoding="utf-8"
    )
    skill = skills / "engineering" / "cobra-viper-best-practices"
    (skill / "evals").mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: cobra-viper-best-practices\n---\n", encoding="utf-8"
    )
    (skill / "evals" / "evals.json").write_text("{}", encoding="utf-8")
    (skills / "engineering" / "_trigger-evals").mkdir()
    return skills


def test_stage_builds_one_plugin(tmp_path: Path) -> None:
    skills = fake_squad_skills(tmp_path)
    plugin = agent_evals.stage(skills, tmp_path / "out")
    manifest = json.loads((plugin / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    assert manifest == {"name": "squad-agents"}
    agents = plugin / "agents" / "go-cobra.md"
    assert agents.is_file()
    assert not agents.is_symlink()
    assert agents.read_text(encoding="utf-8") == (ROOT / "go-cobra" / "system.md").read_text(
        encoding="utf-8"
    )
    skill = plugin / "skills" / "cobra-viper-best-practices"
    assert (skill / "SKILL.md").is_file()
    assert not (skill / "evals").exists(), "a skill's own expectations must not be staged"
    assert not (plugin / "skills" / "_trigger-evals").exists()
    for case_dir in agent_evals.case_dirs():
        out = plugin / "evals" / case_dir.name
        assert (out / "case.yaml").read_bytes() == (case_dir / "case.yaml").read_bytes()
        assert (out / "fixture").is_dir()
        assert not (out / "fixture").is_symlink()
        assert (out / "fixture" / "go.mod").is_file()
        scaffold = out / "scaffold.sh"
        assert scaffold.read_text(encoding="utf-8") == agent_evals.SCAFFOLD_SCRIPT
        assert os.access(scaffold, os.X_OK)


def test_stage_refuses_to_overwrite(tmp_path: Path) -> None:
    skills = fake_squad_skills(tmp_path)
    agent_evals.stage(skills, tmp_path / "out")
    with pytest.raises(SystemExit):
        agent_evals.stage(skills, tmp_path / "out")


def test_eval_command_grants_and_flags(tmp_path: Path) -> None:
    cmd = agent_evals.eval_command(
        tmp_path, tmp_path, run_args(ablation="with-without", case="go-*")
    )
    tools = cmd[cmd.index("--allow-tools") + 1 : cmd.index("--ablation")]
    assert tools == ["Bash", "Edit", "Write"]
    assert cmd[cmd.index("--ablation") + 1] == "with-without"
    for flag in ("--scaffold", "--trust-plugin", "--no-publish"):
        assert flag in cmd
    assert cmd[cmd.index("--case") + 1] == "go-*"
    cmd = agent_evals.eval_command(tmp_path, tmp_path, run_args(without_bash=True))
    tools = cmd[cmd.index("--allow-tools") + 1 : cmd.index("--ablation")]
    assert tools == ["Edit", "Write"]


def test_run_env_keeps_go_offline() -> None:
    env = agent_evals.run_env()
    assert env["GOPROXY"] == "off"
    assert env["GOTOOLCHAIN"] == "local"


def test_scaffold_copies_and_commits_the_fixture(tmp_path: Path) -> None:
    if shutil.which("git") is None:
        pytest.skip("git is not installed")
    case = tmp_path / "case"
    case.mkdir()
    (case / "fixture").mkdir()
    (case / "fixture" / "a.txt").write_text("a\n", encoding="utf-8")
    script = case / "scaffold.sh"
    script.write_text(agent_evals.SCAFFOLD_SCRIPT, encoding="utf-8")
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    env = {"PATH": os.environ["PATH"], "HOME": str(tmp_path), "GIT_CONFIG_NOSYSTEM": "1"}
    subprocess.run(["bash", str(script)], cwd=cwd, env=env, check=True)  # noqa: S603, S607
    assert (cwd / "a.txt").read_text(encoding="utf-8") == "a\n"
    status = subprocess.run(
        ["git", "status", "--porcelain"],  # noqa: S607
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert status == ""
