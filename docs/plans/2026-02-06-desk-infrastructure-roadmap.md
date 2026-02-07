# 未来资本 — Desk 数据基建路线图

> 创建日期: 2026-02-06
> 状态: 已审批，逐步推进
> 来源: 三路并行调研 + 基建缺口分析

---

## 背景

Phase 1（合并 + Desk 骨架）完成后，Data Desk 已完备（FMP API + 77 股票 + SQLite/CSV + 云端 cron）。
但其余 5 个 Desk 的数据基建为空。本文档规划每个 Desk 所需的底层数据和数据库。

核心发现：**FMP Starter 计划（$22/月）有十几个端点尚未使用，是最低果实。**

---

## Phase 2a — FMP 已有端点激活（$0 额外成本）

已付费但未采集的数据。按优先级排序。

### 2a-1. 分析师预期 + Forward P/E（极高优先级）

| 项目 | 详情 |
|------|------|
| **FMP 端点** | `financial-estimates`, `price-target-consensus`, `price-target-summary` |
| **采集频率** | 周频（跟基本面同步） |
| **存储** | `data/estimates/` JSON → 后续入 SQLite |
| **用途** | Forward P/E、营收预期、EPS 预期、目标价共识 |
| **服务 Desk** | Research + Portfolio |
| **为什么重要** | 现有 P/E 全是 trailing，缺 forward 估值。机构投资者看的是 forward。|
| **实现要点** | 扩展 `fmp_client.py` 新增 3 个方法，`fundamental_fetcher.py` 新增采集逻辑 |

### 2a-2. 财报日历（极高优先级）

| 项目 | 详情 |
|------|------|
| **FMP 端点** | `earnings-calendar` |
| **采集频率** | 周频 |
| **存储** | `data/calendar/earnings.json` |
| **用途** | 77 只股票的下次财报日期、历史 EPS surprise |
| **服务 Desk** | Risk + Trading |
| **为什么重要** | 期权持仓必须知道财报日期；Risk Desk 的回撤协议需要避开财报 |
| **实现要点** | 简单端点，单次调用可获取未来 3 个月所有财报日期 |

### 2a-3. 内幕交易（高优先级）

| 项目 | 详情 |
|------|------|
| **FMP 端点** | `insider-trading/latest`, `insider-trading/statistics` |
| **采集频率** | 日频 |
| **存储** | `data/insider/` JSON |
| **用途** | 内幕买卖信号，特别是 cluster buying |
| **服务 Desk** | Research |
| **为什么重要** | 大盘股内幕买入是学术验证的最强信号之一 |
| **实现要点** | 可做成类似 Dollar Volume 的日频扫描，异常时 Telegram 推送 |

### 2a-4. 新闻流（高优先级）

| 项目 | 详情 |
|------|------|
| **FMP 端点** | `stock-news`, `press-releases` |
| **采集频率** | 日频 |
| **存储** | `data/news/` 按日期 JSON |
| **用途** | 事件驱动信号 + LLM 摘要/情感分析的输入 |
| **服务 Desk** | Research |
| **为什么重要** | AI Research Desk 的基础输入之一 |
| **实现要点** | 按 symbol 拉取，每只取最近 10 条，去重存储 |

### 2a-5. 宏观经济指标（高优先级）

| 项目 | 详情 |
|------|------|
| **FMP 端点** | `treasury-rates`, `economic-calendar`, `market-risk-premium` |
| **采集频率** | 日频（利率）+ 周频（日历） |
| **存储** | `data/macro/` JSON/CSV |
| **用途** | 利率环境、经济事件日历、风险溢价 |
| **服务 Desk** | Risk + Knowledge |
| **为什么重要** | OPRMS Timing 系统需要宏观背景；期权定价需要无风险利率 |
| **实现要点** | 利率数据非常简洁，单条 JSON |

### 2a-6. 国会交易（中优先级）

| 项目 | 详情 |
|------|------|
| **FMP 端点** | `senate-trading`, `senate-latest`, `house-trading`, `house-latest` |
| **采集频率** | 周频 |
| **存储** | `data/congress/` JSON |
| **用途** | 国会议员买卖作为逆向/确认信号 |
| **服务 Desk** | Research |
| **为什么重要** | 独特数据源，别处不容易拿到结构化数据 |

