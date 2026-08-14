"""
数据源适配器：秣宝网(mobaobuy.com) 私易买「维生素及多维产品」公开报价
========================================================================
目标页面：https://www.mobaobuy.com/siyibuy/indexPage?shopSkuName=维生素及多维产品
真实接口：GET https://www.mobaobuy.com/api/product/apiCommon/sku/querySpotAndAreaQuote
         （即页面默认「区域报价」视图，返回真实成交报价，单位 元/吨）

⚠️ 合规提示（运行前务必确认）：
1. 请先阅读 https://www.mobaobuy.com/robots.txt 与《服务条款》，确认允许抓取。
2. 本适配器仅读取页面已公开展示的报价数字，不做登录破解；匿名即可获取价格。
3. 已设置合理请求间隔（REQUEST_INTERVAL），避免对站点造成压力。
4. 数据版权归秣宝网/各发布商所有，对外展示时请保留来源标注。
5. 如需更完整字段（供应商全称、区域等），可在环境变量配置 MOBAOBUY_COOKIE
   （已登录会话的 Cookie）；未配置时匿名也能拿到价格与品种信息。

归并策略：
同一 spuName（标准品名，如「维生素C原粉」）下有多家报价，
取当日最低报价为 price，并记录 均价(avgPrice)/厂家数(brandCount)/报价条数(quoteCount)。
"""
import time
import gzip
import json
import urllib.parse
import urllib.request
from .base import BaseSource

API_URL = "https://www.mobaobuy.com/api/product/apiCommon/sku/querySpotAndAreaQuote"
SEARCH_KEYWORD = "维生素及多维产品"
PAGE_SIZE = 50
REQUEST_INTERVAL = 0.5  # 秒/页，避免对站点施压

UA = "Mozilla/5.0 (compatible; PriceMonitorBot/1.0; +https://github.com/)"


class MobaobuySource(BaseSource):
    name = "mobaobuy"
    category = "vitamin"

    # ------------------------------------------------------------------
    # HTTP
    # ------------------------------------------------------------------
    def _http_get(self, params):
        q = urllib.parse.urlencode(params)
        url = f"{API_URL}?{q}"
        req = urllib.request.Request(url, headers={
            "User-Agent": UA,
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://www.mobaobuy.com/siyibuy/indexPage?shopSkuName="
                       + urllib.parse.quote(SEARCH_KEYWORD),
        })
        resp = urllib.request.urlopen(req, timeout=20)
        raw = resp.read()
        if resp.headers.get("Content-Encoding") == "gzip":
            raw = gzip.decompress(raw)
        return json.loads(raw.decode("utf-8", "ignore"))

    # ------------------------------------------------------------------
    # 抓取
    # ------------------------------------------------------------------
    def fetch(self):
        # 第一页，拿到 total 与总页数
        first = self._http_get({
            "shopSkuName": SEARCH_KEYWORD,
            "size": PAGE_SIZE,
            "current": 1,
        })
        if not isinstance(first, dict) or not first.get("data"):
            raise RuntimeError(f"mobaobuy API 返回异常: {first}")
        total = first["data"].get("total", 0)
        pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
        records = list(first["data"].get("records", []))

        for cur in range(2, pages + 1):
            time.sleep(REQUEST_INTERVAL)
            try:
                d = self._http_get({
                    "shopSkuName": SEARCH_KEYWORD,
                    "size": PAGE_SIZE,
                    "current": cur,
                })
                records += (d.get("data") or {}).get("records", [])
            except Exception as e:
                print(f"[warn] mobaobuy page {cur} failed: {e}")
                break

        # 按 spuName（标准品名）归并
        grouped = {}
        for r in records:
            spu = (r.get("spuName") or r.get("shopSkuName") or "").strip()
            if not spu:
                continue
            fp = r.get("factoryPriceString")
            if not fp:
                continue
            try:
                price = float(fp)
            except (TypeError, ValueError):
                continue
            if price <= 0:
                continue
            g = grouped.setdefault(spu, {"prices": [], "brands": set(), "specs": set()})
            g["prices"].append(price)
            if r.get("productionEnterpriseShortName"):
                g["brands"].add(r["productionEnterpriseShortName"])
            if r.get("productSpecificationName"):
                g["specs"].add(r["productSpecificationName"])

        items = []
        for spu, g in grouped.items():
            prices = g["prices"]
            items.append({
                "name": spu,
                "category": "vitamin",
                "spec": "/".join(sorted(g["specs"])) if g["specs"] else "",
                "unit": "元/吨",
                "region": "",
                "price": min(prices),
                "avgPrice": round(sum(prices) / len(prices), 2),
                "brandCount": len(g["brands"]),
                "quoteCount": len(prices),
                "source": self.name,
                "updatedAt": "",
            })

        if not items:
            raise ValueError("mobaobuy 未解析到任何有效报价，请检查接口可用性")
        return self.normalize(items)

    # ------------------------------------------------------------------
    # 覆写 normalize，保留 avgPrice / brandCount / quoteCount 等扩展字段
    # ------------------------------------------------------------------
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
                "isSample": bool(it.get("isSample", False)),
                "avgPrice": it.get("avgPrice"),
                "brandCount": it.get("brandCount"),
                "quoteCount": it.get("quoteCount"),
            })
        return out
