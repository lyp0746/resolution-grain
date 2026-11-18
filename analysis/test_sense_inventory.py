"""义项清单的五年变化：用 Open English WordNet 2019 vs 2024 做一次抽样框干净的检验。

为什么要这个：上一轮 SemEval dev 的 pilot 栽在抽样框上——目标词是按"有歧义"挑的，
频次的变异被截断。这里改用**全部词条**（不挑），变化量取"义项数变了没有"，
频次取 wordfreq 的 Zipf，控制词长与词性。

三条预言（对应 ch24 §24.9 与 A.13 ④）：
  P-a 多义↑ ⇒ 变化快（`senses_2019` 系数为正）
  P-b 频次↑ ⇒ 变化慢（`log_freq` 系数为负）
（P-c"F₀ 分档"这一版做不了：同一部词典内部 F₀ 是常数。）

产出：data/derived/sense_inventory.json
"""
import io
import json
import zipfile
import numpy as np
from scipy import stats

OLD = "data/raw/_oewn/english-wordnet-2019.zip"
NEW = "data/raw/_oewn/english-wordnet-2024.zip"
POS = ["noun", "verb", "adj", "adv"]


def parse(zip_path, prefix):
    """返回 {(lemma,pos): senses}。"""
    z = zipfile.ZipFile(zip_path)
    out = {}
    for p in POS:
        name = "%sindex.%s" % (prefix, p)
        for line in z.read(name).decode("utf-8", errors="replace").splitlines():
            if not line or line[0] == " " or line[0].isdigit():
                continue
            f = line.split()
            if len(f) < 4:
                continue
            lemma, pos, synset_cnt = f[0], f[1], f[2]
            try:
                out[(lemma.lower(), pos)] = int(synset_cnt)
            except ValueError:
                continue
    return out


def main():
    from wordfreq import zipf_frequency
    old = parse(OLD, "")
    new = parse(NEW, "oewn2024/")
    keys_old, keys_new = set(old), set(new)
    both = keys_old & keys_new
    print("义项条目：2019 %d ／ 2024 %d ／ 共有 %d ／ 新增 %d ／ 消失 %d"
          % (len(old), len(new), len(both), len(keys_new - keys_old), len(keys_old - keys_new)))
    words = sorted(both)
    n = len(words)
    s_old = np.array([old[w] for w in words])
    s_new = np.array([new[w] for w in words])
    delta = s_new - s_old
    anychg = (delta != 0).astype(int)
    rel = np.abs(delta) / np.maximum(1, s_old)
    freq = np.array([zipf_frequency(w[0].replace("_", " "), "en") for w in words])
    length = np.array([len(w[0]) for w in words])
    pos = np.array([w[1] for w in words])
    ok = freq > 0
    print("有频次的 %d / %d；义项数 2019 中位 %.0f；变化率 %.3f"
          % (ok.sum(), n, np.median(s_old), anychg.mean()))

    res = {"inventory": {"lemmas_2019": len(old), "lemmas_2024": len(new),
                         "shared": len(both), "added": len(keys_new - keys_old),
                         "dropped": len(keys_old - keys_new)},
           "n_analysis": int(ok.sum()), "any_change_rate": round(float(anychg[ok].mean()), 4)}

    # P-a / P-b：在同一批词上，看"变没变"与"变了多少"
    X = np.column_stack([np.ones(ok.sum()), freq[ok], s_old[ok], length[ok]])
    y = rel[ok]
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    dof = len(y) - X.shape[1]
    s2 = (resid @ resid) / dof
    cov = s2 * np.linalg.inv(X.T @ X)
    se = np.sqrt(np.diag(cov))
    names = ["截距", "Zipf 频次", "2019 义项数", "词长"]
    res["ols_rel_change"] = []
    for nm, b, e in zip(names, beta, se):
        t = b / e if e else np.nan
        p = 2 * (1 - stats.t.cdf(abs(t), dof)) if e else np.nan
        res["ols_rel_change"].append({"term": nm, "coef": round(float(b), 6),
                                      "se": round(float(e), 6), "p": round(float(p), 4)})
        print("  rel_change ~ %-10s coef=%+.5f se=%.5f p=%.4f" % (nm, b, e, p))

    # 只有"变没变"：用相关（更稳，因为多数词没变）
    res["spearman"] = {
        "change_vs_freq": round(float(stats.spearmanr(anychg[ok], freq[ok]).statistic), 3),
        "p_freq": round(float(stats.spearmanr(anychg[ok], freq[ok]).pvalue), 4),
        "change_vs_senses": round(float(stats.spearmanr(anychg[ok], s_old[ok]).statistic), 3),
        "p_senses": round(float(stats.spearmanr(anychg[ok], s_old[ok]).pvalue), 4),
    }
    print("  Spearman：变没变 vs 频次 ρ=%(change_vs_freq).3f (p=%(p_freq).4f)；vs 义项数 ρ=%(change_vs_senses).3f (p=%(p_senses).4f)" % res["spearman"])

    # 分层：按义项数分箱，看变化率
    bins = []
    for lo, hi in [(1, 1), (2, 2), (3, 4), (5, 9), (10, 99)]:
        m = ok & (s_old >= lo) & (s_old <= hi)
        if m.sum() > 20:
            bins.append({"senses": "%d—%d" % (lo, hi), "n": int(m.sum()),
                         "change_rate": round(float(anychg[m].mean()), 3),
                         "median_zipf": round(float(np.median(freq[m])), 2)})
    res["bins"] = bins
    for b in bins:
        print("  义项 %-6s n=%5d 变化率 %.3f 中位频次 %.2f" % (b["senses"], b["n"], b["change_rate"], b["median_zipf"]))

    with open("data/derived/sense_inventory.json", "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
