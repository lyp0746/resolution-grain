# 已删除的数据清单（2026-11-16）

> 删除不是归档：这些文件已经不在盘上。**凭本表的 URL 与 SHA256 可重新取得**，
> 而所有派生读数（`data/derived/`）都已落盘且可由脚本重跑。

| 路径 | 文件数 | 大小 | SHA256（首文件或登记值） | 重新取得 | 为什么删 |
|---|---|---|---|---|---|
| `data/raw/datasets/ess_full` | 1 | 1798.4 MB | `b97b9f9be4b8f9cd…` | 见 `MANIFEST*.tsv` | ESS 11 轮全量（α 已判不可识别；信任滞后已测不可判） |
| `data/raw/datasets/kg_rmrb.zip` | 1 | 252.9 MB | `c2b829b3e459da8a…` | 见 `MANIFEST*.tsv` | 人民日报全文 130,186 篇（π_L / κ / p / 码率四个产出已落盘） |
| `data/raw/wid` | 3 | 90.4 MB | `(见 MANIFEST)…` | 见 `MANIFEST*.tsv` | WID 财富份额（世界/中国/美国） |
| `data/raw/datasets/kg_news2016.zip` | 1 | 8.8 MB | `9a994d21d9e7a1a4…` | 见 `MANIFEST*.tsv` | 早期探针，未进任何结论 |
| `data/raw/datasets/kg_weibo2024.zip` | 1 | 6.9 MB | `7ce3cc972c451c33…` | 见 `MANIFEST*.tsv` | 早期探针，未进任何结论 |
| `data/raw/datasets/kg_weibotext.zip` | 1 | 6.9 MB | `53ff63901d023a00…` | 见 `MANIFEST*.tsv` | 早期探针，未进任何结论 |
| `data/raw/datasets/kg_hotlists.zip` | 1 | 6.6 MB | `ca56c66fa562e3c8…` | 见 `MANIFEST*.tsv` | 三平台小时榜 5 天切片（仅示例，结论已进 INSPECT） |
| `data/raw/local/20260630201600.ngrams.txt.gz` | 1 | 8.2 MB | `3ac1df0285ccbe04…` | `(file provided by author)` | 来源未定，未用于任何结论 |

**合计释放 2.18 GB。**

**2026-11-17 追加（本轮）**：`data/raw/_wordvec/wordvectors.zip`，1 个文件，**476.1 MB**，SHA256 `19259678911fcffcf6a289ee7610cba8…`（全值在 `MANIFEST_DATASETS.tsv` 的 `wordvectors_semshift` 行），URL `https://zenodo.org/api/records/3890109/files/wordvectors.zip/content`。
**为什么删**：只用来算一次"使用层面的语义变化"（CCOHA 两期 ＋ BNC/COCA），派生读数 `data/derived/usage_change.json` 已落盘、可由 `analysis/test_usage_change.py` 重跑。
**第二轮曾在 2026-11-18 重新取回同一文件一次**（为存 per-word 派生），取回后再次删除；per-word 表已落盘：`data/derived/usage_change_CCOHA.csv`（7,943 词，215 KB）、`data/derived/usage_change_BNC英).csv`（25,305 词，706 KB）。
**顺带保留的小件**：`data/raw/_oewn/*.zip`（两版词网，各约 10 MB，小，留着便于复算）；`data/raw/_semeval/*.zip`（4.2 MB）。

## 删除前的最后三次分析（都已做完）

| 分析 | 结果 | 落盘 |
|---|---|---|
| 信任滞后于收益？（ESS × Maddison） | r_同期=+0.087，r_滞后=−0.044，**不可判** | `data/derived/trust_lag.csv` |
| α 可识别性（ESS 11 轮） | 不可识别（已删参数） | `data/derived/alpha_ess.json` |
| WID 财富份额 | 全球前 1% 36.8%→36.6%（三十年基本没动） | `data/derived/wid_wealth_share.csv` |
---

## 未入仓的引用（不是"删了"，是"从来没进仓"）

> 按第 5 条数据纪律：一个数要么有 URL＋SHA256 的行，要么在正文里标成"量级引用"。
> 下面是第二版（`source-v2/`）里出现、但**仓里没有文件、也没有记账行**的引用。逐条记，不补白。

| 出处 | 用在 | 数值 | 状态 |
|---|---|---|---|
| Credit Suisse／UBS《全球财富报告》（各年度） | `source-v2/ch27.html` 表 27.1 第二列 | 前 1% 约 **44%**（家庭调查口径） | **未入仓**：只作"另一个口径的量级"用；若要引用具体年度，须先取回并记 URL＋SHA256 |
| 美国 CMS 的 ICD-9-CM／ICD-10-CM 码表 | `source-v2/ch27.html` 表 27.1 | 约 1.5 万 → 约 7 万条 | **未入仓**：只用"量级"；码表逐年微调，出版物里也只写量级 |
| 含铅汽油的暴露—反应与全球停用年份 | `source-v2/ch28.html` §28.2 | 五人死亡、1976—80 年血铅约 15 µg/dL、2021 年全球停用 | **部分入仓**：文献条目在章节里，原始文件未入仓（只用方向） |
| 各政体采纳公历年表 | `source-v2/ch23`／`ch29` | 125 个国家、1570—2016 | **已入仓**：`data/derived/gregorian_adoption.json`（源文件为公开年表整理，见该 JSON 的 `source` 字段） |

**口径**：上表四行里，只有第四行是"可重跑"的；前三行在正文里都已写成量级或方向，没有写成精确数。
