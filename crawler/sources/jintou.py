"""金投网（jiage.cngold.org）有机溶剂每日价格适配器。

数据来源：金投网「金投价格」频道，公开可爬（robots.txt 仅禁止 /templets、/errorpage 等，
价格栏目页未被禁止）。站点对价格页未设 WAF，可稳定抓取。

采集策略（两跳）：
  1) 抓取品种栏目页  https://jiage.cngold.org/<slug>/
     取页面中第一个 /c/YYYY-MM-DD/cNNNNNNN.html 链接 = 当日最新报价文章
  2) 抓取该文章页，解析价格表：
     <td id="nameTd_0">品名</td><td>规格</td>
     <td><span class="dzPrice" data-id="..">价格</span></td><td>（元/吨）</td>

合规提示：价格页标注“本站所有行情数据均来自于网络，所有价格均为参考价格，
不具备市场交易依据”，本适配器仅作行情参考展示，已在 source 字段标明来源。

注意：生意社（100ppi.com）全站启用了华为云 WAF（HW_CHECK Cookie 挑战），
其首页/列表/sitemap 均无法程序化访问，仅已知具体 detail 文章 URL 可开，
无法自动定位“当日最新”文章，且绕过 WAF 违反其服务条款，故不采用。
"""
import re
import time
import urllib.request
import gzip

from .base import BaseSource

CATEGORY = "solvent"
SOURCE_NAME = "金投网"
HOST = "https://jiage.cngold.org"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Accept-Encoding": "gzip, deflate",
}

# 品种中文名 -> 金投网栏目 slug（均已实测可访问）
COMMODITIES = {
    "丙酮": "bingtong",       # 丙酮
    "冰醋酸": "cusuan",       # 醋酸（即冰醋酸）
    "二甲苯": "erjiaben",      # 二甲苯
    "甲醇": "jiachun",        # 甲醇
    "乙醇": "yichun",         # 乙醇
}

# 文章价格表行：品名 / 规格 / 价格(span) / 单位
ROW_RE = re.compile(
    r'<td id="nameTd_\d+">(.*?)</td>\s*'
    r'<td>(.*?)</td>\s*'
    r'<td><span class="dzPrice"[^>]*>(.*?)</span></td>\s*'
    r'<td>(.*?)</td>',
    re.S,
)
ARTICLE_LINK_RE = re.compile(r'/c/\d{4}-\d{2}-\d{2}/c\d+\.html')
TAG_RE = re.compile(r'<[^>]+>')


def _fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    resp = urllib.request.urlopen(req, timeout=25)
    raw = resp.read()
    if resp.headers.get("Content-Encoding") == "gzip":
        raw = gzip.decompress(raw)
    return raw.decode("utf-8", "ignore")


def _clean(text):
    return TAG_RE.sub("", text).strip()


def _to_float(s):
    s = (s or "").replace(",", "").replace("（", "").replace("）", "").strip()
    try:
        return float(s)
    except ValueError:
        return None


class JintouSource(BaseSource):
    name = SOURCE_NAME
    category = CATEGORY

    def fetch(self):
        items = []
        for name, slug in COMMODITIES.items():
            try:
                cat_html = _fetch(f"{HOST}/{slug}/")
                m = ARTICLE_LINK_RE.search(cat_html)
                if not m:
                    print(f"[warn] {name}: 栏目页未找到文章链接")
                    continue
                article_url = HOST + m.group(0)
                art_html = _fetch(article_url)

                rows = ROW_RE.findall(art_html)
                if not rows:
                    print(f"[warn] {name}: 文章页未解析到价格行 ({article_url})")
                    continue

                # 取首行作为该品种代表报价
                raw_name, spec, price_txt, unit_txt = rows[0]
                cname = _clean(raw_name) or name
                price = _to_float(price_txt)
                unit = _clean(unit_txt).replace("（", "").replace("）", "") or "元/吨"
                if price is None:
                    print(f"[warn] {name}: 价格解析为空 ({price_txt})")
                    continue

                items.append({
                    "name": name,                 # 统一用标准中文名（冰醋酸而非醋酸）
                    "displayName": cname,         # 站内原始名（醋酸）
                    "category": CATEGORY,
                    "spec": _clean(spec),
                    "unit": unit,
                    "region": "全国",
                    "price": price,
                    # 不提供 prevPrice：由 scraper 依据历史计算日涨跌
                    "priceLabel": "当日参考价",
                    "source": SOURCE_NAME,
                    "sourceUrl": article_url,
                    "isSample": False,
                    # 金投网单条快照，无聚合字段
                    "avgPrice": None,
                    "brandCount": None,
                    "quoteCount": None,
                })
                print(f"[ok] {name}: {price} {unit} (规格 {_clean(spec)})")
                time.sleep(0.5)  # 礼貌限速
            except Exception as e:
                print(f"[warn] {name}: 抓取失败 {e}")
        return items
