#!/usr/bin/env python3
"""爱与好奇的最小验证：五件事能不能从 nu / kappa 长出来。

三个最小模型，不是一次大一统模拟：
  A. variant 模型      —— 群体、社会摆动、文明五量
  B. binary bridge 模型 —— 文化同化
  C. threshold 模型     —— 社会品味（新码采纳顺序）

设计纪律：
- 每个实验都先写“若反向则什么死”；结果只报方向，不报“证明”。
- 参数是选的，不是估的；这是 C 级构造模拟，不是经验证据。
- 结果写入 analysis/results/sim_love_curiosity.json；判读写在
  analysis/SIM-LOVE-CURIOSITY.md，不把模拟当读数。

用法：
  python analysis/sim_love_curiosity.py
"""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path

import networkx as nx
import numpy as np
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis" / "results"
OUT.mkdir(parents=True, exist_ok=True)

M = 12          # variants on a circle
N = 120         # agents
SEEDS = 10      # seeds per cell


def softmax_rows(u: np.ndarray, beta: float = 6.0) -> np.ndarray:
    z = beta * (u - u.max(axis=1, keepdims=True))
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


def sample_rows(p: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    # p: (n, M); one draw per row
    c = np.cumsum(p, axis=1)
    r = rng.random((p.shape[0], 1))
    return (r > c).sum(axis=1).clip(0, p.shape[1] - 1)


@dataclass
class VariantConfig:
    steps: int = 400
    gamma: float = 0.8
    kappa_mean: float = 0.5
    nu_in: float = 0.8
    nu_out: float = 0.0
    C: float = 0.2
    beta: float = 6.0
    p_in: float = 0.15
    p_out: float = 0.02
    init: str = "random"      # random | consensus
    shock_t: int = -1          # -1 = no shock
    shock_gamma: float | None = None
    shock_variant: int = 6
    shock_frac: float = 0.10
    lag: int = 0               # 0 = no lag; >0 = use frequency from t-lag
    e4_b: float = 0.0          # E4: gamma responds to lagged novelty
    e4_lag: int = 0
    e4_target: float = 0.5


def variant_run(cfg: VariantConfig, seed: int) -> dict:
    rng = np.random.default_rng(seed)
    n = N
    comm = np.array([0] * (n // 2) + [1] * (n - n // 2))
    kappa = np.clip(rng.lognormal(np.log(cfg.kappa_mean), 0.5, n), 0.02, 3.0)
    x = np.zeros(n, dtype=int) if cfg.init == "consensus" else rng.integers(0, M, n)
    hist = []
    nov_hist = []
    for t in range(cfg.steps):
        gamma = cfg.gamma
        if cfg.e4_b > 0 and t >= cfg.e4_lag:
            gamma = cfg.gamma + cfg.e4_b * (nov_hist[t - cfg.e4_lag] - cfg.e4_target)
            gamma = float(np.clip(gamma, 0.05, 4.0))
        if cfg.shock_t >= 0 and t >= cfg.shock_t and cfg.shock_gamma is not None:
            gamma = cfg.shock_gamma
        if cfg.shock_t >= 0 and t == cfg.shock_t:
            idx = rng.choice(n, int(n * cfg.shock_frac), replace=False)
            x[idx] = cfg.shock_variant
        freq = np.bincount(x, minlength=M) / n
        fref = freq if cfg.lag == 0 or len(hist) < cfg.lag else hist[-cfg.lag]
        in_freq = np.zeros((2, M))
        out_freq = np.zeros((2, M))
        for c in range(2):
            m = comm == c
            in_freq[c] = np.bincount(x[m], minlength=M) / m.sum()
            out_freq[c] = np.bincount(x[~m], minlength=M) / (~m).sum()
        U = (
            gamma * fref[None, :]
            + kappa[:, None] * (1.0 - fref)[None, :]
            + cfg.nu_in * in_freq[comm]
            + cfg.nu_out * out_freq[comm]
        )
        U[np.arange(n), x] -= cfg.C
        x = sample_rows(softmax_rows(U, cfg.beta), rng)
        f_now = np.bincount(x, minlength=M) / n
        hist.append(f_now)
        nov_hist.append(1.0 - f_now.max())
    return {"x": x, "comm": comm, "kappa": kappa, "freq": np.array(hist)}


def homophily(x: np.ndarray, comm: np.ndarray, rng: np.random.Generator, pairs: int = 4000) -> float:
    n = len(x)
    ii = rng.integers(0, n, pairs)
    jj = rng.integers(0, n, pairs)
    keep = ii != jj
    ii, jj = ii[keep], jj[keep]
    same = x[ii] == x[jj]
    within = comm[ii] == comm[jj]
    return float(same[within].mean() - same[~within].mean())


def summarizing(freq: np.ndarray, tail: int = 40) -> dict:
    f = freq[-tail:].mean(axis=0)
    return {
        "max_share": float(f.max()),
        "n_variants_5pct": int((f >= 0.05).sum()),
        "entropy": float(-(f * np.log(f + 1e-12)).sum()),
    }


def exp_group() -> dict:
    rows = []
    for nu_in in (0.0, 1.5, 3.0):
        for kappa_mean in (0.1, 1.0):
            hs, nvs, mxs = [], [], []
            for seed in range(SEEDS):
                cfg = VariantConfig(nu_in=nu_in, kappa_mean=kappa_mean, gamma=1.0, C=0.2, steps=350)
                out = variant_run(cfg, seed)
                rng = np.random.default_rng(seed + 1000)
                hs.append(homophily(out["x"], out["comm"], rng))
                s = summarizing(out["freq"])
                nvs.append(s["n_variants_5pct"])
                mxs.append(s["max_share"])
            rows.append({
                "nu_in": nu_in,
                "kappa_mean": kappa_mean,
                "homophily_mean": float(np.mean(hs)),
                "homophily_sd": float(np.std(hs, ddof=1)),
                "frac_separated": float(np.mean(np.array(hs) > 0.5)),
                "n_variants_mean": float(np.mean(nvs)),
                "max_share_mean": float(np.mean(mxs)),
            })
    return {"design": "3x2: nu_in {0,1.5,3.0} x kappa_mean {0.1,1.0}; gamma=1.0, C=0.2, 10 seeds", "rows": rows}


def exp_swing() -> dict:
    rows = []
    for shock_gamma in (0.8, 2.0):
        for lag in (0, 5):
            novs, halves = [], []
            for seed in range(SEEDS):
                cfg = VariantConfig(
                    steps=250, gamma=0.5, shock_t=50, shock_gamma=shock_gamma,
                    kappa_mean=0.5, nu_in=0.8, C=0.1, lag=lag, init="random",
                )
                out = variant_run(cfg, seed)
                f = out["freq"]
                nov = 1.0 - f.max(axis=1)
                pre = nov[40:50].mean()
                post = nov[50:]
                peak = post.max()
                imax = int(post.argmax())
                target = pre + (peak - pre) / 2
                after = post[imax:]
                hit = np.where(after <= target)[0]
                half = int(hit[0]) if len(hit) else -1
                novs.append(float(peak - pre))
                halves.append(half)
            rows.append({
                "gamma_before": 0.5,
                "gamma_after": shock_gamma,
                "lag": lag,
                "amplitude_mean": float(np.mean(novs)),
                "half_life_median": float(np.median(halves)),
            })
    return {
        "design": "consensus-ish start; at t=50 raise gamma; novelty=1-max share; 10 seeds",
        "note": "amplitude>0 means a transient; a sustained cycle would also show repeated peaks after t=50",
        "rows": rows,
    }


def exp_swing_e4() -> dict:
    """E4: gamma_t = gamma0 + b*(novelty_{t-lag} - target).

    This is an extra assumption, not a corollary of E2. It is tested here so the
    book can either declare it (C-level) or drop the swing claim.
    """
    rows = []
    for b in (1.0, 2.0):
        for lag in (5, 10):
            periods, amps = [], []
            for seed in range(SEEDS):
                cfg = VariantConfig(
                    steps=600, gamma=1.0, kappa_mean=0.5, nu_in=0.5,
                    C=0.1, e4_b=b, e4_lag=lag,
                )
                out = variant_run(cfg, seed)
                nov = 1.0 - out["freq"].max(axis=1)
                x = nov[150:] - nov[150:].mean()
                ac = np.correlate(x, x, "full")[len(x) - 1:]
                ac = ac / ac[0]
                peaks = [i for i in range(5, len(ac) - 1) if ac[i] > ac[i - 1] and ac[i] > ac[i + 1]]
                periods.append(int(peaks[0]) if peaks else -1)
                amps.append(float(nov[150:].std()))
            rows.append({
                "b": b, "lag": lag,
                "period_median": float(np.median(periods)),
                "period_values": periods,
                "amplitude_mean": float(np.mean(amps)),
            })
    return {
        "design": "E4: gamma_t = 1.0 + b*(novelty_{t-lag}-0.5), clip [0.05,4]; 600 steps; 10 seeds",
        "note": "period = first autocorrelation peak after t=150; -1 = no peak",
        "rows": rows,
    }


def exp_trait() -> dict:
    rows = []
    for nu_in in (0.0, 1.5):
        for kappa_mean in (0.1, 1.0):
            mus, Hs, ks = [], [], []
            for seed in range(SEEDS):
                cfg = VariantConfig(nu_in=nu_in, kappa_mean=kappa_mean, gamma=0.8, C=0.2, steps=350)
                out = variant_run(cfg, seed)
                f = out["freq"][-40:].mean(axis=0)
                # circular mean of variants
                ang = 2 * np.pi * np.arange(M) / M
                mu = (np.angle(np.sum(f * np.exp(1j * ang))) * M / (2 * np.pi)) % M
                H = float(np.sum(f ** 2))
                mus.append(float(mu))
                Hs.append(H)
                ks.append(float(out["kappa"].mean()))
            rows.append({
                "nu_in": nu_in,
                "kappa_mean": kappa_mean,
                "mu": float(np.mean(mus)),
                "nu": nu_in,
                "kappa": float(np.mean(ks)),
                "H": float(np.mean(Hs)),
                "C": 0.2,
            })
    return {"design": "same 2x2; mu=circular mean, H=Herfindahl; descriptive, not a test", "rows": rows}


def binary_assim(seed: int, nu_out: float, C: float, gap: int, p_out: float = 0.05) -> float:
    rng = np.random.default_rng(seed)
    n, L = 120, 4
    G = nx.stochastic_block_model([n // 2, n - n // 2], [[0.15, p_out], [p_out, 0.15]], seed=seed)
    A = nx.to_numpy_array(G)
    nbrs = [np.where(A[i] > 0)[0] for i in range(n)]
    comm = np.array([0] * (n // 2) + [1] * (n - n // 2))
    x = np.zeros((n, L), dtype=int)
    x[comm == 1, :gap] = 1
    for _ in range(250):
        new = x.copy()
        for i in range(n):
            if len(nbrs[i]) == 0:
                continue
            j = rng.choice(nbrs[i])
            nu = 1.0 if comm[i] == comm[j] else nu_out
            p = 1.0 / (1.0 + np.exp(-(2.0 * nu - C)))
            if rng.random() < p:
                b = rng.integers(L)
                new[i, b] = x[j, b]
        x = new
    a = x[comm == 0]
    b = x[comm == 1]
    ii = rng.integers(0, len(a), 300)
    jj = rng.integers(0, len(b), 300)
    return float(1.0 - np.mean(np.abs(a[ii] - b[jj]).sum(axis=1)) / L)


def exp_assimilation(p_out: float = 0.05) -> dict:
    rows = []
    for nu_out in (0.0, 0.3, 0.8):
        for C in (0.1, 0.5):
            for gap in (1, 4):
                vals = [binary_assim(seed, nu_out, C, gap, p_out=p_out) for seed in range(SEEDS)]
                rows.append({
                    "nu_out": nu_out, "C": C, "initial_gap": gap,
                    "cross_similarity_mean": float(np.mean(vals)),
                    "cross_similarity_sd": float(np.std(vals, ddof=1)),
                })
    return {
        "design": f"two groups, 4-bit codes; bridge p_out={p_out}; 250 steps; 10 seeds",
        "note": "cross_similarity 1 = same code; 0.5 = random; 0.05 = disjoint",
        "rows": rows,
    }


def taste_run(seed: int, gamma: float, C: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    n = 120
    G = nx.watts_strogatz_graph(n, 6, 0.15, seed=seed)
    nbrs = [np.array(list(G.neighbors(i))) for i in range(n)]
    kappa = np.clip(rng.lognormal(np.log(0.5), 0.5, n), 0.02, 3.0)
    adopted = np.zeros(n, dtype=bool)
    seeds = rng.choice(n, 3, replace=False)
    adopted[seeds] = True
    t_adopt = np.full(n, 101, dtype=int)
    t_adopt[seeds] = 0
    for t in range(1, 101):
        exposure = np.array([adopted[nbrs[i]].mean() if len(nbrs[i]) else 0.0 for i in range(n)])
        p = 1.0 / (1.0 + np.exp(-(5.0 * (kappa - 0.5) + 4.0 * exposure - 2.0 * gamma - C)))
        new = (~adopted) & (rng.random(n) < p)
        adopted |= new
        t_adopt[new & (t_adopt == 101)] = t
        if adopted.all():
            break
    degree = np.array([len(x) for x in nbrs])
    return t_adopt, kappa, degree


def exp_taste() -> dict:
    rows = []
    for gamma in (0.5, 1.5):
        for C in (0.1, 0.5):
            rhos_k, rhos_d = [], []
            for seed in range(SEEDS):
                t, k, d = taste_run(seed, gamma, C)
                rk = spearmanr(t, k).statistic
                rd = spearmanr(t, d).statistic
                rhos_k.append(float(rk))
                rhos_d.append(float(rd))
            rows.append({
                "gamma": gamma, "C": C,
                "rho_kappa_mean": float(np.mean(rhos_k)),
                "rho_degree_mean": float(np.mean(rhos_d)),
                "rho_kappa_sd": float(np.std(rhos_k, ddof=1)),
                "rho_degree_sd": float(np.std(rhos_d, ddof=1)),
            })
    return {
        "design": "threshold adoption on WS(6,0.15); 3 seeds; 100 steps; 10 seeds",
        "note": "negative rho = high kappa / high degree adopt earlier",
        "rows": rows,
    }


def taste_run_strong(seed: int, gamma: float, C: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Isolate A: kappa constant, BA network, exposure = number of adopted neighbours."""
    rng = np.random.default_rng(seed)
    n = 120
    G = nx.barabasi_albert_graph(n, 3, seed=seed)
    nbrs = [np.array(list(G.neighbors(i))) for i in range(n)]
    kappa = np.full(n, 0.5)
    adopted = np.zeros(n, dtype=bool)
    seeds = rng.choice(n, 3, replace=False)
    adopted[seeds] = True
    t_adopt = np.full(n, 101, dtype=int)
    t_adopt[seeds] = 0
    for t in range(1, 101):
        exposure = np.array([adopted[nbrs[i]].sum() if len(nbrs[i]) else 0.0 for i in range(n)])
        p = 1.0 / (1.0 + np.exp(-(0.5 * exposure - 2.0 * gamma - C)))
        new = (~adopted) & (rng.random(n) < p)
        adopted |= new
        t_adopt[new & (t_adopt == 101)] = t
        if adopted.all():
            break
    degree = np.array([len(x) for x in nbrs])
    return t_adopt, kappa, degree


def exp_taste_strong() -> dict:
    rows = []
    for gamma in (0.5, 1.5):
        for C in (0.1, 0.5):
            rhos_d = []
            for seed in range(SEEDS):
                t, _, d = taste_run_strong(seed, gamma, C)
                rhos_d.append(float(spearmanr(t, d).statistic))
            rows.append({
                "gamma": gamma, "C": C,
                "rho_degree_mean": float(np.mean(rhos_d)),
                "rho_degree_sd": float(np.std(rhos_d, ddof=1)),
            })
    return {
        "design": "A-isolation: BA(3), kappa=0.5 constant, exposure=count; 100 steps; 10 seeds",
        "note": "negative rho = high degree adopts earlier; this is the strongest A test in this script",
        "rows": rows,
    }


def voi_binary(p, q: float, L_fn: float, L_fp: float):
    """Value of a binary signal for a binary decision.

    State theta in {0,1}, prior p = P(theta=1).
    Action 0 costs L_fn if theta=1; action 1 costs L_fp if theta=0.
    Signal e is correct with probability q; VOI is the expected cost reduction.
    """
    p = np.clip(np.asarray(p, dtype=float), 1e-9, 1 - 1e-9)
    cost0 = p * L_fn
    cost1 = (1.0 - p) * L_fp
    C0 = np.minimum(cost0, cost1)

    pe1 = q * p + (1.0 - q) * (1.0 - p)
    p1 = q * p / pe1
    pe0 = (1.0 - q) * p + q * (1.0 - p)
    p0 = (1.0 - q) * p / pe0

    C1_1 = np.minimum(p1 * L_fn, (1.0 - p1) * L_fp)
    C1_0 = np.minimum(p0 * L_fn, (1.0 - p0) * L_fp)
    C1 = pe1 * C1_1 + pe0 * C1_0
    return C0 - C1


def exp_voi() -> dict:
    """VOI replaces kappa*IG: the inverted U is derived, and its peak shifts."""
    rows = []
    ps = np.linspace(0.01, 0.99, 99)
    for L_fn, L_fp in ((1.0, 1.0), (5.0, 1.0), (1.0, 5.0), (9.0, 1.0)):
        v = voi_binary(ps, 0.7, L_fn, L_fp)
        peak = float(ps[int(np.argmax(v))])
        threshold = float(L_fp / (L_fn + L_fp))
        rows.append({
            "L_fn": L_fn, "L_fp": L_fp,
            "signal_accuracy": 0.7,
            "peak_p": peak,
            "decision_threshold": threshold,
            "max_voi": float(np.max(v)),
        })
    return {
        "design": "binary state/action, symmetric signal q=0.7; p grid 0.01..0.99",
        "note": "VOI is zero at p=0/1; single-peaked; peak shifts with payoff asymmetry; no Wundt curve assumed",
        "rows": rows,
    }


def main() -> None:
    payload = {
        "meta": {
            "status": "C-level constructed simulation; parameters are chosen, not estimated",
            "n": N, "variants": M, "seeds": SEEDS,
        },
        "group": exp_group(),
        "swing": exp_swing(),
        "swing_e4": exp_swing_e4(),
        "trait": exp_trait(),
        "assimilation": exp_assimilation(),
        "assimilation_strong": exp_assimilation(p_out=0.20),
        "taste": exp_taste(),
        "taste_strong": exp_taste_strong(),
        "voi": exp_voi(),
    }
    (OUT / "sim_love_curiosity.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print("wrote", OUT / "sim_love_curiosity.json")
    for k in ("group", "swing", "swing_e4", "trait", "assimilation", "assimilation_strong", "taste", "taste_strong", "voi"):
        print(k, len(payload[k]["rows"]), "rows")


if __name__ == "__main__":
    main()