### 2a-7. SEC 文件告警（中优先级）

| 项目 | 详情 |
|------|------|
| **FMP 端点** | `sec-filings/latest`, `sec-filings/symbol` |
| **采集频率** | 日频 |
| **存储** | `data/sec/` JSON |
| **用途** | 8-K 物质事件告警、10-K/10-Q 发布日期 |
| **服务 Desk** | Research + Risk |
| **为什么重要** | 8-K 是公司披露重大事件的法定渠道 |

### 2a-8. 行业表现（中优先级）

| 项目 | 详情 |
|------|------|
| **FMP 端点** | `sector-performance`, `sector-pe`, `industry-performance`, `industry-pe` |
| **采集频率** | 日频 |
| **存储** | `data/sector/` JSON |
| **用途** | 板块轮动检测、行业相对估值 |
| **服务 Desk** | Portfolio |
| **为什么重要** | 组合管理需要知道行业层面在发生什么 |

### 2a-9. 营收拆分（中优先级）

| 项目 | 详情 |
|------|------|
| **FMP 端点** | `revenue-product-segmentation`, `revenue-geographic-segments` |
| **采集频率** | 季频（随财报更新） |
| **存储** | `data/fundamental/segments.json` |
| **用途** | 理解集中持仓的收入结构（按产品、按地区） |
| **服务 Desk** | Research |
| **为什么重要** | 单只股 20%+ 仓位时，必须深度理解收入驱动 |

### 2a-10. 财务健康评分（中优先级）

| 项目 | 详情 |
|------|------|
| **FMP 端点** | `financial-scores` |
| **采集频率** | 周频 |
| **存储** | 扩展 `valuation.db` 或 `data/fundamental/scores.json` |
| **用途** | Piotroski F-Score（质量）、Altman Z-Score（破产风险） |
| **服务 Desk** | Risk |
| **为什么重要** | 自动化健康体检，异常时预警 |

### 2a-11. 已实现但未使用的端点（低成本激活）

| 端点 | 当前状态 | 行动 |
|------|---------|------|
| `key-metrics` | 代码已写，从未调用 | 加入采集流程，存储到 `data/fundamental/key_metrics.json` |
| `quote` | 代码已写，从未调用 | 暂不启用，等 Portfolio Desk 需要实时价格时再激活 |

### 2a-12. 其他可采集端点（低优先级）

| 端点 | 用途 | 存储 |
|------|------|------|
| `biggest-gainers`, `biggest-losers`, `top-traded-stocks` | 市场异动，补充 Dollar Volume | `data/movers/` |
| `company-share-float` | Float-adjusted RVOL | 扩展 profiles |
| `stock-peers` | 同业对比 | `data/fundamental/peers.json` |
| `dividends-company` | 股息历史、除息日 | `data/fundamental/dividends.json` |
| `stock-split-details` | 拆股事件 | `data/corporate_actions/` |
| `employee-count-historical` | 用人趋势 | `data/fundamental/employees.json` |
| `mergers-acquisitions/latest` | M&A 事件 | `data/corporate_actions/` |
| `enterprise-values` | EV 计算 | `data/fundamental/ev.json` |
| `owner-earnings` | Buffett 式现金流 | `data/fundamental/owner_earnings.json` |
| `financial-statement-growth` | 增长率 | `data/fundamental/growth.json` |

---

## Phase 2b — 现有数据推导计算（$0 额外成本）

用已有的 price CSV 和 fundamental JSON 计算推导。

### 2b-1. 相关性矩阵

| 项目 | 详情 |
|------|------|
| **数据源** | 现有 `data/price/*.csv` |
| **计算** | 滚动 60/120 日 Pearson 相关性 |
| **存储** | `risk/correlation/` CSV/pickle |
| **用途** | "你以为分散了其实是一个大赌注"检测 |
| **服务 Desk** | Risk |
| **实现** | pandas + numpy，定期重算 |

### 2b-2. 行业暴露分析

| 项目 | 详情 |
|------|------|
| **数据源** | 现有 `profiles.json` + 持仓数据（待建） |
| **计算** | 持仓金额按行业/个股聚合 |
| **存储** | Portfolio 报表 |
| **用途** | 行业集中度、单票集中度监控 |
| **服务 Desk** | Portfolio + Risk |

