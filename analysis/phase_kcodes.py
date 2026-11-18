"""k 码相图：份额自由能的稳定解与"极化/碎片化"的分岔。

模型（附录 A.10 的份额层）：
    F[P] = <h,P> + (γ/2) P'DP - (1/β) H(P),   H(P) = -Σ P ln P
不动点（单纯形内）：
    P_q ∝ exp{ -β ( h_q + γ (DP)_q ) }
用不动点迭代求；对每个 (β, γ) 数"稳定解"与"有效码数"。

产出：data/derived/phase_kcodes.json
"""
import json
import itertools
import numpy as np

ROOT = "data/derived"


def D_tree(k_branch=2, levels=2, w_hi=1.0, w_lo=0.4):
    """层级距离：不同大类 = hi，同类不同叶 = lo，同码 = 0。"""
    k = k_branch ** levels
    codes = list(itertools.product(range(k_branch), repeat=levels))
    D = np.zeros((k, k))
    for i, a in enumerate(codes):
        for j, b in enumerate(codes):
            if i == j:
                continue
            D[i, j] = w_hi if a[0] != b[0] else w_lo
    return D, codes


def D_uniform(k):
    D = np.ones((k, k)) - np.eye(k)
    return D


def fixed_points(D, h, beta, gamma, n_start=64, iters=400, seed=0):
    """从随机初值不动点迭代，收集不同的稳定解。"""
    k = len(h)
    rng = np.random.default_rng(seed)
    sols = []
    seeds = [np.eye(k)[i] * 0.9 + 0.1 / k for i in range(k)]
    seeds += [rng.dirichlet(np.ones(k)) for _ in range(n_start)]
    for P in seeds:
        for _ in range(iters):
            z = h + gamma * (D @ P)
            Pn = np.exp(-beta * (z - z.min()))
            Pn /= Pn.sum()
            if np.max(np.abs(Pn - P)) < 1e-10:
                P = Pn
                break
            P = Pn
        # 稳定性：F 的 Hessian 在单纯形切空间上正定？
        # F 的 Hessian：γD + (1/β)·diag(1/P)（熵项的二阶导为正）
        Hess = (1.0 / beta) * np.diag(1.0 / np.maximum(P, 1e-12)) + gamma * D
        # 投影到 ΣδP=0 的切空间
        A = np.column_stack([np.ones(k)] + [np.eye(k)[:, i] for i in range(k - 1)])
        Q, _ = np.linalg.qr(A)
        B = Q[:, 1:]
        Hr = B.T @ Hess @ B
        stable = np.all(np.linalg.eigvalsh(0.5 * (Hr + Hr.T)) > 1e-8)
        if stable:
            if not any(np.max(np.abs(P - s)) < 1e-6 for s in sols):
                sols.append(P)
    return sols


def effective_codes(P, thr=0.05):
    return int((P > thr).sum())


def sweep():
    out = {"tree_k4": [], "uniform_k4": [], "tree_k8": []}
    grids = {
        "tree_k4": (D_tree(2, 2)[0], np.array([0.0, 0.0, 0.3, 0.3])),
        "uniform_k4": (D_uniform(4), np.array([0.0, 0.0, 0.3, 0.3])),
        "tree_k8": (D_tree(2, 3)[0], np.zeros(8) + np.linspace(0, 0.4, 8)),
    }
    for name, (D, h) in grids.items():
        k = len(h)
        for bg in [0.5, 0.9, 1.5, 2.5, 4.0, 7.0]:
            # 取 beta*gamma 固定，扫 beta（=噪声温度）与 gamma 的组合
            for gamma in [1.0, 2.0, 4.0]:
                beta = bg / gamma
                sols = fixed_points(D, h, beta, gamma, n_start=48, iters=300)
                out[name].append({
                    "beta_gamma": bg, "gamma": gamma, "beta": round(beta, 4),
                    "n_solutions": len(sols),
                    "eff_codes": sorted({effective_codes(P) for P in sols}),
                    "max_share": sorted({round(float(P.max()), 3) for P in sols}),
                })
    return out


if __name__ == "__main__":
    import os
    os.makedirs(ROOT, exist_ok=True)
    res = sweep()
    with open(os.path.join(ROOT, "phase_kcodes.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    for name, rows in res.items():
        print("==", name)
        for r in rows:
            print("  βγ=%.1f γ=%.0f 解数=%d 有效码=%s 最大份额=%s"
                  % (r["beta_gamma"], r["gamma"], r["n_solutions"], r["eff_codes"], r["max_share"]))
