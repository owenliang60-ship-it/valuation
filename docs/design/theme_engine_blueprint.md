# 市场主线识别系统 — Theme Engine 设计蓝图

> 设计日期: 2026-02-13 Session 17
> 状态: 设计完成，待实现

---

## 核心目标

系统性识别市场中出现的早期趋势和财富效应最集中的赛道。

**设计哲学**：量价引擎发现"什么在动"，注意力引擎确认"为什么在动"。

**参考案例**：2025年4月关税 dip 后，内存赛道（SNDK/MU/WDC）财富效应集中爆发。

---

## 双引擎架构

### 引擎 A：量价动量（纯 OHLCV 数据，零外部依赖）

| 信号 | 核心逻辑 | 频率 | 数据需求 |
|------|---------|------|---------|
| 相关性聚类变化 | 60日滚动相关→层次聚类→Jaccard对比上周→NEW_FORMATION | 周频 | price CSV |
| IBD-style RS Rating | 0.4×3mo + 0.2×6mo + 0.2×9mo + 0.2×12mo → 百分位排名 1-99 | 周频 | price CSV |
| Dollar Volume Rank 加速 | 5日均Dollar Volume排名 vs 20日均排名，跳升>15位=信号 | 日频 | price CSV |
| RVOL 持续放量 | 连续3-5天 RVOL > 2σ = 机构建仓 | 日频 | price CSV (已有指标) |
| PMARP 极端信号 | >98% 极端超涨 / <2% 回升 = 超跌反转 | 日频 | price CSV (云端已扫描) |

**关键公式**：

```
# IBD RS Rating
RS_Raw = 0.4 * Return_3M + 0.2 * Return_6M + 0.2 * Return_9M + 0.2 * Return_12M
RS_Rating = PercentileRank(RS_Raw) * 98 + 1

# 相关性聚类
Distance = sqrt(2 * (1 - correlation))
Linkage = Ward's method
Threshold = 0.6 (broad) / 0.7 (tight)
New Theme = Jaccard(current_cluster, all_prev_clusters) < 0.3

# Dollar Volume 加速
DV_short = mean(close * volume, 5d)
DV_long = mean(close * volume, 20d)
Rank_acceleration = Rank_long - Rank_short  # >15 = signal
```

### 引擎 B：注意力量化（外部 API，全免费）

| 信号 | 工具/API | 成本 | 频率 | 衡量维度 |
|------|---------|------|------|---------|
| Google Trends | pytrends (Topic ID) | $0 | 周频 | 公众注意力 |
| Reddit 提及量 | PRAW (r/stocks, r/investing, r/wallstreetbets, r/options) | $0 | 日频 | 投资者社区热度 |
| 新闻提及频率 | Finnhub (免费60req/min) + FMP (已有) | $0 | 日频 | 媒体关注度 |

**每个信号归一化方式**：计算 Z-score（当前值 vs 30/90日均值），统一到可比尺度。

### 池子动态扩展机制

```
核心池（$1000亿+ 科技/金融/医疗/消费/通信）~77只
    ↓ 每日/每周固定扫描

注意力引擎广撒网（不限市值/行业）
    ↓ 输出 Top 10-20 热度 tickers

热度股自动拉取价格数据 → 纳入下周量价扫描池
    ↓ 连续 N 周在热度榜 → 观察池常驻
    ↓ 从热度榜消失 N 周 → 自动移出
```

**注意力广撒网方式**：
- Google Trends：追踪主题关键词（"DRAM", "AI chip", "quantum"等），发现热门主题后反查相关股票
- Reddit：扫描 daily discussion，正则提取 $TICKER 格式的高频提及
- Finnhub：market news 端点统计 ticker 本周新闻频率

---

## 信号优先级与组合逻辑

### 时间领先关系

```
财报关键词（季频，最早但最慢）
    → 相关性聚类形成 + OBV背离（T+1周）
        → RVOL持续放量 + DV加速（T+2周）
            → Google Trends + Reddit + 新闻（T+3-4周）
```

**量价信号领先注意力信号 1-2 周**。引擎A发现，引擎B确认。

### 主题生命周期与信号对应

| 阶段 | 引擎A信号 | 引擎B信号 | 行动 |
|------|----------|----------|------|
| 发现期 | 聚类开始出现，相关性0.3→0.5 | 无明显信号 | 观察 |
| 早期采纳 | RS Rating top quartile，间歇放量 | Google Trends开始上升 | 研究+小仓 |
| 加速期 | 聚类确认(>0.7)，RVOL持续，PMARP>98% | Reddit+新闻爆发，Trends飙升 | 主仓位 |
| 拥挤期 | RS接近99但动量放缓，DV不再加速 | 注意力到顶但波动加大 | 减仓/止盈 |
| 均值回归 | 聚类维持但方向反转，PMARP从高位回落 | 情绪急转负面 | 清仓 |

---

## 已排除的方向

| 方向 | 排除原因 |
|------|---------|
| 空头利息变化 | 复杂，数据源不确定 |
| ETF 资金流加速 | 需要额外付费数据源 |
| 期权 Call Skew 陡峭化 | 复杂度高 |
| 分析师覆盖启动潮 | 复杂度高 |
| 主题篮子市场宽度 | 复杂度高 |
| OBV 背离 | 逻辑不够直观 |
| 财报关键词密度 | 季频太滞后 |

---

## 模块规划

| 模块 | 路径 | 功能 |
|------|------|------|
| `momentum.py` | `src/indicators/` | RS Rating + 横截面动量排名 |
| `theme_scanner.py` | `src/analysis/` | 相关性聚类 + 聚类变化检测 + DV加速 |
| `attention.py` | `terminal/` | Google Trends + Reddit + Finnhub 注意力引擎 |
| `theme_pool.py` | `terminal/` | 池子动态扩展管理 |
| `scan_themes.py` | `scripts/` | 每周扫描入口，输出主线报告 |

### 依赖关系

```
已有: src/indicators/rvol.py, src/indicators/pmarp.py
已有: src/analysis/correlation.py (需扩展聚类)
已有: config/settings.py (股票池)
已有: terminal/tools/ (FMP API)
新增: pytrends, praw, finnhub-python (pip install)
```

### 计算量

- 77只股票全套扫描 < 5秒
- 相关性矩阵 77×77 < 1秒
- 层次聚类 < 1秒
- 笔记本完全够用，无需云端

---

## 实现路线（待细化）

- **P0**: 引擎A量价动量模块（纯本地数据，可立即实现）
- **P1**: 引擎B注意力量化（需接入外部API）
- **P2**: 池子动态扩展 + 主线报告输出
- **P3**: 与现有 terminal pipeline / deep analysis 集成
- **P4**: 云端自动化（每日/每周 cron）

---

## 参考资料

- Heptabase 卡片「系统性识别市场主题/叙事 — 学术与实践综合研究报告」
- BlackRock "Tomorrow's Themes, Today" 框架
- MSCI Security Crowding Model（四维拥挤度，简化版可用）
