# Quality Gate — Self-Check Before Delivery

## Why this exists

Even a thorough first pass produces a paper with one or two issues — citations that don't resolve, a figure that's too small, a table caption that's a fragment. This reference is the checklist you run **after** drafting and recompiling, **before** telling the user "it's done". If any item fails, return to the relevant reference and fix.

The gate is bright-line. Do not soften the targets to ship.

## Hard gates (must pass)

### G1 · PDF compiles cleanly

```bash
cd output/paper-writer/<slug>/latest/paper
pdflatex -interaction=nonstopmode main.tex >/dev/null 2>&1
bibtex main >/dev/null 2>&1
pdflatex -interaction=nonstopmode main.tex >/dev/null 2>&1
pdflatex -interaction=nonstopmode main.tex >/dev/null 2>&1

# Must have output and be non-trivial
test -s main.pdf || echo "FAIL: main.pdf missing or empty"

# Zero undefined citations
grep -c "Citation .* undefined" main.log    # must be 0

# Zero undefined references (\ref resolution)
grep -c "Reference .* undefined" main.log   # must be 0

# Overfull boxes = content crossing the margin. List the worst, then drive to 0.
grep "Overfull \\\\hbox" main.log | grep -oE '\([0-9.]+pt too wide\)' | sort -t'(' -k2 -rn | head
grep -c "Overfull \\\\hbox" main.log        # target 0 (a stray ≤2pt microtype box is fine)
```

If any of these fail, fix the underlying issue, recompile, recheck. Overfull is a **remediation loop, not a tolerated warning** (unattended runs have no human to spot the spill): a figure/table overrun means it wasn't wrapped per `02`/`04` — wrap TikZ in `\resizebox{\linewidth}{!}{…}`, add `width=\linewidth` to includes, shrink/`tabularx` the table; a long unbreakable token needs `\sloppy`/`\url{}`/a manual break. Recompile until the count is 0.

### G2 · Bibliography size

```bash
grep -c "^@" bibliography.bib    # must be ≥ 200
```

If under 200, return to `01-bibliography-expansion.md` and run more WebSearch queries.

No `unknown` keys in the bib:

```bash
grep -E "^@.+\{unknown" bibliography.bib   # must be empty
```

### G2.5 · No orphan bib entries

A bib that contains entries never `\cite{}`-d in the prose is **padding**.
Common failure mode is reaching G2's count by appending famous papers from
adjacent fields (LLM, vision, foundational deep learning, …) that the
paper never uses. This gate detects orphans; **detection is not
termination — it triggers remediation**.

```bash
# every key in bibliography.bib must appear in at least one \cite, \citep,
# \citet, etc. in main.tex or sections/*.tex
bib_keys=$(grep -oE '^@[a-z]+\{[^,]+,' bibliography.bib \
           | sed -E 's/^@[a-z]+\{//; s/,$//' | sort -u)
cite_keys=$(grep -hoE '\\cite[a-z]*\{[^}]+\}' main.tex sections/*.tex 2>/dev/null \
            | grep -oE '\{[^}]+\}' | tr ',' '\n' | tr -d '{} \n' \
            | sort -u | sed '/^$/d')
orphans=$(comm -23 <(echo "$bib_keys") <(echo "$cite_keys"))
orphan_count=$(echo "$orphans" | grep -c .)
echo "orphan bib entries: $orphan_count (must be 0)"
test "$orphan_count" -eq 0 || {
  echo "ACTION REQUIRED · $orphan_count orphans (first 10):"
  echo "$orphans" | head -10
}
```

**This is a remediation trigger, not a task-failure signal.** If
`orphan_count > 0`, DO NOT exit the step or report failure. Loop on
remediation until orphans reach 0, in this priority order:

1. **Cite them in prose** (preferred). Most orphans are real on-topic
   papers you researched but skipped writing about. Extend Related Work
   and Methods to discuss each. Use `03-section-playbook.md` for
   citation-density targets per section. Re-run the gate.
2. **Prune + lower scope.** If after honest effort you cannot extend the
   prose to cover the orphans, re-classify as a workshop paper (≥ 60
   cites; see G3 note) and prune the bib to entries you actually cite.
   Update the abstract to match. Re-run the gate.
3. **Prune + honest shortfall report.** If even the workshop target
   cannot be honestly reached, prune to the cited entries and add a
   sentence to the abstract / introduction noting the literature scope.
   Then re-run the gate. Never quietly pad with famous but off-topic
   papers — a smaller honest bib is acceptable output.

Only after `orphan_count == 0` may you proceed past this gate.

### G3 · Page count

```bash
pdfinfo main.pdf | grep Pages    # must be ≥ 8 for a research paper
```

For survey-length: ≥ 12. For workshop-length: ≥ 4 (relax G2 to 60 in this case; document the exception).

### G4 · Cite count across sections

```bash
total=0
for f in sections/*.tex; do
  c=$(grep -o "\\\\cite{" "$f" | wc -l)
  total=$((total + c))
done
echo "TOTAL \\cite{}: $total"     # must be ≥ 60
```

Distribution check (`grep -o` per section file): no section should have zero citations except possibly Method (which can be 4–8). Aim:

| Section | Min `\cite{` count |
|---|---|
| abstract | 4 |
| introduction | 12 |
| related_work | 30 |
| method | 4 |
| experiment | 5 |
| results | 5 |
| conclusion | 4 |

### G5 · Figures and tables in Results

```bash
grep -c "begin{figure" sections/results.tex     # must be ≥ 1
grep -c "begin{table" sections/results.tex      # must be ≥ 1
```

Plus, somewhere in the paper:

