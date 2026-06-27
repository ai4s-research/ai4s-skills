<div align="center">

# AI4S Skills

**Open-source [Agent Skills](https://docs.claude.com/en/docs/claude-code/skills) for AI for Science.**

Turn a research direction or a concrete topic into a full research package —
topic exploration, literature survey, runnable experiments, a publication-grade
paper, and an integrity audit — driven by any coding agent.

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

## The 7 skills

| Skill | Role | Primary output |
|---|---|---|
| [**ai4s-agent**](skills/ai4s-agent) | Meta-skill — chains the four downstream skills end to end | the full package below |
| [**research-explorer**](skills/research-explorer) | Topic exploration from a broad direction | `research_exploration.md` · `topic_matrix.md` · `literature_pre_survey.md` |
| [**literature-survey**](skills/literature-survey) | Comprehensive survey generation | 6–20 pp survey PDF + 60+ real citations + LaTeX source + taxonomy figures |
| [**experiment-suite**](skills/experiment-suite) | Experiment package | design doc + runnable code + `results.json` (with provenance) + publication figures + report |
| [**paper-writer**](skills/paper-writer) | Research paper | 8–14 pp paper PDF + 200+ citations + 4–8 figures + tables |
| [**mindmap-render**](skills/mindmap-render) | Mindmap rendering | renders a `topic_matrix.md` into an image (ships a Python script) |
| [**integrity-auditor**](skills/integrity-auditor) | Paper integrity audit | image / numerical / logical findings, 4-level evidence grading, `audit_report.md` + forensics tools |

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
deterministic **slug** + a simple `output/<slug>/latest/...` path convention — no
code-level coupling.

## Quick start

### With Claude Code

Copy a skill into your project (or your global skills dir) and ask for it:

```bash
# project-local
mkdir -p .claude/skills
cp -R path/to/ai4s-skills/skills/literature-survey .claude/skills/

# then, in Claude Code:
#   "Use the literature-survey skill to write a survey on <your topic>."
```

Or drop the whole set into `~/.claude/skills/` to make all seven available everywhere.

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

## Quality discipline (applies to every skill)

| Principle | Requirement |
|---|---|
| Real citations | Every BibTeX entry must trace to a URL the agent actually fetched — no citations from memory |
| Real layout | `booktabs` tables, floats placed with `[!t]`, `~\cite{}` |
| Real figures | Vector PDF, embedded fonts, explicit palettes — no 3-D bars / pie / rainbow |
| Honest numbers | Every number labelled `measured` / `simulated` / `illustrative` |
| Honest attribution | Generated artifacts carry a permanent "human expert review strongly recommended" note |

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
