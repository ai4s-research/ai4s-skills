---
name: ai4s-agent
description: Use when the user wants an end-to-end AI4S research pipeline — broad direction or specific topic in, full research package out (exploration + literature survey + experiment + paper). Meta-SKILL that chains the four downstream caps in order. Pure markdown — no Python runtime.
---

# AI4S Agent (meta-SKILL)

## Overview

Top-level entry point for the AI4S research stack. This SKILL contains **no work of its own** — its only job is to call four downstream SKILLs in the right order, with the right slug, and reuse intermediate artefacts by path convention.

```
direction → research-explorer → topic
topic     → literature-survey  (60+ real bib, 100+ recommended)
topic     → experiment-suite   (design + code + results + figures)
topic     → paper-writer       (assembles into 200+ cite PDF)
```

Each downstream cap is **already single-stage and self-sufficient**: its agent loads that cap's SKILL.md and produces the full final-quality artefact directly. There is no skeleton/enrichment split. This meta-SKILL only handles ordering, the path convention, and disclosure consistency.

## When to Use

- User asks for "a paper on X" or "research package on X" and wants the whole stack run end-to-end.
- User wants to compare what each cap produces — useful for development/debugging the pipeline itself.

## When NOT to Use

- User wants to enrich only one stage (e.g., only the literature survey) → invoke that cap's SKILL directly.
- User wants only topic exploration → invoke `research-explorer` directly.

## The slug contract

Every cap computes the same slug from the same topic string:

```python
import re, hashlib
def slug(t):
    n = re.sub(r'[\s_]+', '-', re.sub(r'[^\w\s-]', '', t.lower().strip())).strip('-')[:40].rstrip('-')
    h = hashlib.sha1(t.encode()).hexdigest()[:8]
    return f"{n}-{h}"
```

Use the **same string** across all four caps. If the user provides a direction (not a topic), `research-explorer` runs against the direction; once a topic is chosen, the topic becomes the slug input for the remaining three.

## Workflow

> **Planner-driven mode:** If this agent is invoked in `planner-driven`
> mode (Vela `agents.mode = 'planner-driven'`), follow the contract in
> [`references/plan-json-protocol.md`](references/plan-json-protocol.md).
> The planner writes `.vela/plan.json` and exits without doing the actual
> research work; subsequent steps execute the plan.

### Step 1 — Understand the user's starting point

- **Direction** ("transformer time series forecasting") — start at `research-explorer`, pick a topic from its `research_exploration.md`, then proceed.
- **Topic** ("Transformer-based long-horizon forecasting with patch tokenisation") — skip `research-explorer`; go straight to the parallel branch (lit-survey, experiment-suite, paper-writer).
- **Real measured experiment data?** If yes, the user supplies a `results.json` path; experiment-suite loads it instead of writing a simulated one; the paper's `\thanks` drops the simulated clause.

### Step 2 — Explore (only if input was a direction)

Load `cap-research-explorer/.claude/skills/research-explorer/SKILL.md`. Follow its 5 steps to produce:

```
output/cap-research-explorer/<dir_slug>/latest/{research_exploration.md, topic_matrix.md, literature_pre_survey.md}
```

Discuss the candidate topics with the user. They pick one specific topic; that string becomes `$TOPIC` for the rest.

### Step 3 — Literature survey

Load `cap-literature-survey/.claude/skills/literature-survey/SKILL.md` with `$TOPIC`. It produces:

```
output/cap-literature-survey/<topic_slug>/latest/survey_paper/
├── main.pdf                    # the 6–20 page survey
├── main.tex
├── bibliography.bib            # 60+ real entries, 100+ recommended (URL-anchored)
├── sections/, figures/
output/cap-literature-survey/<topic_slug>/latest/literature_table.md
```

### Step 4 — Experiment package

Load `cap-experiment-suite/.claude/skills/experiment-suite/SKILL.md` with `$TOPIC`. It produces:

```
output/cap-experiment-suite/<topic_slug>/latest/
├── experiment_design.md
├── experiment/                  # runnable model.py / data.py / train.py / evaluate.py
├── results.json                 # with "simulated" + "provenance"
├── figures/                     # publication-grade + manifest.json (basenames only)
└── experiment_report.md
```

If `--real-results-path` was provided in Step 1, the agent loads it here and `results.json` is flagged `"simulated": false`.

### Step 5 — Paper

Load `cap-paper-writer/.claude/skills/paper-writer/SKILL.md` with `$TOPIC`. Paper-writer's cross-cap conventions automatically pick up Steps 3 and 4:

- Seeds `bibliography.bib` from `output/cap-literature-survey/<topic_slug>/latest/survey_paper/bibliography.bib`, then expands it to 200+ inside paper-writer if needed.
- Reads numbers and provenance from `output/cap-experiment-suite/<topic_slug>/latest/results.json`.
- Copies/symlinks the publication-grade figures from `output/cap-experiment-suite/<topic_slug>/latest/figures/`.

It produces:

```
output/cap-paper-writer/<topic_slug>/latest/paper/
├── main.pdf                    # 8–14 pages, 200+ cites
├── main.tex
├── bibliography.bib
├── sections/, figures/
```

### Step 6 — Deliver

Report the four output roots to the user:

1. `output/cap-research-explorer/<dir_slug>/latest/` (if exploration ran)
2. `output/cap-literature-survey/<topic_slug>/latest/`
3. `output/cap-experiment-suite/<topic_slug>/latest/`
4. `output/cap-paper-writer/<topic_slug>/latest/`

Plus the paper-writer stats per its `references/05-quality-gate.md` report format.

## Disclosure consistency

The same `simulated` flag must drive disclosure across all four artefacts:

- `cap-experiment-suite/.../results.json` → `"simulated": true|false` is the source of truth.
- `cap-experiment-suite/.../experiment_report.md` top-of-page disclosure must match.
- `cap-paper-writer/.../main.tex` `\author{AI4S Agent\thanks{…}}` must include the simulated clause iff `results.json` has `"simulated": true`.
- The always-on **human-review clause** is mandatory in every case.

## Rules

- **No LLM SDK in any cap, including this one.** Pure markdown — `.claude/skills/ai4s-agent/SKILL.md` and `README.md` only.
- **One slug per topic, computed identically across caps.** The contract above is non-negotiable.
- **Never collapse the four caps into one agent run.** Each cap's SKILL is the single source of truth for what counts as "done" for its artefact.
- A non-interactive runner (e.g., `claude --print` headless) lives **outside** the cap-* ecosystem. The caps stay pure.
