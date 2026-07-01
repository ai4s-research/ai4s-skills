"""Standalone evaluation: train an FNO on freshly generated Burgers data and
print its test relative-L2 error, including zero-shot super-resolution.

Usage:  python evaluate.py
This is a light smoke entrypoint; the full study lives in run_all.py.
"""

from __future__ import annotations

import data as D
from train import train_model, evaluate


def main() -> None:
    xtr, ytr = D.make_dataset(500, 128, seed=100)
    xv, yv = D.make_dataset(200, 128, seed=43)
    xte, yte = D.make_dataset(200, 128, seed=44)
    model, hist, nparam = train_model(
        "fno", xtr, ytr, xv, yv, grid=128, epochs=50, seed=0, verbose=True)
    print(f"\nFNO test rel-L2 @128 = {evaluate(model, xte, yte):.4f} "
          f"({nparam/1e3:.1f}k params)")
    for g in (256, 512, 1024):
        xg, yg = D.make_dataset(200, g, seed=44)
        print(f"zero-shot rel-L2 @{g:<4} = {evaluate(model, xg, yg):.4f}")


if __name__ == "__main__":
    main()
