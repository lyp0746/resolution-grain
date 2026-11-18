# 粗码（resolution-grain）

> **DOI**：10.5281/zenodo.24339910（概念 DOI：10.5281/zenodo.24339909）
> **副题**：为什么越省力分得越粗，而核实总是慢半拍
> **状态**：在建。数据层已完备，正文未起笔。
> 结构服从 `_series/spec/skeleton.md`（v2 冻结版）：**7 部分 × 4 章 = 28 章**（上限），正文 150,000—180,000 汉字。

---

## 这本书在讲什么

一句话：**同一份省力，在宽环境里表现为隧道视野，在窄环境里表现为糊成一片。**

> 书名定为《粗码》，副题“为什么越省力分得越粗，而核实总是慢半拍”。
> 目录 slug 仍为 `resolution-grain`（改名只影响路径，发布前一并处理）。

从那里出发，全书走三层：

- **个人层**：分辨率 `v` 是 `(T+λ)/(2w)`——带宽价格、认知成本、在意程度三者的驻点。
- **群体层**：`w` 下降 → 码变粗 → 标签（"摆拍""剧本""伪人"）替代叙事，因为**粗码是最便宜的码**。
- **社会层**：共情资源 `E_t`、核实延迟 `τ`、替代供给 `ρ`、惩罚可见度 `p`、技术弹性 `κ`——五条能算的序列，一条算不出的（`α`）。

**它不主张自己是一个新原理。** 第一性方程是 Sims (2003) 理性疏忽在社会规则上的应用；
新颖性收在一个诚实的位置：**不是新原理，是新应用**（规则、分类、代际）。

---

## 目录契约

```
source/       book.json + front_* + ch01..ch24 + appendix_a..f + back_*
assets/       css / svg / charts
analysis/     推导、审计、协议、图件脚本（核心资产）
data/         raw（本地缓存，不入版本）/ derived / MANIFEST*.tsv / DIGEST*.md
docs/         变量表、源登记簿、需求单、事件台账、术语表、缺口补法、工作日志
scripts/      collect/（采集器）+ build.sh / release.sh / validate.sh
versions/     CHANGELOG.md
output/       build 产物（gitignore）
release/      组装产物（gitignore）
```

**纪律**：`source/` 是唯一正文来源；`output/`、`release/` 永不手改；
`data/raw/` 是本地缓存（不入版本），但每个文件在 `MANIFEST*.tsv` 里都有 URL、字节数与 SHA256——
**删了能照账重新拿回来**，这是这个仓库能被核对的唯一理由。

---

## 核心资产（`analysis/INDEX.md` 是唯一入口）

