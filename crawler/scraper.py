#!/usr/bin/env python3
"""价格采集主程序。

用法：
  python crawler/scraper.py --source mock      # 仅 Mock（默认，开箱即用）
  python crawler/scraper.py --source example   # 仅示例公开源（需先填好适配器）
  python crawler/scraper.py --source all        # Mock + 示例源合并（生产推荐）

输出：
  data/latest.json   当日价格
  data/history.json  历史序列 {name: [{date, price}]}
（GitHub Actions 中运行后会自动提交，触发 Pages 重新部署）
"""
import argparse
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from sources.mock import MockSource
from sources.example_100ppi import Example100ppiSource

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")


def load_existing_history():
    p = os.path.join(DATA_DIR, "history.json")
    if os.path.exists(p):
        try:
            return json.load(open(p, encoding="utf-8"))
        except Exception:
            return {}
    return {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=["mock", "example", "all"], default="mock")
    ap.add_argument("--days", type=int, default=30)
    args = ap.parse_args()

    # 1) 当日价格
    latest = []
    if args.source in ("mock", "all"):
        latest += MockSource().fetch()
    if args.source in ("example", "all"):
        try:
            latest += Example100ppiSource().fetch()
        except Exception as e:
            print("[warn] example source failed:", e)

    today = datetime.date.today().isoformat()
    for it in latest:
        it["updatedAt"] = today
        prev = float(it.get("prevPrice", it["price"]))
        price = float(it["price"])
        it["changeRate"] = 0.0 if prev == 0 else round((price - prev) / prev * 100, 2)

    # 2) 历史序列
    hist = load_existing_history()
    if args.source in ("mock", "all") and hasattr(MockSource(), "history"):
        # Mock 直接提供完整历史
        hist = MockSource().history(args.days)
    else:
        # 追加模式：把当日价格追加到已有历史
        for it in latest:
            series = hist.get(it["name"], [])
            if not series or series[-1]["date"] != today:
                series.append({"date": today, "price": it["price"]})
            hist[it["name"]] = series

    # 3) 写出
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(os.path.join(DATA_DIR, "latest.json"), "w", encoding="utf-8") as f:
        json.dump(latest, f, ensure_ascii=False, indent=2)
    with open(os.path.join(DATA_DIR, "history.json"), "w", encoding="utf-8") as f:
        json.dump(hist, f, ensure_ascii=False, indent=2)

    print(f"[ok] wrote {len(latest)} items, updatedAt={today}")


if __name__ == "__main__":
    main()
