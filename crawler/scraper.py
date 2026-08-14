#!/usr/bin/env python3
"""价格采集主程序。

用法：
  python crawler/scraper.py --source mobaobuy   # 仅秣宝网真实维生素报价
  python crawler/scraper.py --source jintou     # 仅金投网真实有机溶剂报价（丙酮/冰醋酸/二甲苯/甲醇/乙醇）
  python crawler/scraper.py --source all        # 维生素(真实) + 有机溶剂(真实) 合并（生产默认）
  python crawler/scraper.py --source solvent    # 仅有机溶剂「示例/估算」数据（占位演示）
  python crawler/scraper.py --source example    # 仅示例公开源（需先填好适配器）

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
from sources.mobaobuy import MobaobuySource
from sources.jintou import JintouSource
from sources.solvent_demo import SolventDemoSource

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


def build_sources(source):
    srcs = []
    if source == "mock":
        # 纯离线演示（含未标注的示例数据），不并入生产
        srcs.append(MockSource())
    if source in ("mobaobuy", "all"):
        srcs.append(MobaobuySource())
    if source in ("jintou", "all"):
        # 金投网真实有机溶剂报价（丙酮/冰醋酸/二甲苯/甲醇/乙醇）
        srcs.append(JintouSource())
    if source == "example":
        # 示例公开源模板，需先 pip install requests beautifulsoup4 并填好适配器
        srcs.append(Example100ppiSource())
    if source == "solvent":
        # 有机溶剂「示例/估算」占位（已标注 isSample），仅演示用，不进生产
        srcs.append(SolventDemoSource())
    return srcs


def merge_history(hist, name, today, price):
    series = hist.get(name, [])
    if not series or series[-1]["date"] != today:
        series.append({"date": today, "price": price})
    hist[name] = series


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=["mock", "example", "mobaobuy", "jintou", "solvent", "all"], default="all")
    ap.add_argument("--days", type=int, default=30)
    args = ap.parse_args()

    sources = build_sources(args.source)

    # 先加载历史，用于计算日涨跌基线
    hist = load_existing_history()

    # 1) 当日价格
    latest = []
    for src in sources:
        try:
            latest += src.fetch()
        except Exception as e:
            print(f"[warn] source {src.name} failed: {e}")

    today = datetime.date.today().isoformat()
    for it in latest:
        it["updatedAt"] = today
        price = float(it["price"])
        # 优先用源自带的 prevPrice；否则用历史中最近一个点的价格作为基线
        prev = it.get("prevPrice")
        if prev is None:
            series = hist.get(it["name"], [])
            prev = series[-1]["price"] if series else price
        prev = float(prev)
        it["changeRate"] = 0.0 if prev == 0 else round((price - prev) / prev * 100, 2)

    # 2) 历史序列
    # 2a) 提供完整历史的源（如 mock/solvent_demo）直接覆盖其 name
    provided = set()
    for src in sources:
        if hasattr(src, "history"):
            try:
                h = src.history(args.days)
                if h:
                    for name, series in h.items():
                        hist[name] = series
                    provided |= set(h.keys())
            except Exception as e:
                print(f"[warn] {src.name}.history failed: {e}")
    # 2b) 其余源（mobaobuy/jintou）按日追加
    for it in latest:
        if it["name"] in provided:
            continue
        merge_history(hist, it["name"], today, it["price"])

    # 3) 写出
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(os.path.join(DATA_DIR, "latest.json"), "w", encoding="utf-8") as f:
        json.dump(latest, f, ensure_ascii=False, indent=2)
    with open(os.path.join(DATA_DIR, "history.json"), "w", encoding="utf-8") as f:
        json.dump(hist, f, ensure_ascii=False, indent=2)

    print(f"[ok] wrote {len(latest)} items, history names={len(hist)}, updatedAt={today}")


if __name__ == "__main__":
    main()
