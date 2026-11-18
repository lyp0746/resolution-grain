"""两条语义变化律：用公开数据复现一次（不是新证据，是"目标对不对"的检查）。

数据：SemEval-2020 Task 1 的公开 dev 真值（Zenodo 3931969，posteval 包），
      四语言各 37 个目标词；两条真值文件：task1（二分类 0/1）与 task2（连续 0—1）。
频次：wordfreq 的 Zipf 频次（离线，按语种）。
多义：WordNet 同义词集数（只对英语可用）。
读数：Spearman 相关（change vs 频次，预期为负；change vs 多义，预期为正）＋ n。
"""
import io
import json
import os
import zipfile
import numpy as np
from scipy import stats

ZIP = "data/raw/_semeval/semeval2020_ulscd_posteval.zip"
LANGS = ["english", "german", "latin", "swedish"]
WF = {"english": "en", "german": "de", "swedish": "sv"}


def read_truth(lang, task):
    z = zipfile.ZipFile(ZIP)
    p = "semeval2020_ulscd_posteval/test_data_truth/%s/%s.txt" % (task, lang)
    rows = []
    for line in z.read(p).decode("utf-8").splitlines():
        if not line.strip():
            continue
        w, v = line.split("\t")
        rows.append((w, float(v)))
    return rows


def base(word):
    w = word.split("_")[0]
    return w.replace("-", " ")


def senses(word):
    from nltk.corpus import wordnet as wn
    w = base(word)
    pos = word.split("_")[1] if "_" in word else None
    m = {"nn": wn.NOUN, "vb": wn.VERB, "jj": wn.ADJ, "rb": wn.ADV}.get(pos)
    try:
        return len(wn.synsets(w, m)) if m else len(wn.synsets(w))
    except Exception:
        return 0


def main():
    import nltk
    nltk.data.path.insert(0, os.path.abspath("_temp/nltk_data"))
    from wordfreq import zipf_frequency
    out = {"note": "dev 真值（37 词/语种）；非新证据，只检验两条律在此数据上是否同向", "rows": []}
    for lang in LANGS:
        try:
            t2 = read_truth(lang, "task2")
        except KeyError:
            continue
        t1 = dict(read_truth(lang, "task1"))
        words = [w for w, _ in t2]
        chg = np.array([v for _, v in t2])
        fr = np.array([zipf_frequency(base(w), WF.get(lang, "en")) for w in words])
        row = {"lang": lang, "n": len(words)}
        ok = fr > 0
        row["spearman_change_vs_freq"] = round(float(stats.spearmanr(chg[ok], fr[ok]).statistic), 3)
        row["p_freq"] = round(float(stats.spearmanr(chg[ok], fr[ok]).pvalue), 4)
        if lang == "english":
            sn = np.array([senses(w) for w in words])
            row["spearman_change_vs_senses"] = round(float(stats.spearmanr(chg, sn).statistic), 3)
            row["p_senses"] = round(float(stats.spearmanr(chg, sn).pvalue), 4)
            # 二元分类上的同一检查（更大间距）
            y = np.array([t1.get(w, np.nan) for w in words])
            okb = (~np.isnan(y)) & ok
            if okb.sum() > 5:
                row["binary_mean_freq_changed"] = round(float(fr[okb & (y == 1)].mean()), 2)
                row["binary_mean_freq_stable"] = round(float(fr[okb & (y == 0)].mean()), 2)
        out["rows"].append(row)
        print(json.dumps(row, ensure_ascii=False))
    with open("data/derived/semchange_laws.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
