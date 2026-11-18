#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A17：内容那一格能不能用模拟填一半——“分类博弈”跑一次。

背景（别人的研究，本书只借最小的一份）
  - Steels (1995)：命名博弈，标签是任意的，共享靠局部协商长出来。
  - Baronchelli et al. (2006)：N 个个体、局部协商，词汇共享是一个**突然**的相变。
  - Puglisi, Baronchelli & Loreto (2008)：把“名字”换成“类别”，类别边界也会自己长出来。
  - Kirby (2001)、Regier et al. (2007)：传递瓶颈与“最优划分”决定类别落在哪儿。

本书要问的是**自己那一格**：A.13 说“通了形式，没通内容”。这一节用三个模拟把它拆开：
  E1 **标签是任意的**：同一套参数、不同随机种子，胜出的标签不同，但都稳定 ⇒ 内容是
     **规范自由度**（gauge），不是从公设推出来的。
  E2 **没有锚就会漂**：每代换掉 10% 的个体，标签在共同体里**漂移**（无外部锚），而类别的
     数量稳定 ⇒ 正是第 10 章“码的折旧”。
  E3 **类别数由价格定**：失败代价 w 抬高 ⇒ 平均类别数上升。拟合 log k ~ log w 的指数，
     与 6.14 的两条律（1/2 或 1/3）比。

输出 data/derived/naming_game.json
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "derived" / "naming_game.json"



def naming_game(n: int = 60, k: int = 6, rounds: int = 60000, turnover: float = 0.0,
                seed: int = 0) -> dict:
    """环状局部协商的命名博弈：k 个格固定，只有标签（内容）在动。"""
    rng = np.random.default_rng(seed)
    vocab = [f"L{i}" for i in range(1, 4 * n + 1)]
    codes = [list(rng.choice(vocab, size=k, replace=False)) for _ in range(n)]
    succ = 0
    total = 0
    consensus_time = None
    win_history = []
    for t in range(rounds):
        i = int(rng.integers(n))
        j = (i + 1) % n if rng.random() < 0.5 else (i - 1) % n
        b = int(rng.integers(k))
        total += 1
        if codes[i][b] == codes[j][b]:
            succ += 1
        else:
            if rng.random() < 0.5:
                codes[j][b] = codes[i][b]
            else:
                codes[i][b] = codes[j][b]
        if turnover and rng.random() < turnover / k:
            codes[int(rng.integers(n))] = list(rng.choice(vocab, size=k, replace=False))
        if t % (rounds // 30) == 0:
            from collections import Counter
            # 逐格共识：每个格子里最常见标签的占比，再对格取平均
            share = float(np.mean([Counter(code[b] for code in codes).most_common(1)[0][1] / n
                                   for b in range(k)]))
            win_history.append(round(share, 3))
            if consensus_time is None and share > 0.9:
                consensus_time = t
    from collections import Counter
    winners = [Counter(code[b] for code in codes).most_common(1)[0][0] for b in range(k)]
    per_bin = [round(Counter(code[b] for code in codes).most_common(1)[0][1] / n, 3)
               for b in range(k)]
    c = Counter(x for code in codes for x in code)
    return {"n": n, "k": k, "success_rate": round(succ / total, 3),
            "consensus_round": consensus_time,
            "winning_labels_per_bin": winners, "per_bin_consensus": per_bin,
            "mean_per_bin_consensus": round(float(np.mean(per_bin)), 3),
            "n_distinct_labels": len(c), "trace": win_history}


def main() -> None:
    res: dict = {}
    res["E1_arbitrary"] = {
        "same_params_different_seeds": [naming_game(n=40, k=6, rounds=40000, seed=s) for s in (1, 2, 3)],
        "note": "参数完全相同，只有随机种子不同——胜出的标签不同，这就是“内容”的规范自由度",
    }
    res["E2_scaling"] = [naming_game(n=n, rounds=200000, seed=5) for n in (20, 40, 80, 160)]
    res["E3_turnover"] = {
        "none": naming_game(n=40, rounds=60000, turnover=0.0, seed=9),
        "low": naming_game(n=40, rounds=60000, turnover=0.002, seed=9),
        "high": naming_game(n=40, rounds=60000, turnover=0.01, seed=9),
    }
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=1)[:2500])


if __name__ == "__main__":
    main()
