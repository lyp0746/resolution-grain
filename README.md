# 粗码 · Coarse Codes

**为什么越省力分得越粗，而核实为何总是追不上**
*How Saving Effort Reshapes Resolution, and Why Verification Trails Behind*

> **系列**：《有限系统的取舍》第十册（未入 `inventory.tsv`、不进合集）
> **上一版本**：2026-11-20，DOI [10.5281/zenodo.24390257](https://doi.org/10.5281/zenodo.24390257)（概念 DOI [10.5281/zenodo.24339909](https://doi.org/10.5281/zenodo.24339909)）
> **本版 DOI**：[10.5281/zenodo.24393431](https://doi.org/10.5281/zenodo.24393431)（概念 DOI 10.5281/zenodo.24339909）
> **当前版本**：**2026-11-21**——7 部分 **33 章**；正文 **323,420 汉字**；170 表／43 图；印刷版 **642 页**（EPUB／网页版／Markdown 齐备）
> **许可**：CC BY 4.0 ｜ **下载**：见 [Releases](../../releases)，**先看 `resolution-grain-print.pdf`**（印刷版，默认预览）

---

## 一、这本书在讲什么 ｜ What this book is about

同一份力气，花在两个地方，会得到两种完全不同的结果。时间紧、睡得少、后果重的时候，人不是变懒了，
而是把有限的码率换了一种花法：环境宽的时候缩支撑，只剩一条隧道；环境窄的时候缩刻度，糊成一片。

> **不是「他分得粗」，而是「他的预算只买得起这种粗」。**
> 全书从一个驻点式出发，推到个人、群体、社会、文明四层；四层不是一条阶梯，是一张有环的图（第 3 章 §3.7，图 3.3）：
> 上行把慢量当参数送进快层（涌现），下行只在阈值处改写慢层的可行集（重置）。
> 最后说清一件事：**位置算得出来，时刻算不出来**。

*The same effort, spent in two different places, buys two entirely different results. Under time pressure,
sleep debt and high stakes, people do not become lazy — they spend a limited code budget differently.
The book starts from one first-order condition and carries it through the individual, the group and the society.*

**核心式子 ｜ The core**

```
v* = (T + λ) / (2w)        分辨率是「工夫 + 疲劳」与「错了有多疼」的驻点
δ  = Δ / 2^R               覆盖面翻倍，精度减半（一份预算，两个出口）
```

---

## 二、读数 ｜ By the numbers

| 项 / Item | 值 / Value |
|---|---|
| 结构 Structure | 7 部分 33 章；正文 312 节 ＋ 附录 21 节 |
| 正文 Body text | **323,420** 汉字（全书 358,362） |
| 表／图 Tables / figures | **169** 表 ／ **43** 图 |
| 印刷版 Print edition | **639** 页（A4，含封面与四级目录书签） |
| 证据分级 Evidence grades | A（官方可复现）／B（稳定公开估计）／C（稀疏·构造·思辨） |
| 可检验预言 Testable predictions | **21** 条台账（附录 F.7，各带推翻条件与现状） |
| 空白 Gaps | **9** 处（第 26 章：缺实验／缺数据／缺概念） |
| 降为情景 Claims demoted | **13** 条查不到公开出处的断言（附录 F.1） |
| 索引 Index | 85 条（概念／人名／地名／章名） |

---

## 三、骨架 ｜ Structure

| 部分 Part | 章 Chapters | 主提问 Question |
|---|---|---|
| 一 形状 | 1—4 | 为什么「两种人」是一个错误的起点？ |
| 二 第一性 | 5—8 | 一个式子能推出多少东西？ |
| 三 个人 | 9—12 | 一个人的分辨率可以被追踪吗？ |
| 四 群体 | 13—16 | 标签为什么会替代叙事？ |
| 五 社会 | 17—20 | 六条序列能撑起多少断言？ |
| 六 历史 | 21—24 | 这套公设能落到具体年代与人吗？ |
| 七 边界 | 25—28 | 这本书在哪里停？ |

六个核心（看见／记住／跟上／选择／讲述／临界）各落一章；六个标签读成**两条原理＋四个接触面**：
原理一＝预算下的划分极小化（P1、P2，带出 P3、P4）；原理二＝账可外置、权重可为负（P6）；
接触面＝价格、切法、群体、账。**P5 不是公设**，是「世界会变」这句描述世界的话。

---

## 四、怎么读 ｜ How to read

- **通识轨**：正文一路读下去；公式只在第 5 章出现一次，之后都可用文字替代。
- **同行轨**：附录 A（形式化）、附录 F（缺口与预言台账）、`front_hardcore`（硬核轨）。
- **三种读者可以停的地方**：第 5 章的三行推导、第 7 章与理性疏忽的关系、附录 A。

*Two tracks: the body for general readers; appendices A and F plus `front_hardcore` for specialists.
The formal core is three lines in chapter 5; everything after it can be read in words.*

---

## 五、诚实纪律 ｜ Honesty discipline

1. **结论强度 ≤ 证据强度**；每个数字带 A/B/C，等级写在表注与图注里，不逐句挂。
2. **不可测就说不可测**：第 26 章单列九处空白，附录 F 记十三条查不到出处的断言与七条降级。
3. **失败与反例写在正文**，不放进脚注；**并置不是检验**（把两套理论放一张表上只说明它有位置）。
4. **反身性写「方向＋条件」**，不写宿命；凡需要第七个公设才讲得通的话，降为情景或删。

*Conclusion strength never exceeds evidence strength; what cannot be measured is said to be unmeasurable;
failures and counterexamples are reported in the body; juxtaposition is not a test.*

---

## 六、仓库里有什么 ｜ What is in this repo

```
source/    正文唯一来源（book.json / parts.json / front_* / ch01–ch28 / appendix_a–f / back_*）
assets/    css（paper / ereader / book）· svg · charts · knowledge-map.html（3D 交互版）
analysis/  推导、审计、协议、图件脚本（`INDEX.md` 是唯一入口）
data/      raw（本地缓存，不入版本，账在 MANIFEST*.tsv）· derived · DIGEST*.md
docs/      变量表、源登记簿、需求单、事件台账、工作日志
scripts/   collect/（采集器）+ build.sh / release.sh / selfcheck.sh
archive/   过程日志与已归档的计划文档（logs/）
versions/  CHANGELOG.md
output/    build 产物（gitignore）      release/  组装产物（gitignore）
```

**构建 ｜ Build**

```bash
PY="/mnt/d/0_Code/Iris Series/.venv/Scripts/python.exe"
bash scripts/selfcheck.sh          # 六项自查：结构／引用／目录／密度／产物／标签
"$PY" build_book.py --pdf          # 印刷版 → output/book.pdf
"$PY" build_book.py --ereader --pdf
"$PY" build_epub.py && "$PY" build_markdown.py
"$PY" analysis/make_theory_map.py  # 图 4.3 知识图谱、图 7.2 理论地图、3D 交互版
```

---

## 七、数据与可核性 ｜ Data and verifiability

- 定量结论都标了**快照日**（本版冻结于 2026-11-19）；原始文件的抓取时间（UTC）与 SHA256 在 `data/MANIFEST*.tsv`。
- 原始数据不入版本；派生读数在 `data/derived/`，由脚本生成，不手改。
- 主要公开来源：PolitiFact（21,063 条核实记录）、Seshat 古政体编码集（398 政体）、
  eCFR／Federal Register（266 个节级修订间隔）、历法采纳（125 国）、ESS／WVS、OEWN 义项清单（12.4 万条）。

---

## 八、系列 ｜ The series

《有限系统的取舍》九本书 ＋ 十五篇工作论文 ＋ 一部合集（共 24 件，以 `../inventory.tsv` 为准）。
本书是**第十册**，按作者决定：**不进入 `inventory.tsv`、不进合集**；归档记录见
`_zenodo/published_resolution-grain.json` 与 `_zenodo/REGISTRY.md`「未入册」一节。

*Item 10 of the series The Tradeoffs of Finite Systems. By the author's decision it is **not** counted
in `inventory.tsv` and **not** included in the 24-item collection.*

---

**引用 ｜ Cite**

> 李毅芃（2026）.《粗码：为什么越省力分得越粗，而核实为何总是追不上》. Zenodo.
> https://doi.org/10.5281/zenodo.24393431

*Li, Y. (2026). Coarse Codes: How Saving Effort Reshapes Resolution, and Why Verification Trails Behind. Zenodo.*

**许可 ｜ License**：正文与图表 CC BY 4.0；代码 MIT（见 `LICENSE`、`LICENSE-MIT`）。
