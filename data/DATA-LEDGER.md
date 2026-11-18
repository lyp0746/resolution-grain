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
