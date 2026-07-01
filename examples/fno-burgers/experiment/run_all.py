"""Full experiment driver — produces measured results.json + figdata.npz.

Runs entirely on CPU from self-generated Burgers ground truth. Everything is
deterministic given the seeds. See experiment_design.md for the rationale.

Tracks:
  1. Main comparison  : FNO vs MLP vs CNN, 3 seeds, grid 128 -> test rel-L2.
  2. Super-resolution : train FNO/CNN at 128, test zero-shot at 128/256/512/1024.
  3. Modes ablation   : FNO with {4,8,12,16} retained Fourier modes.
  4. Data scaling     : FNO trained on {200,500,1000} samples.
  4b. Qualitative     : one test IC, its true solution, and each model's prediction.
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone

import numpy as np

import data as D
from train import train_model, evaluate

# ---- fixed configuration -----------------------------------------------------
GRID = 128
NU = 1e-3
T = 1.0
N_TRAIN = 1000
N_VAL = 200
N_TEST = 200
EPOCHS = 50
SEEDS = [0, 1, 2]
MODES, WIDTH, LAYERS = 16, 32, 4
METHODS = ["fno", "mlp", "cnn"]
LABELS = {"fno": "FNO", "mlp": "MLP", "cnn": "CNN"}
DEVICE = "cpu"

t_start = time.time()

# ---- fixed validation / test sets (shared across seeds) ----------------------
xv, yv = D.make_dataset(N_VAL, GRID, seed=43, nu=NU, T=T)
xte, yte = D.make_dataset(N_TEST, GRID, seed=44, nu=NU, T=T)

# =============================================================================
# Track 1 — main comparison across seeds
# =============================================================================
per_seed = {m: [] for m in METHODS}
curves = {m: {"train_loss": None, "val_loss": None} for m in METHODS}
params = {}
trained_seed0 = {}

for s in SEEDS:
    xtr, ytr = D.make_dataset(N_TRAIN, GRID, seed=100 + s, nu=NU, T=T)
    for m in METHODS:
        model, hist, nparam = train_model(
            m, xtr, ytr, xv, yv, grid=GRID, modes=MODES, width=WIDTH,
            n_layers=LAYERS, epochs=EPOCHS, seed=s, device=DEVICE, verbose=False)
        err = evaluate(model, xte, yte, device=DEVICE)
        per_seed[m].append(err)
        params[m] = nparam
        if s == 0:
            curves[m]["train_loss"] = hist["train_loss"]
            curves[m]["val_loss"] = hist["val_loss"]
            trained_seed0[m] = model
        print(f"seed {s} {LABELS[m]:>3}  test relL2 = {err:.4f}  "
              f"({nparam/1e3:.1f}k params)  [{time.time()-t_start:.0f}s]")

summary = {
    m: {"rel_l2": {
        "mean": float(np.mean(per_seed[m])),
        "std": float(np.std(per_seed[m])),
        "n_seeds": len(SEEDS),
        "params": int(params[m]),
    }} for m in METHODS
}

# =============================================================================
# Track 2 — zero-shot super-resolution (discretisation invariance)
# =============================================================================
# Reuse the seed-0 FNO and CNN (both resolution-flexible); MLP is grid-locked.
superres = {"grids": [], "fno": [], "cnn": []}
for g in [128, 256, 512, 1024]:
    xg, yg = D.make_dataset(N_TEST, g, seed=44, nu=NU, T=T)
    superres["grids"].append(g)
    superres["fno"].append(evaluate(trained_seed0["fno"], xg, yg, device=DEVICE))
    superres["cnn"].append(evaluate(trained_seed0["cnn"], xg, yg, device=DEVICE))
    print(f"super-res grid {g:5d}  FNO {superres['fno'][-1]:.4f}  "
          f"CNN {superres['cnn'][-1]:.4f}  [{time.time()-t_start:.0f}s]")

# =============================================================================
# Track 3 — Fourier-modes ablation (single seed, disclosed)
# =============================================================================
xtr0, ytr0 = D.make_dataset(N_TRAIN, GRID, seed=100, nu=NU, T=T)
modes_ablation = {"modes": [], "rel_l2": []}
for md in [4, 8, 12, 16]:
    model, _, _ = train_model("fno", xtr0, ytr0, xv, yv, grid=GRID, modes=md,
                              width=WIDTH, n_layers=LAYERS, epochs=EPOCHS,
                              seed=0, device=DEVICE)
    err = evaluate(model, xte, yte, device=DEVICE)
    modes_ablation["modes"].append(md)
    modes_ablation["rel_l2"].append(err)
    print(f"modes {md:2d}  test relL2 = {err:.4f}  [{time.time()-t_start:.0f}s]")

# =============================================================================
# Track 4 — training-set-size scaling (single seed, disclosed)
# =============================================================================
data_scaling = {"n_train": [], "rel_l2": []}
for n in [200, 500, 1000]:
    xtr_n, ytr_n = xtr0[:n], ytr0[:n]
    model, _, _ = train_model("fno", xtr_n, ytr_n, xv, yv, grid=GRID, modes=MODES,
                              width=WIDTH, n_layers=LAYERS, epochs=EPOCHS,
                              seed=0, device=DEVICE)
    err = evaluate(model, xte, yte, device=DEVICE)
    data_scaling["n_train"].append(n)
    data_scaling["rel_l2"].append(err)
    print(f"n_train {n:5d}  test relL2 = {err:.4f}  [{time.time()-t_start:.0f}s]")

# =============================================================================
# Track 4b — qualitative sample (for the solution-profile figure)
# =============================================================================
import torch
idx = 0
sample = {"x_grid": np.linspace(0, 1, GRID).tolist(),
          "u0": xte[idx].tolist(), "true": yte[idx].tolist()}
with torch.no_grad():
    for m in METHODS:
        pred = trained_seed0[m](torch.as_tensor(xte[idx:idx+1], dtype=torch.float32))
        sample[m] = pred.squeeze(0).numpy().tolist()

# =============================================================================
# Persist
# =============================================================================
wall = time.time() - t_start
results = {
    "task": "operator learning — 1D viscous Burgers, u(.,0) -> u(.,1)",
    "dataset": f"self-generated Burgers GRF, nu={NU}, T={T}, grid={GRID}, "
               f"{N_TRAIN} train / {N_VAL} val / {N_TEST} test",
    "metrics": ["rel_l2"],
    "seeds": SEEDS,
    "provenance": {
        "mode": "measured",
        "source": "measured run from experiment/run_all.py (pseudo-spectral "
                  "ground truth generated in data.py; no external dataset)",
        "dataset_contract": "./data_contract.md",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "hardware": "CPU (local); PyTorch 2.5.1",
        "wall_clock_seconds": round(wall, 1),
    },
    "summary": summary,
    "ablation": {
        "fourier_modes": modes_ablation,
        "train_size": data_scaling,
    },
    "super_resolution": superres,
    "training_curves": curves,
    "notes": ("Fully measured, deterministic given seeds. Ablations (modes, "
              "train-size) use a single seed (n_seeds=1) and are reported as trends, "
              "not for significance testing. Super-resolution reuses the seed-0 "
              "models evaluated zero-shot on finer grids; MLP is excluded there "
              "because its first layer is grid-locked."),
}

with open("../results.json", "w") as f:
    json.dump(results, f, indent=2)

np.savez("../figures/figdata.npz",
         per_seed_fno=np.array(per_seed["fno"]),
         per_seed_mlp=np.array(per_seed["mlp"]),
         per_seed_cnn=np.array(per_seed["cnn"]),
         curve_fno=np.array(curves["fno"]["val_loss"]),
         curve_mlp=np.array(curves["mlp"]["val_loss"]),
         curve_cnn=np.array(curves["cnn"]["val_loss"]),
         curve_fno_tr=np.array(curves["fno"]["train_loss"]),
         sr_grids=np.array(superres["grids"]),
         sr_fno=np.array(superres["fno"]),
         sr_cnn=np.array(superres["cnn"]),
         ab_modes=np.array(modes_ablation["modes"]),
         ab_modes_err=np.array(modes_ablation["rel_l2"]),
         ab_n=np.array(data_scaling["n_train"]),
         ab_n_err=np.array(data_scaling["rel_l2"]),
         s_x=np.array(sample["x_grid"]), s_u0=np.array(sample["u0"]),
         s_true=np.array(sample["true"]), s_fno=np.array(sample["fno"]),
         s_mlp=np.array(sample["mlp"]), s_cnn=np.array(sample["cnn"]))

print(f"\nDONE in {wall:.0f}s. Wrote results.json + figures/figdata.npz")
print("Main test rel-L2:",
      {LABELS[m]: round(summary[m]['rel_l2']['mean'], 4) for m in METHODS})
