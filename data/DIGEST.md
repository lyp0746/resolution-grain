# 数据读数 v0.1

> 由 `scripts/collect/digest.py` 从 `data/raw/` 生成。快照日见 `data/MANIFEST.tsv`。
> 只列读数，不作推断；每个数字的可靠性按来源登记簿的等级读。

## 一、生育率（E_t 的下游指标）

- 中国 TFR（wb_tfr_chn）：2019: 1.496；2020: 1.236；2021: 1.117；2022: 1.034；2023: 0.999；2024: 1.013
- 美国 TFR（wb_tfr_usa）：2019: 1.706；2020: 1.641；2021: 1.664；2022: 1.657；2023: 1.617；2024: 1.627
- 日本 TFR（wb_tfr_jpn）：2019: 1.360；2020: 1.330；2021: 1.300；2022: 1.260；2023: 1.200；2024: 1.150
- 韩国 TFR（wb_tfr_kor）：2019: 0.918；2020: 0.837；2021: 0.808；2022: 0.778；2023: 0.721；2024: 0.748
- OWID 中国 TFR（OWID/China）：2019: 1.496；2020: 1.236；2021: 1.117；2022: 1.034；2023: 0.999

## 二、平台化的前置条件（λ 与规则谱跃迁的背景）

- 中国互联网普及率（%）（wb_net_chn）：2020: 70.053；2021: 73.053；2022: 75.611；2023: 90.600；2024: 92；2025: 91.600
- 中国的人均 GDP（现价美元）（wb_gdppc_chn）：2020: 10627.464；2021: 12887.436；2022: 12970.606；2023: 12951.178；2024: 13293.116；2025: 13861.970
- 中国城镇化率（%）（wb_urb_chn）：2020: 63.523；2021: 64.721；2022: 65.218；2023: 65.530；2024: 65.895；2025: 66.343

## 三、注意力代理（π_L 的可行性演示）

- zh.wikipedia「中国人」条目（月浏览量合计）：2016: 7,212；2017: 6,105；2018: 6,612；2019: 6,671；2020: 6,461；2021: 5,455；2022: 4,949；2023: 5,036；2024: 7,538；2025: 8,099；2026: 11
- 说明：「伪人」在 zh.wikipedia 无独立条目（实测 404），故 π_L 不能用该条目；该读数的用途是证明**管道可用**，不是证明标签在扩张。

## 四、断言核验（把对话里的数字拉回原文）

- Gallup 28%：原文命中 11 处
  > …Trust in Media at New Low of 28% in U.S. /* bold font weight */ b, strong { font-weight: 600; } @view-transition { navigat…
  > …, television and radio to report the news fully, accurately and fairly is at a new low of 28%.","headline":"Trust in Media at New Low of 28% in U.S.","@id":"https://news.gallup.com/po…
  > …on/POLL/8abbdf49-6d1b-4529-88d0-5c1df464d846.jpg","caption":"Trust in Media at New Low of 28% in U.S."},"inLanguage":"en-US","breadcrumb":{"@type":"BreadcrumbList","itemListElement":[…
  > ….gallup.com/poll/"},{"@type":"ListItem","position":3,"name":"Trust in Media at New Low of 28% in U.S."}]},"name":"Trust in Media at New Low of 28% in U.S.","publisher":{"logo":{"@type…

## 五、仍未取得（2026-11-16 改）

- GDELT：**已取得**（`data/raw/gdelt/gdelt_deepfake_full.json`，677 天，2024-11—2026-11）。最早那次 429 是限速，不是封锁；完整序列已推翻摘录版的趋势（见 README §3c）。
- 国家统计局：SSL 失败，需代理或手工下载。
- CGSS / CFPS / WVS / PIAAC：登记制，需申请，不在本轮范围（WVS 已由 Kaggle 公开集补齐）。
- WGI（`d` 的代理）：World Bank API 对该指标返回空集，需改从 WGI 官网 xlsx 取。
