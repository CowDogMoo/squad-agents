"""Tests for scripts/tag_releases.py against throwaway repositories, never a real remote."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import tag_releases

REPO = Path(__file__).resolve().parents[1]


def git(cwd: Path, *args: str) -> str:
    return subprocess.run(  # noqa: S603 - fixed git argv against temp repos
        ["git", "-C", str(cwd), "-c", "user.name=t", "-c", "user.email=t@example.com", *args],  # noqa: S607
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def write_manifest(root: Path, version: str) -> None:
    path = root / tag_releases.PLUGINS[0]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"name": "squad-agents", "version": version}))


def commit(work: Path, msg: str) -> str:
    git(work, "add", "-A")
    git(work, "commit", "-q", "-m", msg)
    return git(work, "rev-parse", "HEAD").strip()


@pytest.fixture
def repos(tmp_path):
    remote = tmp_path / "remote.git"
    git(tmp_path, "init", "-q", "--bare", str(remote))
    work = tmp_path / "work"
    git(tmp_path, "init", "-q", str(work))
    git(work, "remote", "add", "origin", str(remote))
    write_manifest(work, "1.2.3")
    commit(work, "release 1.2.3")
    return work, remote


def remote_tags(remote: Path) -> dict[str, str]:
    out = git(remote, "for-each-ref", "--format=%(refname:short) %(objectname)", "refs/tags")
    return dict(line.split() for line in out.splitlines())


def run_tagger(work: Path, dry_run: bool = False) -> list[str]:
    return tag_releases.tag_releases(work, "origin", "HEAD", dry_run)


def test_creates_tag_once(repos):
    work, remote = repos
    sha = git(work, "rev-parse", "HEAD").strip()
    assert run_tagger(work) == ["squad-agents--v1.2.3"]
    assert remote_tags(remote) == {"squad-agents--v1.2.3": sha}
    assert run_tagger(work) == []
    assert remote_tags(remote) == {"squad-agents--v1.2.3": sha}


def test_existing_tag_is_never_moved(repos):
    work, remote = repos
    old = git(work, "rev-parse", "HEAD").strip()
    run_tagger(work)
    (work / "note.txt").write_text("later commit")
    commit(work, "later")
    assert run_tagger(work) == []
    assert remote_tags(remote)["squad-agents--v1.2.3"] == old


def test_new_version_adds_tag_and_keeps_old_one(repos):
    work, remote = repos
    old = git(work, "rev-parse", "HEAD").strip()
    run_tagger(work)
    write_manifest(work, "1.3.0")
    new = commit(work, "release 1.3.0")
    assert run_tagger(work) == ["squad-agents--v1.3.0"]
    assert remote_tags(remote) == {"squad-agents--v1.2.3": old, "squad-agents--v1.3.0": new}


def test_tag_already_on_remote_is_left_alone(repos):
    work, remote = repos
    first = git(work, "rev-parse", "HEAD").strip()
    git(work, "tag", "squad-agents--v1.2.3")
    git(work, "push", "-q", "origin", "refs/tags/squad-agents--v1.2.3")
    (work / "note.txt").write_text("later commit")
    commit(work, "later")
    assert run_tagger(work) == []
    assert remote_tags(remote) == {"squad-agents--v1.2.3": first}


def test_dry_run_changes_nothing(repos):
    work, remote = repos
    assert run_tagger(work, dry_run=True) == ["squad-agents--v1.2.3"]
    assert remote_tags(remote) == {}
    assert git(work, "tag").strip() == ""


@pytest.mark.parametrize("version", ["not-a-version", "1.2", ""])
def test_bad_version_is_an_error(repos, version):
    work, remote = repos
    write_manifest(work, version)
    commit(work, "bad")
    with pytest.raises(ValueError, match="semver"):
        run_tagger(work)
    assert remote_tags(remote) == {}


def test_main_reports_error_and_exits_nonzero(repos, capsys):
    work, _ = repos
    write_manifest(work, "bad")
    commit(work, "bad")
    assert tag_releases.main(["--root", str(work)]) == 1
    assert capsys.readouterr().out.startswith("::error::")


def test_real_manifest_names_squad_agents():
    tags = tag_releases.release_tags(REPO, "HEAD")
    assert [t.split("--v")[0] for t in tags] == ["squad-agents"]
