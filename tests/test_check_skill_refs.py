"""Tests for scripts/check_skill_refs.py — the Skill() reference resolver."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from check_skill_refs import collect_skill_names, is_placeholder, main


def make_skill(base: Path, dirname: str, name: str | None = None) -> None:
    skill = base / dirname
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(f"---\nname: {name or dirname}\n---\nbody\n")


def test_collect_names_uses_dir_and_frontmatter(tmp_path):
    make_skill(tmp_path / "testing", "dirname", "front-name")
    assert collect_skill_names([tmp_path]) == {"dirname", "front-name"}


def test_placeholder_only_bare_angle_names():
    assert is_placeholder("<name>")
    assert not is_placeholder("enqueue-coverage-targets-<lang>")


def test_resolving_reference_passes(tmp_path):
    make_skill(tmp_path / "skills", "real-skill")
    (tmp_path / "agent.md").write_text('Load `Skill("real-skill")`.\n')
    assert main(["--root", str(tmp_path)]) == 0


def test_broken_reference_fails(tmp_path, capsys):
    make_skill(tmp_path / "skills", "real-skill")
    (tmp_path / "agent.md").write_text('Load `Skill("real-skill-go")`.\n')
    assert main(["--root", str(tmp_path)]) == 1
    assert 'agent.md:1: Skill("real-skill-go") matches no skill' in capsys.readouterr().out


def test_external_skills_dir_resolves(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    make_skill(tmp_path / "ext" / "testing", "shared-skill")
    (root / "system.md").write_text("Skill('shared-skill')\n")
    assert main(["--root", str(root)]) == 1
    assert main(["--root", str(root), "--skills-dir", str(tmp_path / "ext")]) == 0
