#!/usr/bin/env python3
"""场能最小模拟：同一个自由能，能否同时长出同化与品味？

模型（图上的 Ginzburg–Landau / Ising）：
  E[phi] = (gamma/2) sum_edges (phi_i - phi_j)^2 + sum_i V(phi_i) - h sum_i phi_i
  V(phi) = (lam/4)(phi^2 - 1)^2
  dphi/dt = -dF/dphi + noise

读法：
  h 高、单井 -> 均匀（同化）
  h 低、双井 -> 分相（品味）
  gamma 高 -> 域粗化（两个大本营）；gamma 低 -> 许多小域（多种风格）

这是 C 级构造模拟：参数是选的，不是估的；不把模拟值当读数。
输出：analysis/results/sim_field_energy.json
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis" / "results"
OUT.mkdir(parents=True, exist_ok=True)


def run_field(h: float = 0.0, gamma: float = 1.0, theta: float = 0.02,
              seed: int = 0, n: int = 20, steps: int = 2500,
              eta: float = 0.05, lam: float = 1.0) -> dict:
    rng = np.random.default_rng(seed)
    phi = rng.normal(0.0, 0.1, (n, n))
    for _ in range(steps):
        nb = (np.roll(phi, 1, 0) + np.roll(phi, -1, 0)
              + np.roll(phi, 1, 1) + np.roll(phi, -1, 1))
        lap = nb - 4.0 * phi
        dV = lam * (phi ** 3 - phi)
        phi = phi + eta * (gamma * lap - dV + h) + rng.normal(0.0, np.sqrt(2.0 * theta * eta), (n, n))

    m = float(phi.mean())
    var = float(phi.var())
    pos = float((phi > 0).mean())
    lab, nlab = ndimage.label(phi > 0)
    if nlab:
        sizes = ndimage.sum(np.ones_like(phi), lab, range(1, nlab + 1))
        dom = float(sizes.mean() / (n * n))
    else:
        dom = 0.0
    extreme = float((np.abs(phi) > 0.8).mean())

    nb = (np.roll(phi, 1, 0) + np.roll(phi, -1, 0)
          + np.roll(phi, 1, 1) + np.roll(phi, -1, 1))
    lap = nb - 4.0 * phi
    energy = float(0.5 * gamma * np.sum(phi * lap) + np.sum((lam / 4.0) * (phi ** 2 - 1.0) ** 2) - h * np.sum(phi))
    return {
        "h": h, "gamma": gamma, "theta": theta,
        "m": m, "var": var, "positive_fraction": pos,
        "n_positive_domains": int(nlab), "mean_domain_size": dom,
        "extreme_fraction": extreme, "energy": energy,
    }


def main() -> None:
    rows = []
    for h in (0.0, 0.03, 0.1, 0.3):
        for gamma in (0.2, 0.5, 1.0):
            vals = [run_field(h=h, gamma=gamma, seed=s) for s in range(5)]
            rows.append({
                "h": h, "gamma": gamma,
                "m_mean": float(np.mean([v["m"] for v in vals])),
                "var_mean": float(np.mean([v["var"] for v in vals])),
                "positive_fraction_mean": float(np.mean([v["positive_fraction"] for v in vals])),
                "n_positive_domains_mean": float(np.mean([v["n_positive_domains"] for v in vals])),
                "mean_domain_size_mean": float(np.mean([v["mean_domain_size"] for v in vals])),
                "extreme_fraction_mean": float(np.mean([v["extreme_fraction"] for v in vals])),
                "energy_mean": float(np.mean([v["energy"] for v in vals])),
            })
    payload = {
        "meta": {
            "status": "C-level constructed simulation; parameters chosen, not estimated",
            "grid": "20x20 periodic", "steps": 2500, "eta": 0.05,
            "theta": 0.02, "lam": 1.0, "seeds": 5,
            "note": "h high -> uniform; h low + double well -> phase separation; gamma coarsens domains",
        },
        "rows": rows,
    }
    (OUT / "sim_field_energy.json").write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    print("wrote", OUT / "sim_field_energy.json")
    for r in rows:
        print(
            f"h={r['h']:.2f} g={r['gamma']:.1f} "
            f"m={r['m_mean']:.2f} var={r['var_mean']:.2f} "
            f"pos={r['positive_fraction_mean']:.2f} "
            f"nd={r['n_positive_domains_mean']:.1f} "
            f"dom={r['mean_domain_size_mean']:.2f}"
        )


if __name__ == "__main__":
    main()
