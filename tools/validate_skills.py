#!/usr/bin/env python3
"""Validate the structure of every skill under skills/.

Dependency-free. For each skills/<name>/ it checks:
  - SKILL.md exists
  - SKILL.md begins with a YAML frontmatter block (--- ... ---)
  - frontmatter defines non-empty `name` and `description`
  - `name` equals the folder name

Exits non-zero (and prints every problem) if any check fails. Run in CI.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"


def parse_frontmatter(text: str) -> dict[str, str] | None:
    """Minimal YAML-frontmatter parser: returns top-level key/value strings."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    out: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return out
        if ":" in line and not line.startswith((" ", "\t", "#")):
            key, _, value = line.partition(":")
            out[key.strip()] = value.strip()
    return None  # no closing delimiter


def main() -> int:
    if not SKILLS_DIR.is_dir():
        print(f"ERROR: {SKILLS_DIR} not found")
        return 1

    errors: list[str] = []
    skill_dirs = sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir())
    if not skill_dirs:
        print("ERROR: no skills found under skills/")
        return 1

    for d in skill_dirs:
        name = d.name
        skill_md = d / "SKILL.md"
        if not skill_md.is_file():
            errors.append(f"{name}: missing SKILL.md")
            continue
        fm = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
        if fm is None:
            errors.append(f"{name}: SKILL.md has no valid '---' frontmatter block")
            continue
        if not fm.get("name"):
            errors.append(f"{name}: frontmatter missing 'name'")
        elif fm["name"] != name:
            errors.append(f"{name}: frontmatter name '{fm['name']}' != folder '{name}'")
        if not fm.get("description"):
            errors.append(f"{name}: frontmatter missing 'description'")

    if errors:
        print("Skill validation FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"OK: {len(skill_dirs)} skills validated")
    for d in skill_dirs:
        print(f"  - {d.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