| 文件 | 内容 |
|---|---|
| `MODEL-v2.md` | 第一性、个体/群体/社会三层方程、两个 `v` 的统一、与理性疏忽的关系 |
| `AGENTS-DERIVATION.md`（在仓根） | **唯一公设清单 P1—P5** + 五条推导纪律 + 检查表 |
| `DERIVATION.md` | 推导链全图、可识别性审计、事后拟合清单 |
| `REWALK.md` | 从率—失真重走一遍：删掉什么、留下什么、六条符号预言 |
| `DATA-AUDIT.md` | 每个符号在盘上有没有量、13 条不可核、9 个缺口 |
| `BOOK-PLAN.md` | 体裁判断、六部参照作品、24 章骨架、证据分配、中性叙事红线 |
| `ROADMAP.md` | 接下来做什么：三类材料、六个发散点、五个质量装置、90 天排期 |
| `GAPS-NOW.md` | **现状盘点**：卡写作的五件；`v` 的档案代理（HS/ICD 块数）；三处模型层真问题 |
| `ANCHORS.md` | 文献锚点 40 条：同构/支持/修正/反驳 × 我们必须改的说法 |
| `SUBSUMPTION.md` | **统摄检验（总）**：12 条学说里 8 条可推；三个新领域（分期/标志性事件/人生转折）；§6b 分科验收 |
| `SUBSUMPTION-SOC.md` | **社会学统摄**：11 学说，**6 可推**／3 对应／2 不能（戈夫曼、埃利亚斯、格兰诺维特可推） |
| `SUBSUMPTION-MAP.md` | **推导树 + 十三门总表**：七门可推、六门遗落领域（语言/法/医/军/音乐/AI） |
| `APPENDIX-A6-NETWORK.md` | **A.6 内生网络**：`p_ij` 双通道（相遇/监督）、联立系统七小节、同质性选择的两面 |
| `SUBSUMPTION-PSYCH.md` | **心理学统摄**：米尔格拉姆（阈值效应）／阿希／人格稳定性／PTG-PTSD（倒 U 推导）／刻意练习 |
| `DERIVATION-REPLICATOR.md` | **群体更新从 P1+P3 推出**（不需第六公设）：选择速度∝收益差；极化阈值 `γ*=δ` |
| `CHAPTER-16.md` | **第 16 章详细大纲**（新增的社会学章）：三种执行方式、戈夫曼双轨、埃利亚斯内化、`C∝v` |
| `FINDINGS-PASS2.md` | **第二轮通读发现**：`E_t` 是 `w` 与 `γ` 的乘数；`τ`=层级（首测不支持）；`γ` 变号 |
| `INDEX.md` | **analysis 的唯一入口**：按骨架/可判定性/统摄/案例/写作装置/脚本/归档分七类 |
| `data/DATA-LEDGER.md`（在 `data/`） | **已删原始数据的账**：2.18 GB → 80 MB，八项的 URL+SHA256+理由 |
| `FIRST-PRINCIPLE.md` | **第一性的数学形态**：一条分布泛函统一三层；势博弈；群体心理转变的三机制；经济学四处接口 |
| `FORMAL-GAPS.md` | **数学还差什么**：九个结构性缺口、补法、顺序（G1 规则=划分是支点） |
| `FOUR-TYPES.md` | **回到最初的问题**：不是四种人，是四种分配 regime（环境×预算 2×2），含三组实证与判决检验 |
| `CASE-TANGSONG.md` | **唐宋之变**：四段的合法性划分、七人五型、`γ` 与 `C`、事件算子、分期粒度实证 |
| `CASE-BIOGRAPHY.md` | **传记法**：四栏模板、高骈示范、七人候选（含冯道这个“变的是后世的码”的反例） |
| `CASE-NAMED-ERAS.md` | **命名时代**：镀金/咆哮/改革开放三个名字与数据对表；`γ` 形状解释名字的扩散 |
| `CASE-EXTENSION.md` | **可移植性**：三条判据、五步流程、五个候选段；`C` 的三因子分解（规模×性质×频率）|
| `CASE-USSR.md` | **迟滞的极端案例**（正文第 20 章）：“亡”与“收尸”的间隔可从 P3+P4 推出；四条可测预言 |
| `CASE-PERIODS.md` | **十七个争议历史段**：三条判据定位，每段只检验一条推导 |
| `CASE-FIGURES.md` | **名人矩阵**：按五型排（收窄/崩塌/重锚/加细/换码/抢占），古今中外 |
| `CASE-CONTENTION.md` | **把“争议”算出来**：跨国叙事距离 = 1−Jaccard；甲午 en–ja 距离 0.984 |
| `CASE-APPLIED.md` | **当代四现象 + MBTI**：热潮的先糊后跳、债市两种定价、法国 `w↓` 与德州 `w↑` 成对 |
| `EDUCATION.md` | **教育学的四对挂接**：皮亚杰/维果茨基/马顿/布卢姆；过拟合＝高 `w` 下的最优码 |
| `COUNTEREXAMPLES.md` | 24 章各一条**真**反例：推翻什么、怎么处理 |
| `SCENES.md` | 24 个场景：8 条已成型、10 条有线索、6 条待作者 |
| `make_figures.py` | 八张书用图（统一视觉语言，300 dpi + SVG） |
| `CLAIMS-AUDIT.md` | 43 条断言的逐条裁决（支持/部分/推翻/不可核） |
| `PROTOCOL-gradients.md` | 2×2×2 组内实验协议（n=96，未执行） |
| `SELF-PROTOCOL.md` | n=1 自观察三件套（两周） |
| `BOUNDARY-MAP.md` | 统摄降为分域的模板 |
| `MEMORY-INDEX.md` | 27 轮对话档案的去向（只记结构，不复述原句） |

