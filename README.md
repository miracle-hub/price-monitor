# 化工原料每日价格监测（网页版）

托管于 GitHub Pages 的静态价格看板，价格由 GitHub Actions 定时爬虫采集。
监测品种：已接入「维生素」（数据源：秣宝网 mobaobuy.com 真实公开报价）与「有机溶剂」丙酮 / 冰醋酸 / 二甲苯 / 甲醇 / 乙醇（数据源：金投网 jiage.cngold.org 真实公开报价）。均为真实数据，页面标注来源。

## 功能
- 今日价格看板（按 维生素 / 有机溶剂 分组，红涨绿跌）
- 品种详情 + 30 日价格趋势图（ECharts）
- 爬虫每日定时采集，自动提交并触发 Pages 重新部署

## 目录结构
```
price-monitor/
├── index.html / detail.html   # 前端看板 / 详情
├── assets/                    # 样式与脚本
├── data/                      # 爬虫产出（latest.json / history.json）
├── crawler/                   # 爬虫框架与数据源适配器
│   ├── scraper.py
│   └── sources/ (mock / example_100ppi / mobaobuy / jintou / solvent_demo)
└── .github/workflows/crawl.yml
```

## 本地运行
```bash
# 1) 生成/更新数据
python crawler/scraper.py                  # 默认 all（维生素+有机溶剂，均为真实数据，需联网）
python crawler/scraper.py --source mobaobuy # 仅维生素（秣宝网真实）
python crawler/scraper.py --source jintou   # 仅有机溶剂（金投网真实）：丙酮/冰醋酸/二甲苯/甲醇/乙醇
python crawler/scraper.py --source solvent # 有机溶剂「示例/估算」数据（占位演示，非真实）
python crawler/scraper.py --source mock   # 本地演示，无需联网

# 2) 启动本地服务器预览（fetch 需经 http，不能用 file:// 直接打开）
python -m http.server 8000
# 浏览器访问 http://localhost:8000
```

## 部署到 GitHub Pages
1. 将本仓库推送到 GitHub（`git init` 后添加远程并 push）。
2. 仓库 Settings → Pages → Source 选择 `main` 分支、`/ (root)` 目录 → Save。
3. Actions 中 `daily-crawl` 会按 cron 每日运行；也可在 Actions 页手动 `Run workflow` 立即触发。

> 注意：GitHub 免费版计划任务在仓库 **60 天无提交后会自动暂停**，有更新即恢复。

## 已接入的数据源

### 秣宝网 mobaobuy.com（维生素类，真实数据）
- 来源页面：`https://www.mobaobuy.com/siyibuy/indexPage?shopSkuName=维生素及多维产品`
- 适配器：`crawler/sources/mobaobuy.py`，调用公开接口 `querySpotAndAreaQuote` 获取真实报价（单位 元/吨）。
- 运行：`python crawler/scraper.py --source mobaobuy`（GitHub Actions 已默认此源）。
- 归并规则：同一标准品名（spuName，如「维生素C原粉」）下多家报价，取**最低价**为当日价，并附 `avgPrice`（均价）/ `brandCount`（厂家数）/ `quoteCount`（报价条数）。
- 合规：仅读取页面已公开展示的报价数字，未做登录破解；匿名即可获取价格。运行前请确认其 `robots.txt` 与《服务条款》允许抓取。

### 金投网 jiage.cngold.org（有机溶剂类，真实数据）
- 覆盖品种：**丙酮、冰醋酸、二甲苯、甲醇、乙醇**（金投网栏目 slug：bingtong / cusuan / erjiaben / jiachun / yichun）。
- 适配器：`crawler/sources/jintou.py`。采集策略（两跳）：
  1. 抓取品种栏目页 `https://jiage.cngold.org/<slug>/`，取页面首个 `/c/YYYY-MM-DD/cNNNNNNN.html` 链接（即当日最新报价文章）；
  2. 抓取该文章页，解析价格表（品名 / 规格 / 价格 / 单位），取首行作为该品种当日参考价。
- 运行：`python crawler/scraper.py --source jintou`。
- 合规：金投网 `robots.txt` 仅禁止 `/templets`、`/errorpage` 等管理路径，价格栏目页未被禁止，可合规抓取；其页面声明"所有价格均为参考价格，不具备市场交易依据"，本仓库仅作行情参考展示，已在 `source` 字段标明来源。

> 关于生意社（100ppi.com）：用户曾建议从其采集。实测该站全站启用华为云 WAF（`HW_CHECK` Cookie 挑战），**首页 / 列表 / sitemap 均无法程序化访问**，仅已知具体 `detail-*.html` 文章 URL 可打开，无法自动定位"当日最新"文章；且绕过 WAF 违反其服务条款，故未采用。若后续获得其授权 API，可参照 `mobaobuy.py` 新建适配器接入。

## 有机溶剂「示例 / 估算」占位（可选，非真实）
> `crawler/sources/solvent_demo.py` 仅提供**示例/估算**数据（带 `isSample` 标记，前端显示橙色「示例」徽标），用于站点结构演示。**默认生产流程（`--source all`）已不含此源**，不会误发示例值。如需本地演示带标注的占位数据，可运行 `python crawler/scraper.py --source solvent`。

## 接更多数据源（通用方法）
默认示例适配器 `crawler/sources/example_100ppi.py` 为**模板**，需你：
1. 先确认目标站点的 `robots.txt` 与《服务条款》允许抓取；
2. 多数化工/商品价格为付费资讯，**直接抓取可能违约或侵权**，请优先使用公开可爬源或你已授权的 API；
3. 在适配器里填好 `TARGET_URL` 与 `SELECTOR`，按真实 DOM 解析字段；
4. 运行 `python crawler/scraper.py --source example` 自测，无误后并入 `--source all`。

新增数据源：在 `crawler/sources/` 下新建一个继承 `BaseSource` 的类，实现 `fetch()` 即可。

## 合规与免责
- 本仓库仅为技术框架示例，所采集数据的版权与合规性由使用者负责。
- 页面展示的价格**仅供参考，以实际成交为准**。
- 请合理设置抓取频率，避免对目标站点造成压力。
