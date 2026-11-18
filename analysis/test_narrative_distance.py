#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""把「争议」变成一个可算的量：跨国叙事之间的编码距离。

为什么必须做这个
  作者要求加入「古今中外争议大的历史段」。可「争议大」如果只是一个形容词，
  它在书里就只能进附录的 C 级。
  但在这个框架里它有一个精确形式：**同一个事件，不同共同体维护着不同的公共码 `q̄_A`、`q̄_B`。**
  于是「争议」= 码之间的距离：

     争议(A,B) = D(q̄_A, q̄_B) = 1 − |E_A ∩ E_B| / |E_A ∪ E_B|

  `E_L` = 某语言版本条目实际链接的实体集合（用 Wikidata QID 对齐，跨语言可比）。

为什么用链接而不是文本
  文本距离受语言、篇幅、修辞影响，几乎不可比；**链接的实体是结构**——
  它回答"这段叙事把这件事和什么放在一起"。这正是划分 `q` 的样子。

输出
  data/derived/narrative_distance.csv   event, pair, n_A, n_B, jaccard, distance

纪律
  - 只用公开 API，不抓正文，不做内容判断
  - 结果只说明"结构差异有多大"，不说明"谁对"
  - 采样上限：每语言最多取 500 个链接（API 上限），须在正文注明
"""
from __future__ import annotations

import itertools
import time
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "derived" / "narrative_distance.csv"
H = {"User-Agent": "RuleEnergyInfo/0.2 (academic research)"}

EVENTS = {
    "甲午战争": {"zh": "甲午战争", "ja": "日清戦争", "en": "First Sino-Japanese War", "ko": "청일 전쟁"},
    "朝鲜战争": {"zh": "朝鲜战争", "en": "Korean War", "ko": "한국 전쟁", "ru": "Корейская война"},
    "蒙古帝国": {"zh": "蒙古帝国", "en": "Mongol Empire", "ru": "Монгольская империя", "ja": "モンゴル帝国"},
}
MAX_LINKS = 500


LOUD = {"err": 0}


def api(lang: str, params: dict, tries: int = 5) -> dict:
    last = None
    for k in range(tries):
        try:
            r = requests.get(f"https://{lang}.wikipedia.org/w/api.php", params=params,
                             headers=H, timeout=60)
            if r.status_code == 200:
                return r.json()
            last = f"HTTP {r.status_code}"
        except Exception as e:  # noqa: BLE001
            last = f"{type(e).__name__}"
        time.sleep(2 + 3 * k)
    LOUD["err"] += 1
    print(f"    [warn] {lang} 失败 {tries} 次：{last}")
    return {}


def links_of(lang: str, title: str) -> list[str]:
    out, cont = [], {}
    while len(out) < MAX_LINKS:
        p = {"action": "query", "prop": "links", "titles": title, "pllimit": "max",
             "plnamespace": 0, "format": "json", "redirects": 1, **cont}
        j = api(lang, p)
        pages = j.get("query", {}).get("pages", {})
        if not pages:
            break
        pg = list(pages.values())[0]
        out += [l["title"] for l in pg.get("links", [])]
        if "continue" in j:
            cont = j["continue"]
        else:
            break
    return out[:MAX_LINKS]


def qids(lang: str, titles: list[str]) -> set[str]:
    """把标题批量映射到 Wikidata QID（每批 50）。"""
    got = set()
    for i in range(0, len(titles), 50):
        batch = titles[i:i + 50]
        j = api(lang, {"action": "query", "prop": "pageprops", "ppprop": "wikibase_item",
                       "titles": "|".join(batch), "format": "json", "redirects": 1})
        for pg in j.get("query", {}).get("pages", {}).values():
            q = pg.get("pageprops", {}).get("wikibase_item")
            if q:
                got.add(q)
        time.sleep(0.3)
    return got


def main() -> None:
    rows = []
    for event, langs in EVENTS.items():
        sets = {}
        for lang, title in langs.items():
            ls = links_of(lang, title)
            sets[lang] = qids(lang, ls)
            print(f"  {event} / {lang}: {len(ls)} links → {len(sets[lang])} QIDs")
        for a, b in itertools.combinations(sorted(sets), 2):
            A, B = sets[a], sets[b]
            if not A or not B:
                continue
            jac = len(A & B) / len(A | B)
            rows.append({"event": event, "a": a, "b": b, "n_a": len(A), "n_b": len(B),
                         "shared": len(A & B), "jaccard": round(jac, 4),
                         "distance": round(1 - jac, 4)})
        time.sleep(1)

    d = pd.DataFrame(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    d.to_csv(OUT, index=False, encoding="utf-8-sig")
    print(f"\n{'事件':10}{'语言对':10}{'共享':>6}{'Jaccard':>9}{'距离':>8}")
    for _, r in d.iterrows():
        print(f"{r.event:10}{r.a + '–' + r.b:12}{r.shared:6d}{r.jaccard:9.3f}{r.distance:8.3f}")
    print("→", OUT)


if __name__ == "__main__":
    main()
