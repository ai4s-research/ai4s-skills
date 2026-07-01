"""Ground-truth data generation for the 1D viscous Burgers' equation.

We learn the solution operator  G: u(x, 0) -> u(x, T)  of

    u_t + u u_x = nu u_xx,     x in [0, 1), periodic,   t in [0, T].

Initial conditions are drawn from a Gaussian random field (GRF) with a
Matern-like spectral density, matching the standard FNO-Burgers benchmark
(Li et al., 2021). The PDE is integrated with a pseudo-spectral method
(FFT in space) and an exponential-time-differencing RK2 step for the
stiff diffusion term, which keeps the viscous part exact.

Everything here is a real numerical solver: the arrays it returns are the
ground truth the neural operator is measured against. No data is downloaded.
"""

from __future__ import annotations

import numpy as np


def grf_initial_conditions(n_samples: int, grid: int, rng: np.random.Generator,
                           tau: float = 7.0, alpha: float = 2.5) -> np.ndarray:
    """Sample periodic initial conditions from a Gaussian random field.

    Spectral density ~ (tau^2 + (2*pi*k)^2)^(-alpha).  Larger alpha -> smoother.
    Returns array of shape (n_samples, grid), zero-mean per sample.
    """
    k = np.fft.fftfreq(grid, d=1.0 / grid)  # integer wavenumbers
    # spectral standard deviation of each Fourier mode
    coef = (tau ** 2 + (2.0 * np.pi * k) ** 2) ** (-alpha / 2.0)
    coef[0] = 0.0  # zero mean
    u0 = np.empty((n_samples, grid), dtype=np.float64)
    for i in range(n_samples):
        noise = rng.standard_normal(grid) + 1j * rng.standard_normal(grid)
        uh = coef * noise * grid
        u = np.fft.ifft(uh).real
        # normalise to a consistent amplitude band so the operator task is well-posed
        u = u / (np.std(u) + 1e-8)
        u0[i] = u
    return u0


def solve_burgers(u0: np.ndarray, nu: float = 1e-2, T: float = 1.0,
                  n_steps: int = 2000) -> np.ndarray:
    """Integrate Burgers from u0 to time T with pseudo-spectral integrating-factor RK4.

    Diffusion (the stiff linear part L) is handled exactly through the
    integrating factor exp(L*dt); the nonlinear advection is advanced with RK4.
    This is the scheme from Trefethen, *Spectral Methods in MATLAB* (KdV example),
    and it has no 1/L singularity at the k=0 mode.

    u0: (n_samples, grid). Returns u(.,T) with the same shape.
    """
    grid = u0.shape[1]
    dt = T / n_steps
    k = 2.0 * np.pi * np.fft.fftfreq(grid, d=1.0 / grid)  # spatial wavenumbers
    ik = 1j * k
    # 2/3-rule dealiasing mask for the quadratic nonlinearity
    kmax = np.abs(k).max()
    dealias = (np.abs(k) <= (2.0 / 3.0) * kmax).astype(np.float64)
    L = -nu * k ** 2                     # linear (diffusion) operator in Fourier space
    E = np.exp(L * dt)                   # exact propagator over a full step
    E2 = np.exp(L * dt / 2.0)            # ... and over a half step

    uh = np.fft.fft(u0, axis=1)

    def nonlinear(uh_):
        u = np.fft.ifft(uh_, axis=1).real
        # conservative form: -0.5 d/dx (u^2), dealiased
        return -0.5 * ik * dealias * np.fft.fft(u * u, axis=1)

    for _ in range(n_steps):
        Nu = nonlinear(uh)
        a = E2 * uh + (dt / 2.0) * E2 * Nu
        Na = nonlinear(a)
        b = E2 * uh + (dt / 2.0) * Na
        Nb = nonlinear(b)
        c = E * uh + dt * E2 * Nb
        Nc = nonlinear(c)
        uh = E * uh + (dt / 6.0) * (E * Nu + 2.0 * E2 * (Na + Nb) + Nc)
    return np.fft.ifft(uh, axis=1).real


def make_dataset(n_samples: int, grid: int, seed: int, nu: float = 1e-2,
                 T: float = 1.0) -> tuple[np.ndarray, np.ndarray]:
    """Return (inputs u0, targets uT), both (n_samples, grid), float32."""
    rng = np.random.default_rng(seed)
    u0 = grf_initial_conditions(n_samples, grid, rng)
    uT = solve_burgers(u0, nu=nu, T=T)
    return u0.astype(np.float32), uT.astype(np.float32)


if __name__ == "__main__":
    x, y = make_dataset(4, 128, seed=0)
    print("inputs", x.shape, "targets", y.shape,
          "| input std", float(x.std()), "| target std", float(y.std()))
