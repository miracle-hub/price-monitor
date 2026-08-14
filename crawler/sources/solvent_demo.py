"""有机溶剂「示例/估算」数据源（占位，非实时真实行情）
====================================================
⚠️ 重要：本文件提供的是【示例/估算】数据，仅用于前端演示与站点结构验证，
   并非真实成交价。请尽快用真实可爬源（mobaobuy 无此类目；100ppi 等有反爬）
   或你已授权的 API 替换本文件中的 fetch()/history()。

接入真实源时：
1. 在 crawler/sources/ 下新建一个继承 BaseSource 的适配器（参考 mobaobuy.py）；
2. 实现 fetch() 返回当日价格、history() 返回历史序列；
3. 在 scraper.py 的 build_sources() 中注册，并把 --source 改为新源。
"""
import datetime
import random
from .base import BaseSource

# 各溶剂的「示例」基准参数（均为估算，仅作演示，切勿当作行情）
_PRODUCTS = [
    {"name": "丙酮",     "spec": "工业级 99.5%", "region": "华东", "base": 6500, "vol": 0.025, "brandCount": 6, "quoteCount": 9},
    {"name": "冰醋酸",   "spec": "99.8%",        "region": "华东", "base": 3050, "vol": 0.020, "brandCount": 8, "quoteCount": 12},
    {"name": "二甲苯",   "spec": "异构级",        "region": "华东", "base": 7600, "vol": 0.022, "brandCount": 5, "quoteCount": 7},
]
DAYS = 30


class SolventDemoSource(BaseSource):
    name = "solvent-demo"
    category = "solvent"
    is_sample = True

    def _gen(self):
        today = datetime.date.today()
        result = []
        for p in _PRODUCTS:
            # 固定随机种子 → 每次运行生成一致（但明显合成的）序列
            random.seed(abs(hash(p["name"])) & 0xffffffff)
            price = p["base"] * (1 + random.uniform(-0.05, 0.05))
            series = []
            for i in range(DAYS):
                d = (today - datetime.timedelta(days=DAYS - 1 - i)).isoformat()
                price = max(1.0, price * (1 + random.uniform(-p["vol"], p["vol"])))
                series.append({"date": d, "price": round(price, 2)})
            last = series[-1]["price"]
            prev = series[-2]["price"]
            avg = round(sum(s["price"] for s in series) / len(series), 2)
            result.append({
                "name": p["name"],
                "category": "solvent",
                "spec": p["spec"],
                "unit": "元/吨",
                "region": p["region"],
                "price": last,
                "prevPrice": prev,
                "source": "示例（估算，非实时）",
                "isSample": True,
                "avgPrice": avg,
                "brandCount": p["brandCount"],
                "quoteCount": p["quoteCount"],
                "_series": series,
            })
        return result

    def fetch(self):
        return self.normalize(
            [{k: v for k, v in r.items() if k != "_series"} for r in self._gen()]
        )

    def history(self, days=30):
        out = {}
        for r in self._gen():
            out[r["name"]] = r["_series"]
        return out
