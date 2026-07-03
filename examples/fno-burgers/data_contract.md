# Data Contract

**Data class:** synthetic ground truth, generated at runtime (no external download).

## Source & access route
The dataset is produced by `experiment/data.py`, which numerically integrates the
1D viscous Burgers' equation with a pseudo-spectral integrating-factor RK4 scheme.
There is **no third-party dataset, no network access, and no license constraint** —
the ground truth is a deterministic function of the random seed.

## Generating process
- **PDE:** `u_t + u u_x = nu u_xx`, periodic on `x ∈ [0,1)`, `nu = 1e-3`, integrated to `T = 1.0` on a fine grid (≥ 1024 and ≥ 2× the target grid, 4×grid time steps), then spectrally restricted to the target grid so the targets stay fully resolved at this viscosity.
- **Initial conditions:** Gaussian random field, spectral density `(tau² + (2πk)²)^(-alpha/2)`, `tau=7`, `alpha=2.5`, normalised to unit standard deviation per sample.
- **Discretisation:** uniform grid, 128 points for train/val/test; 256/512/1024 additionally generated for the zero-shot super-resolution test.

## Splits & seeds
| Split | Size | Seed | Notes |
|---|---|---|---|
| train | 1000 | `100 + s` (per model seed `s`) | resampled per seed for honest variance |
| val   | 200  | 43 | fixed across all runs |
| test  | 200  | 44 | fixed; also regenerated at 256/512/1024 for super-resolution |

## Version & reproducibility
- Version = the git commit of `data.py` plus the seeds above. Re-running reproduces every array bit-for-bit on the same NumPy/CPU build.
- `results.json → provenance` records mode=`measured`, wall-clock, and a pointer back to this contract.

## Reuse boundary
These arrays are generated on demand and are **not** cached to disk as a shared
corpus; any downstream skill (e.g. `paper-writer`) consumes `results.json` and the
figures, not the raw tensors. No PII, no external attribution required.
