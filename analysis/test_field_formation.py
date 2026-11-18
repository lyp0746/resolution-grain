"""学科"成型"能不能算：用 Europe PMC 把第 20 章那五个指标里能取到的三个取出来。

第 20 章 §20.5 说"一个领域成没成型"要看五样（学位点、期刊、教科书、共识、卡住）。
这里取三样可自动取到的代理：
  ① 体量（每年命中数）  ② 形状（继续长还是走平）  ③ 正典集中度（前 100 高被引的 Gini）
若三个指向同一件事，"成型"就是一维的量；若彼此打架，那五个指标就不是一个东西。

字段清单**先写死**（成形 5／有争议 4／前范式 2），不按结果挑。
覆盖：Europe PMC 以生物医学为主——**这是一次"在一个库里"的检验**，不是全学科普查。
产出：data/derived/field_formation.json
"""
import json
import os
import time
import requests
import numpy as np
from scipy import stats

BASE = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
CACHE = "data/raw/_epmc"
S = requests.Session()
S.headers.update({"User-Agent": "research-check/1.0"})

FIELDS = {
    "分子生物学": ("molecular biology", "成形"),
    "流行病学": ("epidemiology", "成形"),
    "有机合成": ("organic synthesis", "成形"),
    "凝聚态": ("condensed matter", "成形"),
    "气候影响": ("climate change", "成形"),
    "营养学": ("nutrition", "有争议"),
    "意识研究": ("consciousness", "有争议"),
    "迷幻药": ("psychedelic", "有争议"),
    "精神病分类": ("psychiatric classification", "有争议"),
    "微塑料": ("microplastics", "前范式"),
    "肠道菌群": ("gut microbiome", "前范式"),
}
YEARS = list(range(2000, 2025))


def count(q, year):
    key = os.path.join(CACHE, "c_%s_%d.json" % (q.replace(" ", "_"), year))
    if os.path.exists(key):
        return json.load(open(key))["n"]
    for a in range(3):
        try:
            r = S.get(BASE, params={"query": '(TITLE_ABS:"%s") AND (PUB_YEAR:%d)' % (q, year),
                                    "format": "json", "pageSize": 1}, timeout=30)
            if r.status_code == 200:
                n = r.json()["hitCount"]
                os.makedirs(CACHE, exist_ok=True)
                json.dump({"q": q, "year": year, "n": n}, open(key, "w"))
                return n
        except Exception:
            pass
        time.sleep(0.6 + a)
    return None


def top100(q):
    key = os.path.join(CACHE, "t_%s.json" % q.replace(" ", "_"))
    if os.path.exists(key):
        return json.load(open(key))
    for a in range(3):
        try:
            r = S.get(BASE, params={"query": '(TITLE_ABS:"%s") AND (PUB_YEAR:[2016 TO 2024])' % q,
                                    "format": "json", "pageSize": 100,
                                    "sort": "CITED desc", "resultType": "core"}, timeout=40)
            if r.status_code == 200:
                d = [x.get("citedByCount", 0) for x in r.json()["resultList"]["result"]]
                os.makedirs(CACHE, exist_ok=True)
                json.dump(d, open(key, "w"))
                return d
        except Exception:
            pass
        time.sleep(0.8 + a)
    return []


def gini(x):
    x = np.sort(np.asarray(x, dtype=float))
    n = len(x)
    if n == 0 or x.sum() == 0:
        return float("nan")
    i = np.arange(1, n + 1)
    return float(2 * (i * x).sum() / (n * x.sum()) - (n + 1) / n)


if __name__ == "__main__":
    rows = []
    for name, (q, label) in FIELDS.items():
        v = np.array([count(q, y) or 0 for y in YEARS], dtype=float)
        v = np.maximum(v, 1)
        g1 = (v[15] / v[0]) ** (1 / 15) - 1
        g2 = (v[24] / v[15]) ** (1 / 9) - 1
        dl = np.diff(np.log(v))
        vola = float(dl.std() / max(abs(dl.mean()), 1e-9))
        c = top100(q)
        gi = gini(c) if len(c) >= 30 else float("nan")
        rows.append({"field": name, "label": label, "query": q,
                     "volume_2024": int(v[24]), "growth_2000_2015": round(float(g1), 4),
                     "growth_2015_2024": round(float(g2), 4),
                     "volatility": round(float(vola), 3),
                     "canon_gini": round(float(gi), 3)})
        print("%-9s %-5s 2024=%6d g1=%+.3f g2=%+.3f vola=%.2f gini=%.3f"
              % (name, label, v[24], g1, g2, vola, gi))
    json.dump(rows, open("data/derived/field_formation.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    # 三个指标之间是否指向同一件事
    g1 = np.array([r["growth_2000_2015"] for r in rows])
    g2 = np.array([r["growth_2015_2024"] for r in rows])
    vo = np.array([r["volume_2024"] for r in rows], dtype=float)
    gi = np.array([r["canon_gini"] for r in rows])
    print("\nSpearman：g1 vs g2 %.2f | 体量 vs g2 %.2f | gini vs g2 %.2f | gini vs 体量 %.2f"
          % (stats.spearmanr(g1, g2).statistic, stats.spearmanr(vo, g2).statistic,
             stats.spearmanr(gi, g2).statistic, stats.spearmanr(gi, vo).statistic))
