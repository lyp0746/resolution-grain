"""使用层面的语义变化：两条律在"词向量"上的检验（CCOHA 两期 + 英/美两社区）。

数据：Zenodo 3890109 `wordvectors.zip` 里的 SemEval 两期英文向量（corpus1 1810—1860，
corpus2 1960—2010）与 BNC/COCA（英／美）向量。
做法：取两期的共同词表 → 正交 Procrustes 对齐 → 变化量 = 1 − cos。
协变量：wordfreq 的 Zipf 频次、WordNet 义项数、词长。
预言：P-a 多义↑ ⇒ 变化↑；P-b 频次↑ ⇒ 变化↓。

产出：data/derived/usage_change.json
"""
import io
import json
import zipfile
import numpy as np
from scipy import stats

ZIP = "data/raw/_wordvec/wordvectors.zip"


def load_vec(path, min_len=2, max_words=None):
    words, vecs = [], []
    z = zipfile.ZipFile(ZIP)
    with z.open(path) as fh:
        first = True
        for raw in io.TextIOWrapper(fh, encoding="utf-8", errors="replace"):
            p = raw.rstrip("\n").split(" ")
            if first:
                first = False
                continue          # 文件头形如 "2 11426 300"，一律跳过
            if len(p) < 10:
                continue
            w = p[0]
            if not w.isalpha() or not w.islower() or len(w) < min_len:
                continue
            words.append(w)
            vecs.append(np.asarray(p[1:], dtype=np.float32))
            if max_words and len(words) >= max_words:
                break
    return words, np.vstack(vecs)


def align_rotation(X, Y):
    """正交 Procrustes：求旋转 W，使 X W ≈ Y。"""
    U, _, Vt = np.linalg.svd(X.T @ Y, full_matrices=False)
    return U @ Vt


def analyse(pair, tag):
    from wordfreq import zipf_frequency
    from nltk.corpus import wordnet as wn
    w1, X1 = load_vec(pair[0])
    w2, X2 = load_vec(pair[1])
    i1 = {w: i for i, w in enumerate(w1)}
    i2 = {w: i for i, w in enumerate(w2)}
    common = sorted(set(i1) & set(i2))
    print("[%s] vocab %d / %d, common %d" % (tag, len(w1), len(w2), len(common)))
    A = X1[[i1[w] for w in common]]
    B = X2[[i2[w] for w in common]]
    A /= np.linalg.norm(A, axis=1, keepdims=True)
    B /= np.linalg.norm(B, axis=1, keepdims=True)
    # 在对齐子集上估计旋转（用频次最高的 2 万词，避免低频噪声主导）
    fr = np.array([zipf_frequency(w, "en") for w in common])
    ref = np.argsort(-fr)[:20000]
    W = align_rotation(A[ref], B[ref])
    Aa = A @ W
    Aa /= np.linalg.norm(Aa, axis=1, keepdims=True)
    cos = (Aa * B).sum(1)
    change = 1.0 - cos
    ok = fr > 0
    words = [w for w, k in zip(common, ok) if k]
    change, fr = change[ok], fr[ok]
    sens = np.array([len(wn.synsets(w)) for w in words])
    ln = np.array([len(w) for w in words])
    out = {"tag": tag, "n": int(ok.sum()),
           "median_change": round(float(np.median(change)), 4),
           "spearman_change_vs_freq": round(float(stats.spearmanr(change, fr).statistic), 3),
           "p_freq": round(float(stats.spearmanr(change, fr).pvalue), 6),
           "spearman_change_vs_senses": round(float(stats.spearmanr(change, sens).statistic), 3),
           "p_senses": round(float(stats.spearmanr(change, sens).pvalue), 6)}
    # 多元回归：change ~ 1 + freq + senses + len
    X = np.column_stack([np.ones(len(change)), fr, sens, ln])
    beta, *_ = np.linalg.lstsq(X, change, rcond=None)
    resid = change - X @ beta
    dof = len(change) - X.shape[1]
    s2 = resid @ resid / dof
    cov = s2 * np.linalg.inv(X.T @ X)
    se = np.sqrt(np.diag(cov))
    terms = []
    for nm, b, e in zip(["截距", "Zipf 频次", "WordNet 义项数", "词长"], beta, se):
        t = b / e
        p = 2 * (1 - stats.t.cdf(abs(t), dof))
        terms.append({"term": nm, "coef": round(float(b), 5), "p": round(float(p), 5)})
    out["ols"] = terms
    for t in terms:
        print("   %-12s coef=%+.5f p=%.5f" % (t["term"], t["coef"], t["p"]))
    print("   Spearman: change vs freq ρ=%.3f (p=%.2e); vs senses ρ=%.3f (p=%.2e)"
          % (out["spearman_change_vs_freq"], out["p_freq"],
             out["spearman_change_vs_senses"], out["p_senses"]))
    # 落盘到词粒度（"以后要按行对齐"的分析都靠它）
    with open("data/derived/usage_change_%s.csv" % tag.split()[0].replace("(", "").replace("/", "_"), "w", encoding="utf-8") as f:
        f.write("word\tchange\tzipf\tsenses\tlength\n")
        for w, c, z, se, L in zip(words, change, fr, sens, ln):
            f.write("%s\t%.6f\t%.3f\t%d\t%d\n" % (w, c, z, se, L))

    # 分箱：按义项数
    bins = []
    for lo, hi in [(0, 0), (1, 1), (2, 2), (3, 4), (5, 9), (10, 99)]:
        m = (sens >= lo) & (sens <= hi)
        if m.sum() > 200:
            bins.append({"senses": "%d—%d" % (lo, hi), "n": int(m.sum()),
                         "mean_change": round(float(change[m].mean()), 4)})
    out["bins"] = bins
    for b in bins:
        print("   义项 %-6s n=%6d 平均变化 %.4f" % (b["senses"], b["n"], b["mean_change"]))
    return out


if __name__ == "__main__":
    import os
    os.makedirs("data/derived", exist_ok=True)
    import nltk
    nltk.data.path.insert(0, os.path.abspath("_temp/nltk_data"))
    res = []
    res.append(analyse(("wordvectors/semeval/english-corpus1.vec",
                        "wordvectors/semeval/english-corpus2.vec"), "CCOHA 1810—1860 vs 1960—2010"))
    res.append(analyse(("wordvectors/ukus/bnc.vec", "wordvectors/ukus/coca.vec"), "BNC(英) vs COCA(美)"))
    with open("data/derived/usage_change.json", "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
