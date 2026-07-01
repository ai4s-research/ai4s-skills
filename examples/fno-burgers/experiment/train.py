"""Training loop and the relative-L2 objective used throughout.

Relative L2 (a.k.a. normalised RMSE) is the standard neural-operator metric:

    ||pred - target||_2 / ||target||_2   averaged over the batch.

It is scale-free, so it compares fairly across resolutions and amplitudes.
"""

from __future__ import annotations

import numpy as np
import torch
from torch.utils.data import DataLoader, TensorDataset

from model import build_model, count_params


def rel_l2(pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    """Mean relative L2 error over the batch (dim=-1 is the spatial grid)."""
    num = torch.linalg.norm(pred - target, dim=-1)
    den = torch.linalg.norm(target, dim=-1) + 1e-8
    return (num / den).mean()


def set_seed(seed: int) -> None:
    torch.manual_seed(seed)
    np.random.seed(seed)


def train_model(name: str, x_train, y_train, x_val, y_val, *, grid: int,
                modes: int = 16, width: int = 32, n_layers: int = 4,
                epochs: int = 50, batch_size: int = 20, lr: float = 1e-3,
                seed: int = 0, device: str = "cpu", verbose: bool = False):
    """Train one model; return (model, history) where history has train/val curves."""
    set_seed(seed)
    model = build_model(name, grid=grid, modes=modes, width=width,
                        n_layers=n_layers).to(device)

    xt = torch.as_tensor(x_train, dtype=torch.float32)
    yt = torch.as_tensor(y_train, dtype=torch.float32)
    xv = torch.as_tensor(x_val, dtype=torch.float32).to(device)
    yv = torch.as_tensor(y_val, dtype=torch.float32).to(device)
    loader = DataLoader(TensorDataset(xt, yt), batch_size=batch_size, shuffle=True)

    opt = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=epochs)

    hist = {"train_loss": [], "val_loss": []}
    for ep in range(epochs):
        model.train()
        tot, nb = 0.0, 0
        for xb, yb in loader:
            xb, yb = xb.to(device), yb.to(device)
            opt.zero_grad()
            loss = rel_l2(model(xb), yb)
            loss.backward()
            opt.step()
            tot += loss.item(); nb += 1
        sched.step()
        model.eval()
        with torch.no_grad():
            vl = rel_l2(model(xv), yv).item()
        hist["train_loss"].append(tot / nb)
        hist["val_loss"].append(vl)
        if verbose and (ep % 10 == 0 or ep == epochs - 1):
            print(f"  [{name}] epoch {ep:3d}  train {tot/nb:.4f}  val {vl:.4f}")
    return model, hist, count_params(model)


@torch.no_grad()
def evaluate(model, x_test, y_test, device: str = "cpu") -> float:
    """Return mean relative-L2 error on a test set (possibly a different grid)."""
    model.eval()
    xt = torch.as_tensor(x_test, dtype=torch.float32).to(device)
    yt = torch.as_tensor(y_test, dtype=torch.float32).to(device)
    return rel_l2(model(xt), yt).item()
