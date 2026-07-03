# Example — FNO on the Burgers operator

A complete run produced end to end by the `experiment-suite` and `paper-writer`
skills: **"Learning the Burgers Solution Operator with a Fourier Neural Operator."**

Everything here is real and reproducible:

- [`paper.pdf`](paper.pdf) — the 8-page paper (22 citations, 5 figures).
- [`experiment/`](experiment/) — the code the agent wrote and ran (`model.py` is a real
  1-D FNO with baselines; `run_all.py` runs the full study).
- [`results.json`](results.json) — measured results with provenance (`mode: measured`).
- [`experiment_report.md`](experiment_report.md), [`experiment_design.md`](experiment_design.md),
  [`data_contract.md`](data_contract.md) — the design and report artifacts.

## Measured results

Test relative-L2 on the 1-D viscous Burgers operator (mean over 3 seeds, CPU):

| Model | Rel. L2 | Params |
|---|---|---|
| **FNO** | **4.41%** | 74k |
| MLP | 21.63% | 657k |
| CNN | 67.69% | 42k |

Zero-shot super-resolution (FNO trained at grid 128): error stays 4.2–4.7% at
256 / 512 / 1024 — the discretisation-invariance property. Total run: ~35 min on a
laptop CPU. No external dataset (ground truth from a pseudo-spectral solver).

## Reproduce

```bash
cd experiment
pip install -r requirements.txt
python run_all.py        # writes results.json + figure data
```

All numbers are `measured`; none are simulated or fabricated. The paper was written
by an AI agent and, as noted in it, domain-expert review is recommended before any
downstream use.
