"""词汇的复制子：一个最小模型（附录 A.13 的数值版，C 级构造）。

为什么要有"需求异质"这一层：如果所有人需要同一件事，那么各自最优码会重合，
词汇加一个码几乎没有收益——这一点先跑出来过（增益恒为零）。现实里词汇之所以多，
是因为**要伺候的需求不是同一种**。所以模型里有两类对象：
  · 需求 n = 1..N：每种需求有自己"最合身"的码（离它最近的那个叶子）
  · 码 q = 1..8：层级树上的叶子，彼此误解代价有高有低（同支便宜、异支贵）
每一步：
  ① 每种需求的代理人从当前词汇 Q_t 里挑一个码（离自己越近越好；再加一致性代价 γ）
  ② 提案：以一个外生率 π，某个"用得最不合身"的需求提它的合身码，成本 F0
  ③ 采纳：只有当"这个需求能省下的失真 × 它的份额"超过 F0 才进来（P4/A.5 的比较）
  ④ 退出：连续 3 期没有任何需求使用的码退出（于是词汇有**棘轮**：进要付钱，出要时间）
产出：data/derived/vocab_replicator.json
"""
import json
import itertools
import numpy as np

rng = np.random.default_rng(2026)
LEVELS = 3
K = 2 ** LEVELS
LEAVES = list(itertools.product(range(2), repeat=LEVELS))
T = 800


def tree_D():
    D = np.zeros((K, K))
    for i, x in enumerate(LEAVES):
        for j, y in enumerate(LEAVES):
            if i == j:
                continue
            same = sum(x[k] == y[k] for k in range(LEVELS))
            D[i, j] = {0: 1.0, 1: 0.7, 2: 0.35, 3: 0.0}[same]
    return D


D = tree_D()


def make_needs(N, seed=3):
    """每种需求 = 一个偏好向量（对 8 个leaf的合身度），并给一个质量分布。"""
    r = np.random.default_rng(seed)
    base = r.dirichlet(np.ones(K) * 0.4, size=N)      # 偏好尖的
    pref = 1.0 - base                                 # 越小越合身
    mass = r.dirichlet(np.ones(N) * 1.0)
    return pref, mass


def run(F0, pi, gamma=1.2, N=10, pref=None, mass=None):
    if pref is None:
        pref, mass = make_needs(N)
    active = set(range(4))            # 起手四个叶子
    idle = {q: 0 for q in range(K)}
    entered = exited = 0
    sizes = []
    for t in range(T):
        # ① 每种需求挑当前词汇里最合身的码（加一致性代价：偏离多数要付 gamma×被用份额之外的成本）
        use = {}
        for n in range(N):
            best, bestv = None, 1e9
            for q in active:
                v = pref[n, q]          # 只用"合身度"；一致性代价在均衡里是共同项，此处不计
                if v < bestv:
                    best, bestv = q, v
            use[n] = (best, bestv)
        # ② 提案：最不合身的那一种，提出自己的合身码
        if rng.random() < pi:
            n = max(range(N), key=lambda i: use[i][1])
            want = int(np.argmin(pref[n]))
            if want not in active:
                # ③ 采纳：这个需求能省下的失真 × 它的份额 > F0
                gain = mass[n] * (use[n][1] - pref[n, want])
                if gain > F0:
                    active.add(want)
                    entered += 1
        # ④ 退出
        used = {q for q, _ in use.values()}
        for q in list(active):
            if q not in used:
                idle[q] += 1
                if idle[q] >= 3:
                    active.discard(q)
                    idle[q] = 0
                    exited += 1
        sizes.append(len(active))
    return {"F0": F0, "pi": pi, "N": N, "size_final": len(active),
            "size_max": max(sizes), "entered": entered, "exited": exited,
            "turnover_per_100": round(100 * (entered + exited) / T, 2),
            "frozen": int(len(set(sizes[-200:])) == 1)}


if __name__ == "__main__":
    pref, mass = make_needs(10)
    rows = []
    for F0 in [0.0, 0.005, 0.01, 0.02, 0.05, 0.1]:
        for pi in [0.05, 0.2]:
            r = run(F0, pi, pref=pref, mass=mass)
            rows.append(r)
            print("F0=%.3f π=%.2f 末词汇=%d（峰 %d） 进=%d 出=%d 换手/100=%.2f 冻结=%d"
                  % (F0, pi, r["size_final"], r["size_max"], r["entered"],
                     r["exited"], r["turnover_per_100"], r["frozen"]))
    # 需求更多时
    pref2, mass2 = make_needs(16, seed=11)
    r = run(0.01, 0.2, N=16, pref=pref2, mass=mass2)
    print("N=16 F0=0.01 π=0.2 末词汇=%d（峰 %d）" % (r["size_final"], r["size_max"]))
    rows.append(r)
    with open("data/derived/vocab_replicator.json", "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)
