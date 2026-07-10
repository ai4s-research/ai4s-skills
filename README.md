<div align="center">

[![AI4S Skills — agent skills for AI for Science](assets/banner.webp)](https://github.com/ai4s-research/ai4s-skills)

Seven agent skills for AI-for-Science research — turn a research direction into
literature surveys, runnable experiments, publication-grade papers, and integrity
audits, with every citation, number, and figure traceable to its source.

<p align="center"><b>English</b> · <a href="README.zh.md">中文</a></p>

<p>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT"></a>
  <a href="https://doi.org/10.5281/zenodo.21297455"><img src="https://zenodo.org/badge/DOI/10.5281/zenodo.21297455.svg" alt="DOI"></a>
  <img src="https://img.shields.io/badge/skills-7-success" alt="7 skills">
  <a href="http://makeapullrequest.com"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome"></a>
  <a href="https://linux.do"><img src="https://img.shields.io/badge/Join-linux.do-orange" alt="linux.do"></a>
</p>

</div>

---

## Contents

- [🧩 The skills](#the-skills)
- [🔗 How they connect](#how-they-connect)
- [✅ Authenticity](#authenticity)
- [🔬 Example](#example)
- [📦 Install](#install)
- [🚀 Usage](#usage)
- [🗂️ Repository layout](#repository-layout)
- [🛠️ Included tools](#included-tools)
- [🤝 Contributing](#contributing)
- [⚖️ License](#license)
- [🙏 Acknowledgments](#acknowledgments)

## The skills

| Skill | Role | Primary output |
|---|---|---|
| [ai4s-agent](skills/ai4s-agent/SKILL.md) | Runs the four skills below in order | the full package |
| [research-explorer](skills/research-explorer/SKILL.md) | Explore topics from a broad direction | `research_exploration.md`, `topic_matrix.md`, `literature_pre_survey.md` |
| [literature-survey](skills/literature-survey/SKILL.md) | Write a literature survey | 6–20 pp PDF, 60+ real citations, LaTeX source, taxonomy figures |
| [experiment-suite](skills/experiment-suite/SKILL.md) | Build an experiment package | design doc, runnable code, `results.json` with provenance, figures, report |
| [paper-writer](skills/paper-writer/SKILL.md) | Write a research paper | 8–14 pp PDF, 200+ citations, 4–8 figures, tables |
| [mindmap-render](skills/mindmap-render/SKILL.md) | Render a mindmap | image from a `topic_matrix.md` (Python script) |
| [integrity-auditor](skills/integrity-auditor/SKILL.md) | Audit a paper's integrity | image / numerical / logical findings, 4-level evidence grading, `audit_report.md` |

Each skill is a folder with a `SKILL.md` plus its own references, templates, and
tools. MIT-licensed; works with Claude Code, Cursor, Codex, and Aider.

## How they connect

```
direction
   │
   ▼
[1] research-explorer ──▶ pick one $TOPIC
   │
   ├──▶ [2] literature-survey   → survey PDF + bibliography.bib
   ├──▶ [3] experiment-suite    → results.json + figures/
   └──▶ [4] paper-writer        → paper PDF  (reuses [2] and [3])

integrity-auditor ──▶ audits any paper: external PDF / DOI / arXiv, or [4]'s output
```

`ai4s-agent` runs steps 1–4 in order. Skills pass work to each other through a
shared slug and the path `output/<skill>/<slug>/latest/`.

## Authenticity

The focus of the project. Every skill enforces:

| Principle | In practice |
|---|---|
| **Real citations** | Every BibTeX entry links to a URL the agent fetched in the same session; none from memory. |
| **Labelled numbers** | Every number is marked `measured`, `simulated`, or `illustrative`; simulated values are never reported as measured. |
| **Runnable experiments** | `experiment-suite` outputs runnable code and a `results.json` with provenance. Supply real results and they replace the simulated ones; the "simulated" disclosure is then removed. |
| **Resumable runs** | Long tasks save progress after each step and continue from the last checkpoint, so a reported "done" reflects completed work. |
| **Publication layout** | booktabs tables, `[!t]` floats, `~\cite{}`; vector-PDF figures with embedded fonts and defined color palettes. |
| **Review disclosure** | Every generated document states that domain-expert review is recommended. |
| **Integrity checks** | `integrity-auditor` inspects a paper for image, numerical, and logical problems and grades the evidence. |

## Example

A complete run from `experiment-suite` + `paper-writer`: **"Learning the Burgers
Solution Operator with a Fourier Neural Operator"** — an 8-page paper backed by code
the agent wrote and ran. Full artifact in [`examples/fno-burgers/`](examples/fno-burgers/)
(paper, code, `results.json`, report).

<div align="center">
<table>
<tr>
<td><a href="examples/fno-burgers/paper.pdf"><img src="assets/paper/page-1.webp" width="230" alt="paper page 1"></a></td>
<td><a href="examples/fno-burgers/paper.pdf"><img src="assets/paper/page-2.webp" width="230" alt="paper page 2"></a></td>
<td><a href="examples/fno-burgers/paper.pdf"><img src="assets/paper/page-3.webp" width="230" alt="paper page 3"></a></td>
</tr>
<tr>
<td><a href="examples/fno-burgers/paper.pdf"><img src="assets/paper/page-4.webp" width="230" alt="paper page 4"></a></td>
<td><a href="examples/fno-burgers/paper.pdf"><img src="assets/paper/page-5.webp" width="230" alt="paper page 5"></a></td>
<td><a href="examples/fno-burgers/paper.pdf"><img src="assets/paper/page-6.webp" width="230" alt="paper page 6"></a></td>
</tr>
</table>
<sub><i>The 8-page paper (first 6 pages) — click any page for the full PDF.</i></sub>
</div>

- **Real code, really run** — `model.py` is a 1-D FNO; the full study runs in ~35 min on a laptop CPU.
- **Measured results** — FNO 4.41% rel-L2 vs MLP 21.63% and CNN 67.69% (3 seeds); zero-shot super-resolution holds 4.2–4.7% from grid 128 to 1024.
- **Real citations** — 22 references, each traceable to its source.

Every number is `measured` (provenance in `results.json`); the paper states it was
AI-generated and recommends domain-expert review.

## Install

Run the installer from the project you want the skills in:

```bash
git clone https://github.com/ai4s-research/ai4s-skills

cd /path/to/your-project
/path/to/ai4s-skills/install.sh                              # all skills → ./.claude/skills
/path/to/ai4s-skills/install.sh paper-writer                 # or specific ones
SKILLS_DIR=~/.claude/skills /path/to/ai4s-skills/install.sh  # global instead
```

To install by hand, copy any `skills/<name>/` into `~/.claude/skills/` (global) or
`<project>/.claude/skills/` (project).

## Usage

In Claude Code:

> Use the literature-survey skill to write a survey on \<your topic\>.

With Cursor, Codex, or Aider, point the agent at the skill file:

```
Read skills/literature-survey/SKILL.md and its references/, then produce the survey
for "<your topic>" as specified.
```

Each `SKILL.md` directs the agent to read its `references/` first; those files hold
the procedures for bibliography expansion, figures, layout, and quality checks.

## Repository layout

```
ai4s-skills/
├── skills/
│   ├── ai4s-agent/          SKILL.md + references/
│   ├── research-explorer/   SKILL.md
│   ├── literature-survey/   SKILL.md + references/ + templates/survey/
│   ├── experiment-suite/    SKILL.md + references/ + figure_examples/
│   ├── paper-writer/        SKILL.md + references/ + templates/paper/
│   ├── mindmap-render/      SKILL.md + scripts/ + tests/
│   └── integrity-auditor/   SKILL.md + references/ + forensics_tools/ + templates/ + tests/
├── tools/validate_skills.py   structure / frontmatter validator (run in CI)
├── install.sh
└── .github/workflows/ci.yml
```

Each `SKILL.md` carries YAML frontmatter (`name`, `description`) so an agent can
find and route to it.

## Included tools

Small, single-purpose scripts the skills call. Each directory has its own
`requirements.txt`.

- `skills/integrity-auditor/forensics_tools/` — image duplication / ORB matching, panel splitting, channel checks, magnitude (Benford-style) consistency, decimal matching, spreadsheet aggregate consistency.
- `skills/experiment-suite/figure_examples/` — a matplotlib style kit (`style_kit.py`) and worked figure examples.
- `skills/mindmap-render/scripts/` — `generate_mindmap.py`.

## Contributing

A new skill needs:

1. `skills/<name>/SKILL.md` with `name` and `description` frontmatter (`name` = folder name).
2. Optional `references/`, `templates/`, and tools.
3. No `import anthropic` / `import openai`.
4. `python tools/validate_skills.py` passing (CI runs it on every PR).

See [CONTRIBUTING.md](CONTRIBUTING.md) and the [Code of Conduct](CODE_OF_CONDUCT.md).

## License

[MIT](LICENSE).

> Outputs are drafts. Review by a domain expert is recommended before any citation,
> submission, or decision. Verify numbers, citations, and claims.

## Acknowledgments

Thanks to [linux.do](https://linux.do) — a vibrant tech community where this project is shared and discussed.