### 2b-3. 基准对比

| 项目 | 详情 |
|------|------|
| **数据源** | 需新采集 SPY、QQQ 日频价格（加入 price fetcher） |
| **计算** | 持仓 vs 基准的相对收益 |
| **存储** | `data/benchmark/` |
| **用途** | Alpha 归因、业绩评估 |
| **服务 Desk** | Portfolio |

### 2b-4. OPRMS 评级代码化

| 项目 | 详情 |
|------|------|
| **数据源** | Heptabase "未来资本"白板现有评级 |
| **存储** | `data/ratings/oprms.json` + `knowledge/oprms/` |
| **用途** | 仓位计算自动化：`总资产 × DNA上限 × Timing系数` |
| **服务 Desk** | Knowledge + Portfolio |

---

## Phase 2c — 需引入新数据源

### 2c-1. 期权数据（关键缺口）

| 项目 | 详情 |
|------|------|
| **FMP 状态** | 完全不提供期权数据 |
| **候选来源** | Tradier API（免费 sandbox）/ IBKR API / Polygon.io |
| **数据内容** | 期权链、Greeks（Δ/Γ/Θ/V）、IV、OI、Volume |
| **存储** | `data/options/` |
| **用途** | Greeks Dashboard、IV 曲面、期权策略回测 |
| **服务 Desk** | Risk + Trading |
| **优先级** | 取决于期权交易活跃度 |

### 2c-2. VIX + 信用利差

| 项目 | 详情 |
|------|------|
| **数据源** | FRED API（免费） |
| **数据内容** | VIX 指数、投资级/高收益信用利差、收益率曲线 |
| **存储** | `data/macro/` |
| **用途** | 市场恐慌指标、regime 检测 |
| **服务 Desk** | Risk + Knowledge |
| **实现** | `fredapi` Python 包，简单调用 |

### 2c-3. 13F 机构持仓

| 项目 | 详情 |
|------|------|
| **数据源** | SEC EDGAR（免费）或 FMP Ultimate（$149/月） |
| **数据内容** | 机构持仓变化、超级投资者跟踪 |
| **存储** | `data/institutional/` |
| **用途** | Buffett/Druckenmiller/Ackman 动向 |
| **服务 Desk** | Research |
| **优先级** | 中低 — 季度更新，信息滞后 45 天 |

---

## Phase 3 — 需付费升级（按需评估）

| 数据 | 来源 | 成本 | 用途 | 触发条件 |
|------|------|------|------|---------|
| **财报电话会议文字稿** | FMP Ultimate | $149/月 (+$127) | LLM 情感分析、管理层语调追踪 | AI Research Desk 建成后 |
| **13F 批量** | FMP Ultimate | 同上 | 机构持仓结构化数据 | SEC EDGAR 不够用时 |
| **日内数据** | FMP Premium | $59/月 (+$37) | 5min/15min K 线 | 暂不需要（日频足够） |
| **30 年历史** | FMP Premium | 同上 | 超长期回测 | 暂不需要 |

---

## 各 Desk 基建依赖汇总

### Research Desk

| 基建 | 来源 | Phase | 状态 |
|------|------|-------|------|
| Forward 估值 (Forward P/E) | FMP `financial-estimates` | 2a-1 | 待建 |
| 财报日历 | FMP `earnings-calendar` | 2a-2 | 待建 |
| 内幕交易 | FMP `insider-trading` | 2a-3 | 待建 |
| 新闻流 | FMP `stock-news` | 2a-4 | 待建 |
| 国会交易 | FMP `senate/house-trading` | 2a-6 | 待建 |
| SEC 文件 | FMP `sec-filings` | 2a-7 | 待建 |
| 营收拆分 | FMP `revenue-segmentation` | 2a-9 | 待建 |
| 投资备忘录库 | 人工 + AI | P0 纪律 | 待建 |
| 财报文字稿 | FMP Ultimate | Phase 3 | 待评估 |
| 13F 机构持仓 | EDGAR / FMP | 2c-3 | 待建 |

### Risk Desk

