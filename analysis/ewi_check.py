"""临界慢化：从合成序列里恢复 τ 与 1/(1-βzγ) 的关系（早期预警信号的可行性检查）。

平均场的一阶展开：m 偏离稳定点 m* 时
    dm/dt = -κ (m - m*) + σ ξ,     κ = [1 - βzγ·sech²(β(zγm*+h))]/τ0
    AR(1) = exp(-κ Δt)   ⇒  τ_relax = 1/κ,   AR(1) 越接近 1，越接近阈值
本脚本：固定 σ，扫 βzγ（即离阈值多远），数出 var 与 AR(1)。
"""
import json
import numpy as np

rng = np.random.default_rng(11)
DT = 0.05
STEPS = 40000
BURN = 5000


def simulate(beta_z_gamma, sigma=0.12, tau0=1.0, h=0.0):
    def f(m):
        return np.tanh(beta_z_gamma * m + h)

    # 找 m*：单调时用不动点迭代
    m = 0.5 if beta_z_gamma < 1 else 0.9
    for _ in range(2000):
        m_new = f(m)
        if abs(m_new - m) < 1e-12:
            break
        m = 0.5 * (m + m_new)
    m = m_new
    q = beta_z_gamma * (1 - m * m)     # βzγ·sech²
    kappa = max(1e-6, (1 - q) / tau0)
    out = np.empty(STEPS)
    x = m
    for t in range(STEPS):
        x += DT * (-kappa * (x - m)) + sigma * np.sqrt(DT) * rng.standard_normal()
        out[t] = x
    return out[BURN:], kappa, m


def acf1(x):
    x = x - x.mean()
    return float(np.corrcoef(x[:-1], x[1:])[0, 1])


if __name__ == "__main__":
    rows = []
    for bg in [0.2, 0.5, 0.8, 0.9, 0.95, 0.98]:
        x, kappa, m = simulate(bg)
        rows.append({
            "beta_z_gamma": bg,
            "m_star": round(float(m), 4),
            "kappa": round(float(kappa), 4),
            "tau_relax": round(float(1 / kappa), 3),
            "var": round(float(x.var()), 5),
            "ar1": round(acf1(x), 4),
            "tau_from_ar1": round(float(-DT / np.log(acf1(x))), 3),
        })
    with open("data/derived/ewi_check.json", "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)
    for r in rows:
        print("βzγ=%.2f  m*=%.3f  κ=%.3f  τ=%.2f  var=%.4f  AR1=%.3f  τ(AR1)=%.2f"
              % (r["beta_z_gamma"], r["m_star"], r["kappa"], r["tau_relax"],
                 r["var"], r["ar1"], r["tau_from_ar1"]))
