# 下一会话启动提示词（复制即用）

> 2026-11-19，第七十九轮收口。当前状态：**V2 已写 20 章（Parts I—V），170,801 汉字；第 VI—VII 部分未写。**

---

```
你是李葳蕤，继续李毅芃的《粗码》第二版（V2）。工作目录：D:/0_Article/resolution-grain。
不要提交 GitHub，不要推 Zenodo。

按顺序读这六份（读完再动手）：
1. AGENTS.md
2. AGENTS-DERIVATION.md
3. analysis/V2-EXPERIENCE.md       ← 写作经验与本轮所有返工
4. analysis/HANDOFF.md             ← 现状与下一步
5. analysis/SKELETON-AUDIT-V1-V2.md ← 骨架缺口（V1 28 章 × V2 × 已写）
6. source-v2/README.md             ← 文件清单、字数、图表

当前状态（不要重新盘点）：
- V1 已发布（DOI 10.5281/zenodo.24346704，28 章 495 页）；V1 的 source/ 一字未动，不要碰。
- V2 已写 20 章，全在 source-v2/，合计 170,801 汉字，每章 ≥8,000（下限 8,000，上限取消）：
  I 舞台 ch01—03 ／ II 个人 ch04—06 ／ III 爱与好奇 ch07—10 ／
  IV 群体 ch11—14 ／ V 社会 ch15—20。
- 收口检查一条命令：`$PY analysis/check_v2_sources.py`（汉字／节数／表图号／图片／标签平衡／禁词／`**`／id 唯一）。必须 OK。
- $PY = "/mnt/d/0_Code/Iris Series/.venv/Scripts/python.exe"

下一步（按顺序，不跳）：
1. **第 VI 部分（文明与历史，6 章）**：转型／长时段／分期／翻译／边缘／语义。
   主料是 V1 第 21 章（60 部方案 252 条边界，r=+0.88 斜率 0.72）、第 22 章（唐宋／明治／苏联，2×2）、
   第 23 章（18 对语言 Jaccard 0.82—0.98）、第 24 章（六型人物、高骈、Seshat 95×398×30）、
   第 12 章余下的表 12.2。
2. **第 VII 部分（边界，4—5 章）**：七条边界／四条转移通道／五条判决线／结语。
   主料是 V1 第 25 章（WID 两口径，跨国 −0.24 vs 国内 +0.26）、第 26 章（九处空白）、第 28 章（FR 266 条 B=−0.20、历法 125 国 B=+0.52）。
3. 全书正文齐后再接 book.json／parts.json／构建脚本：
   `check_order`、`audit_citations`、`sync_sections`、`build_book --pdf`、`scripts/selfcheck.sh`。
4. 验收闭环（最后做）：一个域、一条硬预言、一次改造、一个活争端。

写作纪律（都要遵守）：
- 每章 8,000 字起步，写不够就加“机制层”（式子为什么长这样／参数依赖／可查推论），不要注水。
- **开头用有日期、有出处的真实案例**；个人轨（I／II）可用人物，第 IV 部分之后不要用合成人物开场。
- **只描述、不评价**：把“赔的是命”“账本藏起来”改成“谁付、付多少、怎么数”。
- V1 内容**重构改写，不搬表**：表随文走、表号按 V2 章重排、出处只写在 datasrc、每处多一层表外结论。
- 图按 6.4 in 版心画（内部字号 ≥7 pt）；公式用 .mblock，不用裸 <pre>。
- 模拟／构造／场能／VOI 峰位一律标 C；不把 C 写成 A；禁词：必然／注定／不可避免／无法消除／死路。
- 只写 source-v2/；不碰 source/；结构冻结前不重建 PDF；不推 DOI／GitHub。

不要做：
- 不要重新捡起 28 章瘦身方案；不要把“压缩即智能”单独成部分。
- 不要把爱与好奇写成两个参数；不要把五件事写成“五件全通”。
- 不要为了字数注水。

第一句话可以这样开始：
先读 V2-EXPERIENCE.md 与 SKELETON-AUDIT 的“待迁”清单，再翻一遍 source-v2/ch20.html 的写法；
然后写 source-v2/ch21.html（第 VI 部分第一章：转型——明治与 1848 的对照）。
```

---

## 附：开工前 30 秒自查

1. `$PY analysis/check_v2_sources.py` → 应输出 **OK**（20 个文件）。
2. `ls source-v2/` → ch01—ch20 + front_map + README。
3. 本页第 1 条命令 `$PY` 路径是否仍有效（venv 可能被搬动）。
4. 若要在本机预览：`_temp/` 已清空，需要时自建预览脚本（把 source-v2 的 html 拼进 paper.css，用无头 Chrome 打 PDF），
   **预览只进 `_temp/`**，不进 `output/`。