---

## 能复现的六条序列

| 量 | 读数 | 脚本 |
|---|---|---|
| `τ` 美国侧 | 21,063 条，中位 6 天，P90 26，7.8% 超 30 天（重尾） | `scripts/collect/derive_tau.py` |
| `τ` 中国侧 | 47 个反转事件；2016—2022 中位 4.4 天（全 ≤13 天）；2023—2026 出现长尾（最长 143 天） | `analysis/derive_tau_china_v2.py` |
| `E_t` | WVS 234 国×波（中国 5 波） | `analysis/ess8_age_vs_edu.py` |
| `π_L` | 人民日报 130,186 篇（2021-01→2026-04）+ 微博正文（2026-11→） | `scripts/collect/digest_labels.py` |
| `ρ` / `p` / `κ` | 核查产能 1,963→934；处置可见度 2.68%→1.73%→2.68%；AI 占谣言类 0→18.8%→25.9% | `analysis/derive_gaps.py` |
| 财富份额 | WID 世界/中国/美国 1820—2024 | `scripts/collect/derive_wid.py` |
| **粗码的失真** | 标题只有正文 2.2—2.5% 的码率；限定词保留 **0.3—1.3%** | `analysis/derive_code_rate.py` |
| **Shepard 检验** | 群体宽度异质性 k 与梯度尾部指数 b 同向：1.31→1.69 | `data/derived/shepard_check.csv` |
| **分期粒度检验** | 跨度↑⇒段粗，r=**+0.879**（n=45）；五代粒度差 5 倍 | `analysis/test_periodization.py` |
| **「厌倦」的模型** | 冲击卷积→阈值→权重反转→迟滞；翻转落在 950.8（示意，非拟合） | `analysis/sim_yanduan.py` |
| **叙事距离** | 甲午 en–ja 0.984、ja–zh 0.928、en–ko 0.817；其余事件 0.91—0.95 | `analysis/test_narrative_distance.py` |

---

## 命令

```bash
PY="/mnt/d/0_Code/Iris Series/.venv/Scripts/python.exe"

"$PY" analysis/derive_tau_china_v2.py     # 中国侧 τ（两批合并）
"$PY" analysis/derive_gaps.py             # ρ / p / κ
"$PY" scripts/collect/derive_wid.py       # WID 财富份额
"$PY" scripts/collect/digest_labels.py    # 标签密度 × 精度
"$PY" scripts/collect/fetch_piyao.py      # 前向采集（每周一次）

"$PY" build_book.py --pdf                 # 书面世后：HTML + A4 PDF
bash scripts/build.sh                     # 全量：audit → 印刷 → 电子版 → EPUB → Markdown
```

---

## 三条边界（写进正文，不只写在这里）

1. **结论强度 ≤ 证据强度。** 43 条断言里，支持 9、部分 6、推翻 6、不可核 13、概念/未测 9。
   不可核的那 13 条**不许当论据**。
2. **不可做的六件事**（第 22 章单列）：人群的分辨率分布、塔西佗阈值、每轮套利的共情折损、
   学习率、负荷→成本系数、身份动员收益——都要实验室或面板，一个独立研究者做不了。
3. **代际冲突与性别对立只作背景**：不点人群、不给频率、不做因果，合计不超过 1,500 字。

---

## 尚未完成

- 正文 28 章（0/28）
- 前置 6 件、后置 4 件、附录 A–F
- `CITATION.cff` 的 DOI（未注册）
- `inventory.tsv` 未收录：**这本书目前不计入系列的 9 册**，发布前才登记，届时件数会变——这是作者的保留决定。
