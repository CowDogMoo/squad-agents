#!/usr/bin/env python3
"""Fail when a skill an agent names does not resolve to a real skill.

Agents name skills two ways: the `skills:` list in a prompt's YAML
frontmatter, which Claude Code preloads, and `Skill("name")` calls, which
hosts that do not preload (squad) run instead. A name that matches no skill
makes the agent's mandatory first iteration fail at runtime, so every name
found in the repo's markdown and YAML must match the name of a directory
holding a SKILL.md in one of the given skill trees (a squad-skills checkout).

Usage: check_skill_refs.py --skills-dir DIR [--skills-dir DIR ...] [--root DIR]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REF_RE = re.compile(r"""Skill\(\s*["']([^"']+)["']\s*\)""")
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---(?:\n|\Z)", re.DOTALL)
LIST_ITEM_RE = re.compile(r"^\s+-\s+[\"']?([^\"'#\s]+)[\"']?\s*(?:#.*)?$")
SCAN_SUFFIXES = {".md", ".yaml", ".yml"}
SKIP_DIRS = {".git", ".squad-skills", "_includes", "node_modules", ".venv", "evals"}


def collect_skill_names(skills_dirs: list[Path]) -> set[str]:
    """Return the directory name of every skill under the given directories."""
    return {skill_md.parent.name for base in skills_dirs for skill_md in base.rglob("SKILL.md")}


def is_placeholder(name: str) -> bool:
    """A bare `<name>` documents the call syntax rather than naming a skill."""
    return name.startswith("<") and name.endswith(">") and name.count("<") == 1


def frontmatter_skills(text: str) -> list[tuple[int, str]]:
    """Return (line, name) for each entry of a leading frontmatter `skills:` list."""
    match = FRONTMATTER_RE.match(text)
    if not match:
        return []
    found: list[tuple[int, str]] = []
    in_skills = False
    # Line 1 is the opening `---`, so frontmatter line i is file line i + 2.
    for offset, line in enumerate(match.group(1).splitlines(), start=2):
        if re.match(r"^skills:\s*$", line):
            in_skills = True
            continue
        if in_skills:
            item = LIST_ITEM_RE.match(line)
            if item:
                found.append((offset, item.group(1)))
                continue
            in_skills = False
    return found


def find_refs(root: Path) -> list[tuple[Path, int, str]]:
    """Return (file, line, skill name) for each skill named under root."""
    refs: list[tuple[Path, int, str]] = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink() or not path.is_file() or path.suffix not in SCAN_SUFFIXES:
            continue
        if SKIP_DIRS.intersection(path.relative_to(root).parts):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if path.suffix == ".md":
            refs.extend((path, lineno, name) for lineno, name in frontmatter_skills(text))
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
        required=True,
        help="directory tree of skills (e.g. a squad-skills checkout); repeatable",
    )
    args = parser.parse_args(argv)

    root = args.root.resolve()
    known = collect_skill_names(args.skills_dir)
    if not known:
        print("no SKILL.md found under --skills-dir", file=sys.stderr)
        return 1
    missing = [
        (path, lineno, name)
        for path, lineno, name in find_refs(root)
        if name not in known and not is_placeholder(name)
    ]
    for path, lineno, name in missing:
        print(f'{path.relative_to(root)}:{lineno}: skill "{name}" matches no skill')
    if missing:
        print(f"{len(missing)} unresolved skill reference(s)", file=sys.stderr)
        return 1
    print(f"All skill references resolve ({len(known)} skills known)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
