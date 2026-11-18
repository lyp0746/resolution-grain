# 数据集检查 v0.1

> 由 `scripts/collect/inspect_datasets.py` 生成。只报模式与覆盖，不报结论。

## 1. PolitiFact（τ 的美国侧）

- 文件：`politifact_factcheck_data.json`，记录 21152 条
- 字段：factcheck_analysis_link, factcheck_date, factchecker, statement, statement_date, statement_originator, statement_source, verdict

- **τ 可算**：21,063 条；中位 6 天，P25 2，P75 13，P90 26
- τ > 30 天占比：7.8%；τ > 365 天：0.5%
- 按年（中位 τ）：2007: 8；2008: 2；2009: 2；2010: 6；2011: 9；2012: 8；2013: 8；2014: 6；2015: 6；2016: 5；2017: 6；2018: 6；2019: 6；2020: 4；2021: 4；2022: 4
- 年份覆盖：2007–2022

  - `factcheck_analysis_link`：缺失 0/21152；示例 https://www.politifact.com/factchecks/2008/jun/16/barack-obama/no-exem
  - `factcheck_date`：缺失 0/21152；示例 6/16/2008
  - `factchecker`：缺失 21/21152；示例 Adriel Bettelheim
  - `statement`：缺失 0/21152；示例 John McCain opposed bankruptcy protections for families "who were only
  - `statement_date`：缺失 0/21152；示例 6/11/2008
  - `statement_originator`：缺失 0/21152；示例 Barack Obama
  - `statement_source`：缺失 0/21152；示例 speech
  - `verdict`：缺失 0/21152；示例 true

## 2. 中国三平台小时榜（π_L 的当期切片）

- 快照文件 5 个，行数 86,607
- 覆盖：2026-10-30T02:00:00Z → 2026-11-03T03:00:00Z
- 平台分布：{'baidu': 4845, 'baidu_car': 2850, 'baidu_game': 2850, 'baidu_meme': 2850, 'baidu_movie': 950, 'baidu_novel': 2850, 'baidu_tv': 950, 'bilibili': 4750, 'bilibili_rank': 9500, 'douyin': 4657, 'ithome': 1140, 'kr36': 3585, 'kuaishou': 4464, 'netease': 9500, 'sina': 4275, 'tencent': 4750, 'thepaper': 1900, 'tieba': 2850, 'toutiao': 4750, 'weibo': 4750, 'weibo_ent': 4750, 'zhihu': 2841}
- 分类前 8：[('艺人', 2709), ('综艺', 2170), ('类型：手机游戏', 1520), ('tech', 1140), ('finance', 980), ('剧集', 964), ('日常', 915), ('单机游戏', 907)]

## 3. 微博热搜（π_L 的长序列候选）

### `weibo-hot-search-labeled.csv`：6,218 行
- 表头：['日期', '热搜词条', '链接', '标签（时政、科技、科普、娱乐、体育、社会讨论/话题、时事、经济）']
- 首行：['2020-11-24', '60秒盘点嫦娥系列探测器发射瞬间', 'https://s.weibo.com//weibo?q=%2360%E7%A7', '科技']
- 末行：['2020-12-23', '纪云沉下线', 'https://s.weibo.com//weibo?q=%E7%BA%AA%E', '娱乐']
- 日期范围：2020-11-24 → 2020-12-23（30 个不同日期）
- 标题关键词命中（占全部行）：摆拍 1；剧本 0；反转 0；辟谣/谣言 12；道歉 23

### `weibo-hot-search-unlabeled.csv`：69,936 行
- 表头：['日期', '热搜词条', '链接']
- 首行：['2020-12-24', '加快建设交通强国', 'https://s.weibo.com//weibo?q=%23%E5%8A%A']
- 末行：['2021-11-24', '门锁的剧情跟独居女性有多大关系', 'https://s.weibo.com//weibo?q=%23%E9%97%A']
- 日期范围：2020-12-24 → 2021-11-24（302 个不同日期）
- 标题关键词命中（占全部行）：摆拍 4；剧本 44；反转 15；辟谣/谣言 128；道歉 254
