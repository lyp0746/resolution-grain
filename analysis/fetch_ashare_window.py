#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抓取 A 股最近一个月的主要指数、两融与质押数据（2026-10-20 至 2026-11-20）。

来源：
  指数日线  https://web.ifzq.gtimg.cn/appstock/app/fqkline/get
  两融合计  https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPTA_RZRQ_LSHJ
  质押周度  https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPT_CSDC_STATISTICS

输出：data/derived/ashare_window_2026-10-20_2026-11-20.json
"""
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "derived" / "ashare_window_2026-10-20_2026-11-20.json"
START, END = "2026-10-20", "2026-11-20"

INDICES = {
    "上证指数": "sh000001",
    "深证成指": "sz399001",
    "创业板指": "sz399006",
    "科创50": "sh000688",
    "沪深300": "sh000300",
    "上证50": "sh000016",
    "中证500": "sh000905",
    "中证1000": "sh000852",
    "北证50": "bj899050",
}

S = requests.Session()
S.headers.update({"User-Agent": "Mozilla/5.0", "Referer": "https://quote.eastmoney.com/"})


def get(url, **kw):
    for i in range(4):
        try:
            r = S.get(url, timeout=25, **kw)
            r.raise_for_status()
            return r
        except Exception:
            time.sleep(1.5 * (i + 1))
    raise RuntimeError(f"fetch failed: {url}")


def fetch_index(symbol):
    if symbol.startswith("bj"):
        # 腾讯的北证历史只回单日；改用新浪日线（不复权，指数无需复权）
        u = ("https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/"
             "CN_MarketData.getKLineData")
        p = {"symbol": symbol, "scale": 240, "ma": "no", "datalen": 40}
        rows = get(u, params=p).json()
        return [{"date": r["day"], "open": float(r["open"]), "close": float(r["close"]),
                 "high": float(r["high"]), "low": float(r["low"]),
                 "volume": float(r["volume"])}
                for r in rows if START <= r["day"] <= END]
    u = "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get"
    p = {"param": f"{symbol},day,{START},{END},100,qfq"}
    j = get(u, params=p).json()
    d = j["data"][symbol]
    rows = d.get("day") or d.get("qfqday") or []
    out = []
    for r in rows:
        # [date, open, close, high, low, volume]
        out.append({"date": r[0], "open": float(r[1]), "close": float(r[2]),
                    "high": float(r[3]), "low": float(r[4]), "volume": float(r[5])})
    return out


def stats(rows):
    if len(rows) < 2:
        return {}
    closes = [r["close"] for r in rows]
    rets = [closes[i] / closes[i - 1] - 1 for i in range(1, len(closes))]
    peak, mdd = closes[0], 0.0
    for c in closes:
        peak = max(peak, c)
        mdd = min(mdd, c / peak - 1)
    # 最长连续下跌（按收盘价严格下降）
    longest = cur = 0
    for x in rets:
        cur = cur + 1 if x < 0 else 0
        longest = max(longest, cur)
    # 末端连续下跌
    tail = 0
    for x in reversed(rets):
        if x < 0:
            tail += 1
        else:
            break
    mean = sum(rets) / len(rets)
    var = sum((x - mean) ** 2 for x in rets) / max(1, len(rets) - 1)
    return {
        "first_date": rows[0]["date"], "last_date": rows[-1]["date"],
        "first_close": closes[0], "last_close": closes[-1],
        "return_pct": (closes[-1] / closes[0] - 1) * 100,
        "max_drawdown_pct": mdd * 100,
        "trading_days": len(rows), "down_days": sum(1 for x in rets if x < 0),
        "longest_down_streak": longest, "tail_down_streak": tail,
        "daily_vol_pct": (var ** 0.5) * 100,
    }


def fetch_margin():
    u = "https://datacenter-web.eastmoney.com/api/data/v1/get"
    p = {"reportName": "RPTA_RZRQ_LSHJ", "columns": "ALL", "pageNumber": 1,
         "pageSize": 50, "sortColumns": "DIM_DATE", "sortTypes": "-1",
         "filter": f"(DIM_DATE>='{START}')"}
    j = get(u, params=p).json()
    rows = []
    for x in j["result"]["data"]:
        d = x["DIM_DATE"][:10]
        if d > END:
            continue
        rows.append({"date": d, "rzye": x["RZYE"], "rqye": x["RQYE"],
                     "rzrqye": x["RZRQYE"], "ltzb": x.get("RZYEZB")})
    return sorted(rows, key=lambda x: x["date"])


def fetch_pledge():
    u = "https://datacenter-web.eastmoney.com/api/data/v1/get"
    p = {"reportName": "RPT_CSDC_STATISTICS", "columns": "ALL", "pageNumber": 1,
         "pageSize": 20, "sortColumns": "TRADE_DATE", "sortTypes": "-1"}
    j = get(u, params=p).json()
    rows = []
    for x in j["result"]["data"]:
        d = x["TRADE_DATE"][:10]
        if d < START or d > END:
            continue
        rows.append({"date": d,
                     "pledged_shares_wan": x["TOTAL_PLEDGED_SHARES"],
                     "pledge_mv_wan": x["PLEDGE_MARKET_VALUE"],
                     "pledge_mv_ratio_pct": (x["PM_RATIO"] / 100.0) if x.get("PM_RATIO") is not None else None,
                     "pledge_companies": x["PLEDGE_CO_NUM"]})
    return sorted(rows, key=lambda x: x["date"])


def main():
    data = {"window": {"start": START, "end": END},
            "fetched_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "sources": {
                "indices": "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get; 北证50: https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData",
                "margin": "https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPTA_RZRQ_LSHJ",
                "pledge": "https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPT_CSDC_STATISTICS",
            }, "indices": {}, "margin": [], "pledge": []}
    for name, sym in INDICES.items():
        rows = fetch_index(sym)
        data["indices"][name] = {"symbol": sym, "rows": rows, "stats": stats(rows)}
        time.sleep(0.8)
    data["margin"] = fetch_margin()
    data["pledge"] = fetch_pledge()
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {OUT}")
    for name, x in data["indices"].items():
        s = x["stats"]
        print(f"{name:6s} {s.get('return_pct',0):+7.2f}%  mdd {s.get('max_drawdown_pct',0):7.2f}%  "
              f"down {s.get('down_days',0)}/{s.get('trading_days',0)}  streak {s.get('longest_down_streak',0)}  tail {s.get('tail_down_streak',0)}")
    if data["margin"]:
        m0, m1 = data["margin"][0], data["margin"][-1]
        print(f"margin {m0['date']} {m0['rzrqye']/1e12:.3f} -> {m1['date']} {m1['rzrqye']/1e12:.3f} 万亿")
    if data["pledge"]:
        p0, p1 = data["pledge"][0], data["pledge"][-1]
        print(f"pledge {p0['date']} {p0['pledge_mv_ratio_pct']:.2f}% -> {p1['date']} {p1['pledge_mv_ratio_pct']:.2f}%")


if __name__ == "__main__":
    main()
