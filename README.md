<div align="center">

[![AI4S Skills — agent skills for AI for Science](assets/banner.webp)](https://github.com/ai4s-research/ai4s-skills)

**Open-source [Agent Skills](https://docs.claude.com/en/docs/claude-code/skills) for AI for Science** — turn a research direction or a concrete topic into topic exploration, literature surveys, runnable experiments, publication-grade papers & integrity audits, driven by any coding agent.

<p align="center"><b>English</b> · <a href="README.zh.md">中文</a></p>

<!--
Multilingual links via zdoc are temporarily disabled (service returned 402 Insufficient Balance).
Re-enable when zdoc is available again:
<p align="center">
  <a href="https://zdoc.app/de/ai4s-research/ai4s-skills">Deutsch</a> |
  <a href="https://zdoc.app/en/ai4s-research/ai4s-skills">English</a> |
  <a href="https://zdoc.app/es/ai4s-research/ai4s-skills">Español</a> |
  <a href="https://zdoc.app/fr/ai4s-research/ai4s-skills">français</a> |
  <a href="https://zdoc.app/ja/ai4s-research/ai4s-skills">日本語</a> |
  <a href="https://zdoc.app/ko/ai4s-research/ai4s-skills">한국어</a> |
  <a href="https://zdoc.app/pt/ai4s-research/ai4s-skills">Português</a> |
  <a href="https://zdoc.app/ru/ai4s-research/ai4s-skills">Русский</a> |
  <a href="https://zdoc.app/zh/ai4s-research/ai4s-skills">中文</a>
</p>
-->

<p>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/skills-7-success" alt="7 skills">
  <a href="http://makeapullrequest.com"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome"></a>
</p>

</div>

---

## What this is

`ai4s-skills` is a curated, maintained set of **agent skills** for the AI-for-Science
research workflow. Each skill is a self-contained operating manual (a `SKILL.md`
plus references, LaTeX templates, and deterministic helper tools) that a coding
agent — **Claude Code, Cursor, Codex, Aider, …** — loads and executes to produce
final-quality research artifacts.

**Design stance — skills, not a framework:**

- **Agent-driven.** The skill is the playbook; the calling agent does the work with
  its own `WebSearch` / `WebFetch` / `Edit` / `Bash`. No orchestrator to install.
- **No LLM SDK lock-in.** Skills never `import anthropic` / `import openai`. They
  are portable across agents and models.
- **Deterministic tools only.** Where code helps (image forensics, publication
  figures, mindmap rendering) it is small, single-purpose, dependency-light Python —
  called *by* the agent, never wrapping it.
- **Honest by construction.** Real citations (every BibTeX entry traceable to a
  fetched URL), real figures (vector PDF, no chartjunk), labelled numbers
  (measured / simulated / illustrative), and a permanent "human expert review
  recommended" attribution on every generated artifact.

## What makes it different

The "AI research agent" space is getting crowded. `ai4s-skills` is deliberately
narrow and opinionated:

- **The whole arc — including experiments _and_ an integrity audit.** Many suites
  stop at literature review and writing (some explicitly never run experiments).
  This one covers exploration → survey → runnable experiments → paper, and adds an
  **integrity-auditor** that forensically checks papers for image reuse, numerical
  anomalies, and logical gaps — authenticity as a first-class capability, not an
  afterthought.
- **Authenticity is the design axis, not a feature.** Every citation traces to a URL
  the agent actually fetched; every number is labelled `measured` / `simulated` /
  `illustrative` (simulated is never dressed up as measured); every run is
  incremental, persisted, and resumable, so "done" means done — not a fabricated
  finish. See [Authenticity by design](#authenticity-by-design).
- **Depth over breadth.** Seven skills, each shipping detailed operational
  references — bibliography-expansion discipline, publication-figure QA contracts,
  4-level evidence grading — not thin wrappers around an API.
- **No framework, no lock-in, MIT.** Pure markdown skills plus a few deterministic
  tools — no orchestrator, daemon, database, or LLM SDK to install. Portable across
  Claude Code, Cursor, Codex, and Aider, and free for commercial use.

## The 7 skills

| Skill | Role | Primary output |
|---|---|---|
| [**ai4s-agent**](skills/ai4s-agent/SKILL.md) | Meta-skill — chains the four downstream skills end to end | the full package below |
| [**research-explorer**](skills/research-explorer/SKILL.md) | Topic exploration from a broad direction | `research_exploration.md` · `topic_matrix.md` · `literature_pre_survey.md` |
| [**literature-survey**](skills/literature-survey/SKILL.md) | Comprehensive survey generation | 6–20 pp survey PDF + 60+ real citations + LaTeX source + taxonomy figures |
| [**experiment-suite**](skills/experiment-suite/SKILL.md) | Experiment package | design doc + runnable code + `results.json` (with provenance) + publication figures + report |
| [**paper-writer**](skills/paper-writer/SKILL.md) | Research paper | 8–14 pp paper PDF + 200+ citations + 4–8 figures + tables |
| [**mindmap-render**](skills/mindmap-render/SKILL.md) | Mindmap rendering | renders a `topic_matrix.md` into an image (ships a Python script) |
| [**integrity-auditor**](skills/integrity-auditor/SKILL.md) | Paper integrity audit | image / numerical / logical findings, 4-level evidence grading, `audit_report.md` + forensics tools |

### How they connect

```
direction
   │
   ▼
[1] research-explorer ──▶ you pick one concrete $TOPIC
   │
   ├──▶ [2] literature-survey   (survey PDF + bibliography.bib)
   ├──▶ [3] experiment-suite    (results.json + figures/)
   └──▶ [4] paper-writer        (reuses [2] bib + [3] results → paper PDF)

   integrity-auditor  ──▶ audits any paper (external PDF/DOI/arXiv, or [4]'s output)
```

`ai4s-agent` is the meta-skill that runs [1]→[4] in order. Skills hand off through a
deterministic **slug** + a simple `output/<skill>/<slug>/latest/...` path convention — no
code-level coupling.

## Quick start

### With Claude Code

Clone the repo, then run the installer **from the project** you want the skills in:

```bash
git clone https://github.com/ai4s-research/ai4s-skills

cd /path/to/your-project
/path/to/ai4s-skills/install.sh            # all skills → ./.claude/skills (this project)
# /path/to/ai4s-skills/install.sh paper-writer                 # or just specific ones
# SKILLS_DIR=~/.claude/skills /path/to/ai4s-skills/install.sh  # install globally instead
```

Then, in Claude Code:

> Use the literature-survey skill to write a survey on \<your topic\>.

Prefer to do it by hand? A skill is just a folder — copy any `skills/<name>/` into
`~/.claude/skills/` (global) or `<project>/.claude/skills/` (project-local).

### With Cursor / Codex / Aider / any coding agent

Point the agent at the skill's playbook and let it follow the steps:

```
Read skills/literature-survey/SKILL.md and its references/, then produce the survey
for "<your topic>" exactly as specified.
```

The skill tells the agent to read its `references/` before acting — the references
hold the disciplines (bibliography expansion, figure standards, layout rules,
quality gates) that make the output publication-grade.

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
├── tools/
│   └── validate_skills.py   structure/frontmatter validator (run in CI)
└── .github/workflows/ci.yml
```

Each `SKILL.md` carries YAML frontmatter (`name`, `description`) so agents can
discover and route to it.

## Deterministic tools included

These are plain, single-purpose helpers the agent calls — not a runtime:

- **`skills/integrity-auditor/forensics_tools/`** — image duplication / ORB matching,
  panel splitting, channel checks, Benford-style magnitude consistency, decimal
  matching, spreadsheet aggregate consistency.
- **`skills/experiment-suite/figure_examples/`** — a publication-style matplotlib
  kit (`style_kit.py`) + worked figure examples.
- **`skills/mindmap-render/scripts/`** — `generate_mindmap.py` to render mindmaps.

## Authenticity by design

Authenticity is enforced across every skill — it is the core of the project, not a
checkbox:

| Principle | What it means in practice |
|---|---|
| **Real citations** | Every BibTeX entry must trace to a URL the agent actually fetched this session — never from memory. |
| **Real numbers** | Every number is labelled `measured` / `simulated` / `illustrative`; simulated data is never presented as measured. |
| **Real experiments** | `experiment-suite` ships runnable code plus a `results.json` carrying provenance. Run it for real and measured results flow into the paper — the "simulated" disclosure drops automatically. |
| **Faithful records** | Long tasks run incrementally, persist progress, and resume where they stopped — "done" is real completion, not a fabricated finish. |
| **Real layout & figures** | `booktabs` tables, `[!t]` floats, `~\cite{}`; vector-PDF figures with embedded fonts and explicit palettes — no 3-D bars / pie / rainbow. |
| **Honest attribution** | Every generated artifact permanently carries a "human expert review strongly recommended" note. |
| **Auditable** | `integrity-auditor` turns these disciplines into a tool — checking any paper (yours or a third party's) for image / numerical / logical integrity issues, with graded evidence. |

## Contributing

New skills and tool improvements are welcome. A new skill needs:

1. `skills/<name>/SKILL.md` with `name` + `description` frontmatter (name = folder name).
2. Optional `references/`, `templates/`, and deterministic helper tools.
3. No `import anthropic` / `import openai` anywhere — skills stay agent- and model-agnostic.
4. `python tools/validate_skills.py` passing (CI runs it on every PR).

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

[MIT](LICENSE) — use freely, including commercially.

> **Disclaimer.** These skills generate research artifacts with the help of AI
> agents. Outputs are drafts: **review by a domain expert is strongly recommended**
> before any citation, submission, or decision. Always verify numbers, citations,
> and claims.
