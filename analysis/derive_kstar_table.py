#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""表 6.2 的生成脚本：把切点成本 b 写进账以后，最优类别数 k* 是多少。

账（与正文一致）：
    J(k) = w·c_p/k² + (T+λ)·[ log₂k + (k−1)·b ]

做三件事：
  1) 扫 b 与 w，给 k*（一维有界最小化）；
  2) 给“赌注加倍时 k* 的倍数”——b=0 时应为 √2，与 T3 的 ½ 指数对上；
  3) 找角点：k*≈1（一刀不切）出现在哪个区间。

注意：这是把式子代进去算的算术，不是读数。c_p 归一到 1、T+λ 定为 1；
换归一化常数会移动中间列，但“倍数”一列只随 b 变。
"""
import json
from pathlib import Path

import numpy as np
from scipy.optimize import minimize_scalar

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "derived" / "kstar_table.json"

T_PLUS_LAMBDA = 1.0
C_P = 1.0


def k_star(w, b):
    f = lambda k: w * C_P / k ** 2 + T_PLUS_LAMBDA * (np.log2(k) + (k - 1) * b)
    r = minimize_scalar(f, bounds=(1.0001, 5000), method="bounded")
    return float(r.x)


def main():
    bs = [0.0, 0.1, 0.5, 1.0, 2.0]
    ws = [0.5, 1.0, 2.0, 4.0, 8.0]
    rows = []
    for b in bs:
        ks = [round(k_star(w, b), 2) for w in ws]
        ratio = k_star(2.0, b) / k_star(1.0, b)
        rows.append({"b": b, "k_star": ks, "ratio_double_w": round(ratio, 3)})
        print(f"b={b:<4} k*={ks}  赌注加倍 -> x{ratio:.3f}")

    print("\n角点（k*<1.05，即“一刀不切”）的 w 上界：")
    corners = {}
    for b in [0.5, 1.0, 2.0]:
        lo, hi = 0.01, 4.0
        for _ in range(60):
            mid = (lo + hi) / 2
            if k_star(mid, b) < 1.05:
                lo = mid
            else:
                hi = mid
        corners[b] = round(hi, 3)
        print(f"  b={b}: w < {hi:.2f}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "w_grid": ws, "b_grid": bs, "rows": rows, "corner_w": corners,
        "note": "算术，不是读数：c_p=1、T+λ=1；换常数会移动中间列，倍数只随 b 变。",
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nwrote", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
