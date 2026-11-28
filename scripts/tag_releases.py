#!/usr/bin/env python3
"""Tag the Claude Code plugin this repository ships at its current version.

  tag_releases.py [--root DIR] [--remote NAME] [--ref REF] [--dry-run]

The plugin system resolves a dependency version range against git tags named
`<plugin-name>--v<version>`, where `<version>` equals the `version` in the
plugin's plugin.json at the tagged commit. For every plugin listed in PLUGINS
this reads name and version at REF (default HEAD), and creates and pushes the
tag when the remote does not already have it. A tag that already exists is
left alone, wherever it points: tags are never moved or deleted, so re-running
is a no-op.

Mirrors .github/scripts/tag_releases.py in CowDogMoo/squad-skills so both
repositories tag the same way.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

PLUGINS = (".claude-plugin/plugin.json",)
SEMVER = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")


def git(root: Path, *args: str) -> str:
    # Fixed git argv built by this script; no shell.
    return subprocess.run(  # noqa: S603
        ["git", "-C", str(root), *args],  # noqa: S607
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def tag_name(name: str, version: str) -> str:
    return f"{name}--v{version}"


def release_tags(root: Path, ref: str) -> list[str]:
    """Return the tag each plugin manifest at REF calls for."""
    tags = []
    for rel in PLUGINS:
        manifest = json.loads(git(root, "show", f"{ref}:{rel}"))
        name, version = manifest.get("name"), manifest.get("version")
        if not name or not isinstance(version, str) or not SEMVER.match(version):
            raise ValueError(f"{rel}: need `name` and a semver `version`, got {name!r} {version!r}")
        tags.append(tag_name(name, version))
    return tags


def remote_has(root: Path, remote: str, tag: str) -> bool:
    return bool(git(root, "ls-remote", "--tags", remote, f"refs/tags/{tag}").strip())


def tag_releases(root: Path, remote: str, ref: str, dry_run: bool) -> list[str]:
    """Create and push any missing tag; return the tags it created."""
    sha = git(root, "rev-parse", "--verify", f"{ref}^{{commit}}").strip()
    created = []
    for tag in release_tags(root, ref):
        if remote_has(root, remote, tag):
            print(f"= {tag} already exists on {remote}, leaving it alone")
            continue
        if dry_run:
            print(f"+ would tag {tag} at {sha[:12]}")
        else:
            # Plain push, never forced: an existing remote tag is rejected.
            git(root, "tag", tag, sha)
            git(root, "push", remote, f"refs/tags/{tag}")
            print(f"+ tagged {tag} at {sha[:12]}")
        created.append(tag)
    return created


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument("--remote", default="origin")
    ap.add_argument("--ref", default="HEAD")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    try:
        tag_releases(args.root, args.remote, args.ref, args.dry_run)
    except (ValueError, subprocess.CalledProcessError) as e:
        detail = getattr(e, "stderr", "") or e
        print(f"::error::{detail}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
