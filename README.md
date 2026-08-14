# 化工原料每日价格监测（网页版）

托管于 GitHub Pages 的静态价格看板，价格由 GitHub Actions 定时爬虫采集。
监测品种：已接入「维生素」（数据源：秣宝网 mobaobuy.com 公开报价）；丙酮、冰醋酸、二甲苯（有机溶剂类）待接入。

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
│   └── sources/ (mock / example_100ppi / mobaobuy)
└── .github/workflows/crawl.yml
```

## 本地运行
```bash
# 1) 生成/更新数据
python crawler/scraper.py                 # 默认 mobaobuy（真实数据，需联网）
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

## 待接入的数据源
- 有机溶剂类：丙酮、冰醋酸、二甲苯（在 `crawler/sources/` 下新增适配器，参考 `example_100ppi.py` 模板）。

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
