"""数据源适配器基类。

所有数据源都继承 BaseSource，实现 fetch() 返回当日价格列表。
normalize() 负责把原始价格统一成带涨跌幅的标准结构。
"""
from abc import ABC, abstractmethod


class BaseSource(ABC):
    name = "base"
    category = "unknown"

    @abstractmethod
    def fetch(self):
        """返回当日价格列表，元素形如：
        {'name','category','spec','unit','region','price'(float),'source'}
        prevPrice / changeRate / updatedAt 由 scraper 统一补充。
        """
        raise NotImplementedError

    def history(self, days=30):
        """可选：返回历史序列 {name: [{date, price}]}。
        未实现时，scraper 会以「每日追加」方式自行累积历史。
        """
        return None

    def normalize(self, items):
        out = []
        for it in items:
            price = float(it["price"])
            prev = float(it.get("prevPrice", price))
            rate = 0.0 if prev == 0 else round((price - prev) / prev * 100, 2)
            out.append({
                "name": it["name"],
                "category": it.get("category", self.category),
                "spec": it.get("spec", ""),
                "unit": it.get("unit", ""),
                "region": it.get("region", ""),
                "price": price,
                "prevPrice": prev,
                "changeRate": rate,
                "updatedAt": it.get("updatedAt", ""),
                "source": it.get("source", self.name),
            })
        return out
