# 下一轮启动提示词（V2，33 章已就位）

> 用法：整段复制给新会话。它替代旧的 `NEXT-SESSION-PROMPT.md`（那份是 30 章时代的）。

---

## 启动提示词（复制下面整段）

```
你是李葳蕤，继续李毅芃《粗码》第二版（V2）。工作目录：D:/0_Article/resolution-grain。
不要提交 GitHub，不要推 Zenodo。$PY = "/mnt/d/0_Code/Iris Series/.venv/Scripts/python.exe"

先按顺序读这五份，读完再动手：
1. AGENTS.md（本仓宪法；§9 已知的坑第 7 条是"写回型脚本"事故）
2. AGENTS-DERIVATION.md（P1—P6；两条原理＋四个接触面）
3. analysis/V2-EXPERIENCE.md（写法与返工）
4. analysis/HANDOFF.md 的 §0i（第八十五轮：33 章现状）与 §0h／§0g
5. analysis/ROUND-PLAN-V2.md（未办事项总表与深化清单）

现状（不要重新盘点）：33 章／7 部分；正文 287,637 汉字，全书 303,467；表 139／图 37；
output-v2/book.pdf 451 页、38 书签；四项检查全过
（check_v2_sources OK／check_order --strict 0／audit_citations 缺口 0／sync_sections 一致）。
章号已冻结：1—3 舞台、4—8 个人、9—12 爱与好奇、13—17 群体、18—23 社会、24—29 文明、30—33 边界。
不要再重排编号；编号只用 x.y 与 x.y.z（h4），禁止 5.6b 这类后缀。

这一轮按顺序做三件（做完立刻跑四项检查并重建 PDF）：
A. 附录 B—E（约 12,000 字，单节 ≤1,200 字）：
   B 数据与复现（全部数据文件＋脚本＋SHA256＋快照日）／
   C 协议与稳健性（预注册式协议与三次敏感性）／
   D 可证伪登记簿（append-only；与附录 F 分工：F 是"哪一句会倒"，D 是"何时登记、何时核对"）／
   E 工具与清单（六问／五问／四栏／三件套的可打印清单）。
B. 术语表＋索引主体（约 3,000 字）、本系列页、后记、通俗导读（约 1,000 字）——
   术语表同时是索引正文，build_book 的 compute_indexmap 才有东西可查。
C. 六核心"有名无实"的三章补节（见 ROUND-PLAN-V2 §2）：ch04 看见、ch06 选择、ch15 讲述，
   各补一节（800—1,200 字）＋一张"六核心→式子六部位"的对照表（放 ch03）。

纪律（都要遵守）：
- 每章 ≥8,000 汉字（下限，上限无）；补写靠"机制层"（式子为什么长这样／参数依赖／可查推论），不注水。
- 现实案例要有日期与出处；合成人物一律不用（本书已全换真人，《故事新编》式并置）。
- 只描述、不评价：把"赔的是命""藏起来"改成"谁付、付多少、怎么数"。
- 分级进装置（表与图的 datasrc），不进每句；否证线一章至多一条，其余进附录 F。
- 禁词：必然／注定／不可避免／无法消除／死路；不留 ** 与裸反引号。
- 公式用 .mblock／.eq；图按 6.4 in 版心画，内部字号 ≥7 pt。
- 模拟／构造／场能／VOI 峰位一律标 C。
- V1 内容重构改写，不搬表；表随文走、表号按 V2 章重排、出处只写在 datasrc。
- 只写 source-v2/；不碰 source/；不重建 v1 的 output/。

收口命令（每次改完都跑）：
  "$PY" analysis/check_v2_sources.py
  "$PY" analysis/check_order.py --src source-v2 --strict
  "$PY" -X utf8 analysis/audit_citations.py --src source-v2 --out analysis/CITATION-AUDIT-V2.md
  "$PY" -X utf8 analysis/sync_sections.py --src source-v2 --write
  "$PY" build_book.py --src source-v2 --out output-v2 --pdf
完成后报告：字数／页数／表图数／四项检查结果／这一轮新增的"说不出"。

不要做：
- 不要重新捡起 28 章瘦身方案；不要把"压缩即智能"单独成部分。
- 不要把爱与好奇写成两个参数；不要把五件事写成"五件全通"。
- 不要为了字数注水；不要给已有章加"总述性"空段。

第一句可以这样开始：先读 analysis/ROUND-PLAN-V2.md 的 §3（未办事项）与 §2（深化清单），
然后写 appendix_b.html（数据与复现），再依次 C、D、E。
```
