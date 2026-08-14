"""
示例公开源适配器 —— 生意社(100ppi.com)公开行情页「模板」
========================================================
⚠️ 合规提示（运行前务必确认）：
1. 先阅读目标站点的 robots.txt 与《服务条款》，确认允许抓取。
2. 多数化工/商品价格来自付费资讯，直接抓取可能违反其条款或构成侵权。
3. 遵守频率限制，设置合理请求间隔与 UA，避免对站点造成压力。
4. 本文件为「模板」，TARGET_URL 与 SELECTOR 需你按实际页面结构填充并自测。
5. 若你已有授权的 API / 付费数据，请另写适配器或在 fetch() 中调用接口。

实现方式：requests 拉取页面 → BeautifulSoup 按 SELECTOR 解析 → normalize 成标准结构。
"""
from .base import BaseSource

# TODO: 替换为具体商品行情页 URL
TARGET_URL = "https://www.100ppi.com/price/"
# TODO: 按实际页面 DOM 调整选择器
SELECTOR = ".price-table tr"


class Example100ppiSource(BaseSource):
    name = "100ppi-example"
    category = "vitamin"

    def fetch(self):
        try:
            import requests
            from bs4 import BeautifulSoup
        except ImportError:
            raise RuntimeError("请先 pip install requests beautifulsoup4")

        headers = {"User-Agent": "Mozilla/5.0 (compatible; PriceMonitor/1.0)"}
        resp = requests.get(TARGET_URL, headers=headers, timeout=15)
        resp.encoding = resp.apparent_encoding
        soup = BeautifulSoup(resp.text, "html.parser")

        rows = soup.select(SELECTOR)
        items = []
        for row in rows:
            # TODO: 按实际 DOM 解析出 name / price / spec 等字段
            # 例：cells = row.find_all("td")
            #      name = cells[0].get_text(strip=True)
            #      price = float(cells[1].get_text(strip=True).replace(",", ""))
            #      items.append({...})
            pass

        if not items:
            raise ValueError("未解析到任何价格，请检查 SELECTOR 与目标页面结构")
        return self.normalize(items)
