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

import re
import sys
from pathlib import Path

NAME_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
MAX_NAME = 64
MAX_DESCRIPTION = 1024

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
        nm = fm.get("name", "")
        desc = fm.get("description", "")
        if not nm:
            errors.append(f"{name}: frontmatter missing 'name'")
        else:
            if nm != name:
                errors.append(f"{name}: frontmatter name '{nm}' != folder '{name}'")
            if not NAME_RE.fullmatch(nm):
                errors.append(f"{name}: name '{nm}' must be lowercase letters, numbers, and hyphens")
            if len(nm) > MAX_NAME:
                errors.append(f"{name}: name exceeds {MAX_NAME} chars (is {len(nm)})")
        if not desc:
            errors.append(f"{name}: frontmatter missing 'description'")
        elif len(desc) > MAX_DESCRIPTION:
            errors.append(f"{name}: description exceeds {MAX_DESCRIPTION} chars (is {len(desc)})")

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
