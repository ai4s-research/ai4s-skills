# Experiment Design — Learning the Burgers Solution Operator with an FNO

## Motivation

Most scientific simulation reduces to solving partial differential equations (PDEs)
under many different inputs — initial conditions, boundary data, coefficient fields.
Classical solvers recompute the full time integration for every new input, which is
expensive when thousands of queries are needed (design optimisation, uncertainty
quantification, real-time control). *Operator learning* proposes to amortise this
cost: train a neural network once to approximate the solution operator
`G: a ↦ u`, then obtain new solutions with a single forward pass. The **Fourier
Neural Operator (FNO)** is the most influential architecture in this line because
it parameterises the kernel of an integral operator directly in the frequency
domain, giving it two properties a plain network lacks: a *global* receptive field
at every layer, and *discretisation invariance* — the same weights act on any grid
resolution. This experiment tests both claims on the canonical 1D Burgers benchmark
in a compact, fully reproducible, CPU-only setting.

## Research question & hypotheses

**Question.** Can an FNO learn the solution operator of the 1D viscous Burgers'
equation accurately, and does it retain accuracy when evaluated at resolutions it
never saw during training?

- **H1 (accuracy).** An FNO reaches low relative-L2 error (target < 3%) on held-out
  initial conditions, and beats a parameter-comparable MLP and CNN.
- **H2 (discretisation invariance).** An FNO trained only at grid 128 keeps
  essentially the same error when evaluated zero-shot at 256/512/1024, whereas a
  grid-locked MLP cannot even be applied.
- **H3 (spectral capacity).** Accuracy improves as the number of retained Fourier
  modes increases, then saturates once the modes cover the solution's active band.

## Task

Regression of a function from a function: input is the discretised initial
condition `u(·,0)` (length N), output is the solution `u(·,1)` (length N). The
governing equation is `u_t + u u_x = nu u_xx` with `nu = 1e-3`, periodic on `[0,1)`.
At this viscosity the solution develops steep, shock-like fronts before mild
diffusion, so the operator is genuinely nonlinear and non-trivial to approximate.

## Datasets

Self-generated ground truth (see `data_contract.md`). Initial conditions are drawn
from a Gaussian random field; the PDE is integrated with a pseudo-spectral
integrating-factor RK4 solver (2000 steps), which treats the stiff diffusion term
exactly and is stable at this viscosity. 1000 training / 200 validation / 200 test
functions at grid 128; test sets are additionally regenerated at 256/512/1024 for
the super-resolution probe. No external dataset is used, which makes the whole study
reproducible bit-for-bit from the seeds.

## Baselines

- **MLP** — a four-layer fully-connected network over the flattened grid. It has no
  inductive bias for locality or translation and its first layer hard-codes the grid
  size, so it is the "no structure" reference and cannot transfer across resolutions.
- **CNN** — a four-layer 1-D convolutional network. It is translation-equivariant and
  resolution-flexible but has only a *local* receptive field. Contrasting it with the
  FNO isolates the specific value of *global* spectral mixing, independent of weight
  sharing.
- **FNO** — four spectral-convolution blocks (16 modes, width 32) with a pointwise
  residual branch, GELU activations, and an `(u₀, x)` lifting so the network sees the
  coordinate. This is a small but faithful FNO.

## Metrics

Mean **relative L2 error** `‖pred − target‖₂ / ‖target‖₂` over the test set — the
standard scale-free operator-learning metric, comparable across resolutions and
amplitudes. It is also the training objective.

## Ablations

1. **Fourier modes** ∈ {4, 8, 12, 16} — tests H3 (spectral capacity vs accuracy).
2. **Training-set size** ∈ {200, 500, 1000} — data efficiency / sample complexity.
3. **Resolution** ∈ {128, 256, 512, 1024} — zero-shot super-resolution, tests H2.

Ablations 1–2 use a single seed and are read as trends, not significance tests; the
main comparison (H1) uses three seeds with mean ± std.

## Compute budget

Deliberately small: CPU only, PyTorch, 50 epochs, batch 20, Adam (lr 1e-3, cosine
decay, weight decay 1e-4). The full study — three seeds × three models plus all
ablations and the super-resolution sweep — completes in roughly ten to fifteen
minutes on a laptop CPU. This is a teaching-scale reproduction chosen so that every
number is measured and re-runnable, not a maximal-accuracy benchmark; a production
FNO would use more data, more modes, and GPU training.

## Threats to validity

The GRF prior fixes the input distribution; conclusions are conditional on it.
Single-seed ablations can be noisy. The MLP/CNN baselines are intentionally modest,
so their absolute numbers should be read as reference points, not tuned upper bounds.
All of these are disclosed in the report and in `results.json → notes`.
