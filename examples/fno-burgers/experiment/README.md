# Burgers Operator Learning — runnable package

Learns the solution operator `G: u(·,0) → u(·,1)` of the 1D viscous Burgers'
equation and compares a **Fourier Neural Operator (FNO)** against MLP and CNN
baselines. All ground truth is generated locally by a pseudo-spectral solver —
**nothing is downloaded**.

## Files
| File | Role |
|---|---|
| `data.py`      | GRF initial conditions + pseudo-spectral IFRK4 Burgers solver (ground truth) |
| `model.py`     | `FNO1d`, `MLPNet`, `CNNNet`, `build_model` |
| `train.py`     | relative-L2 loss, training loop, `evaluate` |
| `run_all.py`   | full experiment → writes `../results.json` and `../figures/figdata.npz` |
| `config.yaml`  | all hyperparameters |
| `evaluate.py`  | standalone: prints test error of a freshly trained FNO |

## Run
```bash
pip install -r requirements.txt
python run_all.py        # ~10–15 min on CPU; deterministic given seeds
```
Outputs land in the parent run directory (`../results.json`, `../figures/`).

## Scope / honesty
This is a compact, CPU-runnable reproduction — **not** a SOTA benchmark. The FNO,
data budget, and epochs are deliberately small so the whole study runs in minutes.
Results are **measured** (see `../results.json` → `provenance.mode == "measured"`),
not simulated. Ablations (Fourier modes, train size) use a single seed and are
reported as trends. A human expert review is recommended before citing any number.
