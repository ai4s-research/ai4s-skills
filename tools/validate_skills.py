#!/usr/bin/env python3
"""Validate the structure and publication guardrails of skills under skills/.

Dependency-free. For each skills/<name>/ it checks:
  - SKILL.md exists
  - SKILL.md begins with a YAML frontmatter block (--- ... ---)
  - frontmatter defines non-empty `name` and `description`
  - `name` equals the folder name
  - paper, survey, and experiment skills share required publication guardrails

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


def validate_publication_guardrails(errors: list[str]) -> None:
    """Lock cross-skill publication rules that must not drift apart."""

    def read(relative: str) -> str:
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"{relative}: required validation target is missing")
            return ""
        return path.read_text(encoding="utf-8")

    def require(relative: str, needle: str, rule: str) -> None:
        if needle not in read(relative):
            errors.append(f"{relative}: missing publication guardrail: {rule}")

    def forbid(relative: str, needle: str, rule: str) -> None:
        if needle in read(relative):
            errors.append(f"{relative}: forbidden publication rule: {rule}")

    require(
        "skills/ai4s-agent/SKILL.md",
        "Re-runs the paper-writer freshness gate",
        "preserve bibliography freshness across the pipeline",
    )

    paper_figures = "skills/paper-writer/references/02-figures-publication-grade.md"
    paper_skill = "skills/paper-writer/SKILL.md"
    paper_layout = "skills/paper-writer/references/04-layout-discipline.md"
    paper_gate = "skills/paper-writer/references/05-quality-gate.md"
    paper_template = "skills/paper-writer/templates/paper/main.tex"
    paper_compile = "skills/paper-writer/templates/paper/compile.sh"
    paper_freshness = (
        "skills/paper-writer/templates/paper/check_bibliography_freshness.py"
    )
    require(paper_figures, "Do not deliver Mermaid, PlantUML", "reject generic diagram DSL output")
    require(paper_figures, "4–8 justified figures", "choose figures by evidence")
    forbid(paper_figures, "xtick.labelsize\": 6.5", "figure text below the 7 pt floor")
    forbid(paper_figures, "At least 1 architecture diagram", "mandatory architecture filler")
    require(paper_skill, "numbers from 1 in first-appearance order", "automatic sequential numbering")
    forbid(paper_skill, r"\begin{figure}[!t]", "one forced placement for every figure")
    forbid(paper_skill, r"\begin{table}[!t]", "one forced placement for every table")
    require(
        "skills/paper-writer/references/03-section-playbook.md",
        "Symbol rule (mandatory)",
        "define new equation symbols at first use",
    )
    require(
        "skills/paper-writer/references/03-section-playbook.md",
        "Citations:** 0 by default",
        "keep abstracts self-contained by default",
    )
    require(paper_layout, "Exactly two sizes are allowed", "uniform table type scale")
    require(paper_layout, "Narrative ownership comes first", "claim-led float placement")
    require(paper_layout, "Automatic numbering only", "automatic object numbering")
    require(paper_gate, "G1.2 · Citation and counter order", "hard numbering-order check")
    require(paper_gate, "G1.5 · Final-size visual integrity", "hard final-page inspection")
    require(paper_gate, "G2.6 · Temporal coverage", "hard bibliography freshness check")
    require(paper_template, r"\bibliographystyle{unsrtnat}", "first-citation bibliography order")
    require(paper_template, r"\usepackage{placeins}", "optional semantic float barriers")
    forbid(paper_template, r"\bibliographystyle{plainnat}", "alphabetic-looking citation numbering")
    require(paper_compile, "rm -f main.aux", "discard stale numbering state")
    forbid(paper_compile, "|| true", "do not hide LaTeX or BibTeX failures")
    require(paper_freshness, '"fast-moving": 60.0', "60% fast-field three-year floor")
    require(paper_freshness, '"recency-led": 70.0', "70% explicit-window floor")
    require(paper_freshness, '"balanced": 40.0', "40% balanced-field three-year floor")

    survey_skill = "skills/literature-survey/SKILL.md"
    survey_figures = "skills/literature-survey/references/02-survey-figures.md"
    survey_layout = "skills/literature-survey/references/04-layout-discipline.md"
    survey_gate = "skills/literature-survey/references/05-quality-gate.md"
    survey_template = "skills/literature-survey/templates/survey/main.tex"
    survey_compile = "skills/literature-survey/templates/survey/compile.sh"
    survey_freshness = (
        "skills/literature-survey/templates/survey/check_bibliography_freshness.py"
    )
    require(survey_skill, "Never force a family to fill a slot", "no mandatory survey figure family")
    require(survey_skill, "numbers from 1 in first-appearance order", "automatic sequential numbering")
    forbid(survey_skill, r"\begin{figure}[!t]", "one forced placement for every figure")
    forbid(survey_skill, r"\begin{table}[!t]", "one forced placement for every table")
    require(survey_figures, "Do not deliver Mermaid, PlantUML", "reject generic diagram DSL output")
    forbid(survey_figures, "xtick.labelsize\":6.5", "figure text below the 7 pt floor")
    forbid(survey_figures, r"\caption{\textbf{Figure 1.}", "manual figure number inside caption")
    require(
        "skills/literature-survey/references/03-survey-section-playbook.md",
        "Define each\n  symbol once at first use",
        "define new equation symbols at first use",
    )
    require(
        "skills/literature-survey/references/03-survey-section-playbook.md",
        "Citations:** 0 by default",
        "keep abstracts self-contained by default",
    )
    require(survey_layout, "Narrative ownership comes first", "claim-led float placement")
    require(survey_layout, "Automatic numbering only", "automatic object numbering")
    require(survey_gate, "optional families, not required slots", "remove mandatory figure trio")
    require(survey_gate, "G1.2 · Citation and counter order", "hard numbering-order check")
    require(survey_gate, "G1.5 · Final-size visual integrity", "hard final-page inspection")
    require(survey_gate, "G2.6 · Temporal coverage", "hard bibliography freshness check")
    require(survey_template, r"\bibliographystyle{unsrtnat}", "first-citation bibliography order")
    require(survey_template, r"\usepackage{placeins}", "optional semantic float barriers")
    forbid(survey_template, r"\bibliographystyle{plainnat}", "alphabetic-looking citation numbering")
    require(survey_compile, "rm -f main.aux", "discard stale numbering state")
    forbid(survey_compile, "|| true", "do not hide LaTeX or BibTeX failures")
    require(survey_freshness, '"fast-moving": 60.0', "60% fast-field three-year floor")
    require(survey_freshness, '"recency-led": 70.0', "70% explicit-window floor")
    require(survey_freshness, '"balanced": 40.0', "40% balanced-field three-year floor")
    if read(paper_freshness) != read(survey_freshness):
        errors.append(
            "paper/survey freshness checkers differ; keep installed skills deterministic"
        )

    experiment_figures = "skills/experiment-suite/references/04-publication-figures.md"
    experiment_qa = "skills/experiment-suite/references/04b-figure-qa.md"
    experiment_gate = "skills/experiment-suite/references/06-quality-gate.md"
    style_kit = "skills/experiment-suite/figure_examples/style_kit.py"
    require(experiment_figures, '"font.family": "sans-serif"', "shared sans-serif paper style")
    forbid(experiment_figures, '"font.family": "serif"', "style conflict with downstream papers")
    require(experiment_figures, "WONG =", "shared colour-blind-safe palette")
    require(experiment_qa, "pdftoppm", "rendered figure inspection")
    require(experiment_qa, "Mermaid, PlantUML", "reject generic diagram DSL output")
    require(experiment_gate, "This hard gate fails", "make final-size inspection mandatory")
    require(style_kit, "font_size: int = 8", "readable 8 pt experiment default")
    require(
        "skills/experiment-suite/references/05-report-structure.md",
        "Define each symbol once at first use",
        "define new equation symbols at first use",
    )


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

    validate_publication_guardrails(errors)

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
