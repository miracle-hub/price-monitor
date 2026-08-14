"""Mock 数据源：无网络依赖，用于本地开发 / 演示 / 测试。

直接生成贴近真实的价格随机游走，保证网页开箱即用。
接入真实爬虫后，可用 --source example 或 --source all 切换。
"""
import random
import datetime
from .base import BaseSource

# (名称, 类别, 规格, 单位, 地区, 基准价)
ITEMS = [
    ("维生素C", "vitamin", "饲料级", "元/kg", "华东", 28.5),
    ("维生素E", "vitamin", "食品级", "元/kg", "华东", 72.0),
    ("维生素A", "vitamin", "饲料级", "元/kg", "华东", 185.0),
    ("维生素B1", "vitamin", "医药级", "元/kg", "华东", 165.0),
    ("丙酮", "solvent", "工业级", "元/吨", "华东", 6200.0),
    ("冰醋酸", "solvent", "99.8%", "元/吨", "华东", 2950.0),
    ("二甲苯", "solvent", "异构级", "元/吨", "华东", 7400.0),
]


class MockSource(BaseSource):
    name = "mock"

    def _walk(self, days, seed_base):
        today = datetime.date.today()
        series = []
        price = seed_base
        rnd = random.Random(seed_base)
        for i in range(days - 1, -1, -1):
            d = (today - datetime.timedelta(days=i)).isoformat()
            price = price * (1 + rnd.uniform(-0.03, 0.03))
            series.append({"date": d, "price": round(price, 2)})
        return series

    def history(self, days=30):
        out = {}
        for nm, cat, sp, unit, region, base in ITEMS:
            out[nm] = self._walk(days, base)
        return out

    def fetch(self):
        today = datetime.date.today().isoformat()
        hist = self.history(30)
        out = []
        for nm, cat, sp, unit, region, base in ITEMS:
            series = hist[nm]
            last = series[-1]["price"]
            prev = series[-2]["price"] if len(series) > 1 else last
            out.append({
                "name": nm, "category": cat, "spec": sp,
                "unit": unit, "region": region,
                "price": last, "prevPrice": prev,
                "updatedAt": today, "source": self.name,
            })
        return out