| 基建 | 来源 | Phase | 状态 |
|------|------|-------|------|
| IPS 文档 | 人工 | P0 纪律 | 待建 |
| 风控规则库 | 人工 | P0 纪律 | 待建 |
| 财报日历 | FMP | 2a-2 | 待建 |
| 宏观指标 | FMP + FRED | 2a-5 + 2c-2 | 待建 |
| 财务健康评分 | FMP `financial-scores` | 2a-10 | 待建 |
| 相关性矩阵 | 现有数据计算 | 2b-1 | 待建 |
| 期权敞口 | Tradier / IBKR | 2c-1 | 待建 |

### Trading Desk

| 基建 | 来源 | Phase | 状态 |
|------|------|-------|------|
| 交易日志数据库 | 手动/券商 | P0 纪律 | 待建 |
| 交易模板 | 人工 | P0 纪律 | 待建 |
| 策略库 | 人工 | P0 纪律 | 待建 |
| 市场异动 | FMP | 2a-12 | 待建 |

### Portfolio Desk

| 基建 | 来源 | Phase | 状态 |
|------|------|-------|------|
| 持仓数据库 | 手动 / IBKR | P1 | 待建 |
| 基准数据 | FMP 价格 | 2b-3 | 待建 |
| Watchlist | 人工 | P1 | 待建 |
| 行业暴露 | 现有数据计算 | 2b-2 | 待建 |
| 绩效归因 | 持仓 + 价格 | P2 | 待建 |
| Forward 估值 | FMP | 2a-1 | 待建 |
| 行业表现 | FMP | 2a-8 | 待建 |

### Knowledge Base

| 基建 | 来源 | Phase | 状态 |
|------|------|-------|------|
| OPRMS 评级代码化 | Heptabase | 2b-4 | 待建 |
| 宏观 regime | 宏观指标 | 2c-2 | 待建 |
| 投资哲学提取 | Heptabase | P3 | 待建 |

---

## FMP 端点能力边界

### Starter ($22/月) 能做的
- 300 calls/minute, 20 GB/月
- 5 年历史, 仅美股, 实时数据
- 所有基本面、估值、日频量价
- 分析师预期、财报日历、内幕交易、国会交易
- 新闻、SEC 文件、宏观经济
- 行业表现、营收拆分、财务评分
- 市场异动、企业行为

### Starter 做不到的
| 数据 | 需要哪个计划 | 替代方案 |
|------|-------------|---------|
| 期权数据 | **任何计划都没有** | Tradier / IBKR / Polygon.io |
| 财报文字稿 | Ultimate ($149) | Seeking Alpha / LSEG |
| 13F 持仓 | Ultimate ($149) | SEC EDGAR 免费 |
| 日内数据 | Premium ($59) | 暂不需要 |
| 30 年历史 | Premium ($59) | 暂不需要 |
| 技术指标 API | Premium ($59) | 已有本地计算 |
| 债券数据 | **不提供** | FRED API 免费 |
| Level 2 / 订单簿 | **不提供** | 券商 API |

---

## 实现顺序建议

```
Week 1: P0 纪律文档（IPS + 风控规则 + 交易日志模板）
         ↓ 不写代码，纯文档，但 ROI 最高

Week 2: 2a-1 分析师预期 + 2a-2 财报日历
         ↓ 最高价值的两个新数据源

Week 3: 2a-3 内幕交易 + 2a-5 宏观指标
         ↓ 信号类数据

Week 4: 2a-4 新闻流 + 2a-7 SEC 文件
         ↓ 事件类数据

Week 5: 2b-1 相关性矩阵 + 2b-2 行业暴露
         ↓ 现有数据推导

Week 6: 2a-8 行业表现 + 2a-9 营收拆分 + 2a-10 财务评分
         ↓ 补充分析维度

Week 7+: 2c 新数据源（期权、VIX、13F）
          ↓ 按需评估
```

---

## 技术实现模式（统一规范）

每个新数据采集器应遵循现有 Data Desk 模式：

```
1. fmp_client.py 新增方法（API 调用 + 限流）
2. 对应 fetcher 模块（采集 + 缓存逻辑）
3. update_data.py 新增 --flag
4. cron 脚本注册
5. data_query.py 暴露查询接口
6. 云端部署（sync_to_cloud.sh）
```

新增数据存储规范：
- JSON 缓存：`data/{类型}/` 目录，带 `_meta` 时间戳
- 需要查询的数据：入 SQLite（扩展 valuation.db 或新建）
- CSV 仅用于时序数据（价格类）
