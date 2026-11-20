#!/usr/bin/env python3
"""Fail when a Skill("name") reference does not resolve to a real skill.

Prompts load skills by name. A name that matches no skill makes the agent's
mandatory first iteration fail at runtime, so every reference found in the
repo's markdown and YAML must match the name of a directory holding a
SKILL.md in this repo's skills/ or in a squad-skills checkout.

Usage: check_skill_refs.py [--root DIR] [--skills-dir DIR ...]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REF_RE = re.compile(r"""Skill\(\s*["']([^"']+)["']\s*\)""")
SCAN_SUFFIXES = {".md", ".yaml", ".yml"}
SKIP_DIRS = {".git", ".squad-skills", "_includes", "node_modules", ".venv", "evals"}


def collect_skill_names(skills_dirs: list[Path]) -> set[str]:
    """Return the directory name of every skill under the given directories."""
    return {skill_md.parent.name for base in skills_dirs for skill_md in base.rglob("SKILL.md")}


def is_placeholder(name: str) -> bool:
    """A bare `<name>` documents the call syntax rather than naming a skill."""
    return name.startswith("<") and name.endswith(">") and name.count("<") == 1


def find_refs(root: Path) -> list[tuple[Path, int, str]]:
    """Return (file, line, skill name) for each Skill("...") call under root."""
    refs: list[tuple[Path, int, str]] = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink() or not path.is_file() or path.suffix not in SCAN_SUFFIXES:
            continue
        if SKIP_DIRS.intersection(path.relative_to(root).parts):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for lineno, line in enumerate(text.splitlines(), start=1):
            for match in REF_RE.finditer(line):
                refs.append((path, lineno, match.group(1)))
    return refs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--skills-dir",
        type=Path,
        action="append",
        default=[],
        help="extra directory tree of skills (e.g. a squad-skills checkout)",
    )
    args = parser.parse_args(argv)

    root = args.root.resolve()
    known = collect_skill_names([root / "skills", *args.skills_dir])
    missing = [
        (path, lineno, name)
        for path, lineno, name in find_refs(root)
        if name not in known and not is_placeholder(name)
    ]
    for path, lineno, name in missing:
        print(f'{path.relative_to(root)}:{lineno}: Skill("{name}") matches no skill')
    if missing:
        print(f"{len(missing)} unresolved Skill() reference(s)", file=sys.stderr)
        return 1
    print(f"All Skill() references resolve ({len(known)} skills known)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