```bash
grep -rc "begin{figure" sections/ | awk -F: '{s+=$2} END {print s}'   # must be ≥ 3 (incl. method/architecture)
grep -rc "begin{table"  sections/ | awk -F: '{s+=$2} END {print s}'   # must be ≥ 2 (main + ablation)
```

### G6 · Numbered equations in Method

```bash
grep -c "begin{equation" sections/method.tex    # must be ≥ 2
```

### G7 · Disclosure footnote present and correct

The `\author{}` block in `main.tex` must carry a `\thanks` footnote with:
- **Always:** "Human review by a domain expert is strongly recommended" (or equivalent wording)
- **When results are simulated:** also explicitly flags the numerical results as simulated

```bash
grep -E "Human review|human review" main.tex      # must match (always-on clause)
```

If `experiment-suite` was run in simulation mode (its `results.json` has `"simulated": true`), additionally:

```bash
grep -i "simulated" main.tex                      # must match
grep -i "simulated" sections/abstract.tex sections/experiment.tex   # must appear in ≥ 1
```

The simulated marker should appear in at least two surfaces (title `\thanks` plus prose) so readers cannot miss it.

If results are real (user supplied data): the simulated clause must be **absent** from the `\thanks` footnote — drop it once real numbers are wired in. The human-review clause stays.

### G8 · Cross-reference integrity

```bash
grep -oE '\\label\{[^}]+\}' sections/*.tex | sed 's/.*\\label{//;s/}.*//' | sort -u > /tmp/labels
grep -oE '\\ref\{[^}]+\}'   sections/*.tex | sed 's/.*\\ref{//;s/}.*//'    | sort -u > /tmp/refs
diff <(comm -23 /tmp/labels /tmp/refs) <(echo)    # labels with no ref → bad
diff <(comm -13 /tmp/labels /tmp/refs) <(echo)    # refs with no label → bad
```

Tolerance: every figure/table/equation `\label{}` must be `\ref{}`-ed at least once. Sections labeled `sec:*` may not all be referenced — that's okay if they're at least mentioned by name.

## Soft gates (should pass)

### S1 · Notation consistency

Skim all sections looking for the same concept under different symbols. E.g., $L$ vs. $T$ for sequence length, $H$ vs. $\tau$ for horizon. Pick one and globally replace.

### S2 · Caption quality

Read each caption alone (cover the figure/table). Does it convey what's shown? If not, lengthen.

### S3 · Anti-pattern sweep

```bash
# First-person mistakes
grep -E "the authors|This paper presents" sections/*.tex   # should be empty

# Vacuous transitions
grep -E "In recent years|It is well known" sections/*.tex   # should be empty

# Citation dumps (≥ 6 keys in one \cite{})
grep -oE '\\cite\{[^}]+\}' sections/*.tex | awk -F, '{print NF}' | sort -nr | head -3
# top number should be ≤ 5
```

### S4 · Honest limitations

Open `sections/conclusion.tex` and verify a limitations paragraph exists. A conclusion without limitations is weaker than one with them.

### S5 · Figures look right

Grep can confirm a figure compiled; it can't confirm a figure is *right* — a heatmap that silently renders with annotations missing from every row but the first (a real `seaborn` bug, not a script mistake) saves without error and passes every G1–G8 gate. Only looking at the render catches that, so do it yourself:

```bash
pdftoppm -r 200 -png main.pdf /tmp/chk   # one PNG per page
```

Read each page with a figure and check:

- Every data point/row/panel that the script intended to draw is actually visible — not just the first row, category, or panel (the seaborn trap above is the concrete failure mode; multi-panel and grouped-bar figures can drop data the same way).
- Text inside the figure is readable at print scale.
- The figure matches its caption.
- Color palette is consistent with other figures (or deliberately different for a reason).
- Tick labels are rotated/sized correctly, nothing overlaps, nothing is clipped at the figure edge.

## Final report format

When all gates pass, deliver to the user:

```
Paper ready: output/paper-writer/<slug>/latest/paper/main.pdf

Stats:
  Pages:        12
  Bibliography: 247 entries
  \cite{} total: 142 across 7 sections
  Figures:      5 (1 architecture, 3 quantitative, 1 heatmap)
  Tables:       3 (main comparison, ablation, dataset stats)
  Simulated:    yes — marker visible in title \thanks and abstract
  Compile:      0 undefined citations, 0 undefined refs, 1 overfull (line 245, minor)

Quality gate: PASSED (G1–G8 hard, S1–S5 soft).
```

If you can't pass G1–G4 without compromising honesty, **say so explicitly** instead of shipping a weaker paper:

> "Bibliography stalled at 156 entries — could not find more high-quality citations on this niche topic via WebSearch. Page count 9. The paper is delivery-quality at this scope; raising to 200 cites would require padding with low-relevance entries that hurt readability."

That's a legitimate stop. Fabricating entries to clear the gate is not.

## Quick checklist

- [ ] G1 compile clean (0 undefined citations / refs)
- [ ] G2 bibliography ≥ 200 real entries; no `unknown` keys
- [ ] G3 PDF ≥ 8 pages
- [ ] G4 total `\cite{}` ≥ 60 across all sections; per-section minimums hit
- [ ] G5 results.tex has ≥ 1 figure + ≥ 1 table; paper-wide ≥ 3 figures + ≥ 2 tables
- [ ] G6 method.tex has ≥ 2 numbered equations
- [ ] G7 disclosure footnote: human-review clause always present; simulated clause present iff results are simulated
- [ ] G8 every figure/table/equation label is referenced
- [ ] S1–S5 soft gates reviewed
- [ ] Visual sanity check on the rendered PDF
- [ ] Honest report to user — don't pad to clear gates
