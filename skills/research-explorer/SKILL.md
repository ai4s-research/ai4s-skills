---
name: research-explorer
description: Use when the user has a vague research direction and wants to explore feasible specific topics. Outputs a structured analysis with candidate topics, innovation/feasibility scoring, and a pre-survey of 20–30 representative works. Single-stage, no Python runtime.
---

# Research Explorer

## Overview

Research-topic exploration SKILL. Takes a broad direction, performs multi-dimensional web research with the agent's own WebSearch / WebFetch tools, and produces three structured Markdown deliverables. **Single stage, full quality from the start.** No Python runtime, no LLM SDK.

## When to Use

- User says "I want to research X" / "我对 X 感兴趣" without a specific topic.
- User wants to know "what are the hot topics in X".
- User needs help narrowing a broad field into 5–10 candidate topics.
- User asks for "research landscape overview" / "选题分析".

## When NOT to Use

- User already has a specific research question → use `literature-survey` or `paper-writer`.
- User wants a quick fact-check → use WebSearch directly.

## Workflow

### Step 1 — Understand the direction

Confirm with the user:

- **Direction** — the broad area of interest (e.g., "federated learning", "NLP for healthcare").
- **Constraints** — theory vs. applied, specific methods, target venue, compute budget, time horizon.
- **Language** — default Chinese in conversation; reports in Chinese unless the user requests otherwise.

### Step 2 — Set up the run directory

```bash
DIRECTION="<direction>"
SLUG=$(python3 -c "import re,hashlib,sys; t=sys.argv[1]; n=re.sub(r'[\\s_]+','-',re.sub(r'[^\\w\\s-]','',t.lower().strip())).strip('-')[:40].rstrip('-'); h=hashlib.sha1(t.encode()).hexdigest()[:8]; print(f'{n}-{h}')" "$DIRECTION")
TS=$(date +%Y-%m-%d_%H%M%S)
RUN=output/cap-research-explorer/$SLUG/$TS

mkdir -p "$RUN"
ln -sfn "$TS" "output/cap-research-explorer/$SLUG/latest"
```

In commands below `$RUN` = `output/cap-research-explorer/<slug>/latest`.

### Step 3 — Multi-dimensional exploration

Run **WebSearch** across the following dimensions (one query per dimension, more if returns are thin):

1. **Hot topics** — "<direction> 2024 2025 hot topics" / "recent advances".
2. **Open problems** — "<direction> open problems" / "challenges".
3. **Surveys** — "<direction> survey 2024" / "<direction> review".
4. **Benchmarks** — "<direction> benchmark" / "<direction> evaluation dataset".
5. **Applications** — "<direction> applications" / "<direction> industry use cases".
6. **Cross-field** — "<direction> + <adjacent field>" (pick 1–2 adjacent fields).
7. **Recent breakthroughs** — papers from the last 6–12 months at top venues.

For each kept candidate, **WebFetch** the abstract URL to extract canonical title / authors / year / venue. Persist intermediate notes to `$RUN/search_notes.md` after every dimension so the work resumes cleanly.

### Step 4 — Produce the three deliverables

Write these in `$RUN/`:

#### 4.1 `research_exploration.md`

Structured analysis containing:

- **Direction recap & constraints**.
- **Landscape map** — main subfields and the relationships between them.
- **5–10 candidate topics**, each with:
  - Title (specific enough to be a paper title).
  - Motivation (why this matters now).
  - Innovation angle (what would be new).
  - Feasibility score (low / medium / high) with a brief justification (data availability, compute requirements, prior work density).
  - Risk / open question.
- **Recommendation** — which 1–3 the user should pursue and why.

#### 4.2 `topic_matrix.md`

A hierarchical Markdown outline of the topic space:

```
# <Direction>
## Subfield A
### Topic A.1
### Topic A.2
## Subfield B
### Topic B.1
```

This file is consumable by `cap-mindmap-render` to produce a visual mindmap.

#### 4.3 `literature_pre_survey.md`

A pre-survey table of **20–30 representative works** discovered above, with columns: title, authors, year, venue, URL, one-sentence relevance note. Every entry must have a URL the agent fetched in this session.

### Step 5 — Optional handoff

If the user picks a topic, suggest the next cap:

- For a paper: `cap-paper-writer` (using the chosen topic).
- For a survey: `cap-literature-survey`.
- For an experiment package: `cap-experiment-suite`.
- For a visual topic map: `cap-mindmap-render` consuming `topic_matrix.md`.

## Cross-cap data flow (path convention)

A downstream cap can locate this exploration via the slug:

- `output/cap-research-explorer/<slug>/latest/topic_matrix.md`
- `output/cap-research-explorer/<slug>/latest/literature_pre_survey.md`

If the user picks one topic from the matrix, downstream caps compute their own slug from the **topic** (not the original direction), so the slug paths diverge from this cap onward — which is correct.

## Important rules

- **No LLM SDK in this cap.** Just a procedure + this SKILL.md.
- **Candidates are suggestions, not guaranteed novel** — the user must verify originality before committing.
- **Feasibility scores are heuristic** — flag uncertainty explicitly when relevant.
- Every literature entry must have a URL fetched in this session; no memory-only entries.
