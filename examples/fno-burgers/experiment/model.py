"""Models for learning the Burgers solution operator.

Three architectures, all mapping a discretised initial condition u0 (length N)
to the solution uT (length N):

  * FNO1d  — Fourier Neural Operator (Li et al., 2021). Learns global kernels in
             spectral space; the number of retained Fourier modes is fixed, so the
             same weights apply at any grid resolution (discretisation invariance).
  * MLPNet — a plain fully-connected net over the flattened grid. Grid-size bound:
             its first layer hard-codes the input length, so it cannot transfer to
             a new resolution. Serves as the "no inductive bias" baseline.
  * CNNNet — a 1-D convolutional net (local, translation-equivariant). Resolution
             flexible but only local receptive field; the contrast with FNO isolates
             the value of *global* spectral mixing.
"""

from __future__ import annotations

import torch
import torch.nn as nn


class SpectralConv1d(nn.Module):
    """1-D spectral convolution: multiply the lowest `modes` Fourier modes by
    learnable complex weights, zero the rest."""

    def __init__(self, in_ch: int, out_ch: int, modes: int):
        super().__init__()
        self.in_ch, self.out_ch, self.modes = in_ch, out_ch, modes
        scale = 1.0 / (in_ch * out_ch)
        self.weight = nn.Parameter(
            scale * torch.rand(in_ch, out_ch, modes, dtype=torch.cfloat)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:  # x: (B, C, N)
        B, C, N = x.shape
        x_ft = torch.fft.rfft(x, dim=-1)                 # (B, C, N//2+1)
        m = min(self.modes, x_ft.shape[-1])
        out_ft = torch.zeros(B, self.out_ch, x_ft.shape[-1],
                             dtype=torch.cfloat, device=x.device)
        out_ft[:, :, :m] = torch.einsum(
            "bim,iom->bom", x_ft[:, :, :m], self.weight[:, :, :m]
        )
        return torch.fft.irfft(out_ft, n=N, dim=-1)      # (B, out_ch, N)


class FNO1d(nn.Module):
    """Fourier Neural Operator, 1-D. Input carries the field plus the x-coordinate
    so the network is aware of geometry (standard FNO lifting)."""

    def __init__(self, modes: int = 16, width: int = 32, n_layers: int = 4):
        super().__init__()
        self.modes, self.width, self.n_layers = modes, width, n_layers
        self.fc0 = nn.Linear(2, width)                   # (u0, x) -> width
        self.spectral = nn.ModuleList(
            [SpectralConv1d(width, width, modes) for _ in range(n_layers)]
        )
        self.local = nn.ModuleList(
            [nn.Conv1d(width, width, 1) for _ in range(n_layers)]
        )
        self.fc1 = nn.Linear(width, 128)
        self.fc2 = nn.Linear(128, 1)
        self.act = nn.GELU()

    def forward(self, u0: torch.Tensor) -> torch.Tensor:  # u0: (B, N)
        B, N = u0.shape
        x = torch.linspace(0, 1, N, device=u0.device).repeat(B, 1)
        h = torch.stack([u0, x], dim=-1)                  # (B, N, 2)
        h = self.fc0(h).permute(0, 2, 1)                  # (B, width, N)
        for spec, loc in zip(self.spectral, self.local):
            h = self.act(spec(h) + loc(h))
        h = h.permute(0, 2, 1)                            # (B, N, width)
        h = self.act(self.fc1(h))
        return self.fc2(h).squeeze(-1)                    # (B, N)


class MLPNet(nn.Module):
    """Fully-connected baseline over the flattened grid (resolution-bound)."""

    def __init__(self, grid: int, hidden: int = 512, depth: int = 4):
        super().__init__()
        self.grid = grid
        layers = [nn.Linear(grid, hidden), nn.GELU()]
        for _ in range(depth - 2):
            layers += [nn.Linear(hidden, hidden), nn.GELU()]
        layers += [nn.Linear(hidden, grid)]
        self.net = nn.Sequential(*layers)

    def forward(self, u0: torch.Tensor) -> torch.Tensor:
        return self.net(u0)


class CNNNet(nn.Module):
    """1-D CNN baseline: local, translation-equivariant, resolution-flexible."""

    def __init__(self, width: int = 64, depth: int = 4, kernel: int = 5):
        super().__init__()
        pad = kernel // 2
        layers = [nn.Conv1d(1, width, kernel, padding=pad), nn.GELU()]
        for _ in range(depth - 2):
            layers += [nn.Conv1d(width, width, kernel, padding=pad), nn.GELU()]
        layers += [nn.Conv1d(width, 1, kernel, padding=pad)]
        self.net = nn.Sequential(*layers)

    def forward(self, u0: torch.Tensor) -> torch.Tensor:  # (B, N)
        return self.net(u0.unsqueeze(1)).squeeze(1)


def build_model(name: str, grid: int, modes: int = 16, width: int = 32,
                n_layers: int = 4) -> nn.Module:
    name = name.lower()
    if name == "fno":
        return FNO1d(modes=modes, width=width, n_layers=n_layers)
    if name == "mlp":
        return MLPNet(grid=grid)
    if name == "cnn":
        return CNNNet()
    raise ValueError(f"unknown model: {name}")


def count_params(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters())
