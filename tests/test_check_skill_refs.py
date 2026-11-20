"""Tests for scripts/check_skill_refs.py — the Skill() reference resolver."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from check_skill_refs import is_placeholder, main


def make_skill(base: Path, dirname: str) -> None:
    skill = base / dirname
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(f"---\nname: {dirname}\n---\nbody\n")


@pytest.fixture
def repo(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    make_skill(tmp_path / "ext" / "engineering", "real-skill")
    return root, tmp_path / "ext"


def run(root: Path, ext: Path) -> int:
    return main(["--root", str(root), "--skills-dir", str(ext)])


def test_placeholder_only_bare_angle_names():
    assert is_placeholder("<name>")
    assert not is_placeholder("enqueue-coverage-targets-<lang>")


def test_resolving_reference_passes(repo):
    root, ext = repo
    (root / "agent.md").write_text('Load `Skill("real-skill")`.\n')
    assert run(root, ext) == 0


def test_broken_reference_fails(repo, capsys):
    root, ext = repo
    (root / "agent.md").write_text('Load `Skill("real-skill-go")`.\n')
    assert run(root, ext) == 1
    assert 'agent.md:1: Skill("real-skill-go") matches no skill' in capsys.readouterr().out


def test_skills_dir_is_required(repo):
    root, _ = repo
    with pytest.raises(SystemExit):
        main(["--root", str(root)])


def test_empty_skills_dir_fails(repo, tmp_path):
    root, _ = repo
    (tmp_path / "empty").mkdir()
    assert run(root, tmp_path / "empty") == 1
