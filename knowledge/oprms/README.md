# OPRMS 评级系统

双维度评级 → 仓位计算。来自 Heptabase "未来资本"白板。

## 核心公式

```
最终仓位 = 总资产 x DNA上限 x Timing系数
```

## Y 轴 — 资产基因 (DNA)

| 等级 | 名称 | 仓位上限 | 特征 |
|------|------|---------|------|
| S | 圣杯 | 25% | 改变人类进程的超级核心资产 |
| A | 猛将 | 15% | 强周期龙头，细分赛道霸主 |
| B | 黑马 | 7% | 强叙事驱动，赔率高但不确定 |
| C | 跟班 | 2% | 补涨逻辑，基本不做 |

## X 轴 — 时机系数 (Timing)

| 等级 | 名称 | 系数范围 | 特征 |
|------|------|---------|------|
| S | 千载难逢 | 1.0-1.5 | 历史性时刻，暴跌坑底/突破 |
| A | 趋势确立 | 0.8-1.0 | 主升浪确认，右侧突破 |
| B | 正常波动 | 0.4-0.6 | 回调支撑，震荡 |
| C | 垃圾时间 | 0.1-0.3 | 左侧磨底，无催化剂 |

## 用法

```python
from knowledge.oprms import calculate_position_size, DNARating, TimingRating

# NVDA: S 级资产，A 级时机，系数 0.9
result = calculate_position_size(
    total_capital=3_000_000,
    dna=DNARating.S,
    timing=TimingRating.A,
    timing_coeff=0.9,
)
# result.target_position_pct = 22.5%
# result.target_position_usd = $675,000
```

## 文件说明

| 文件 | 职能 |
|------|------|
| `models.py` | 数据模型: DNARating, TimingRating, OPRMSRating, PositionSize |
| `ratings.py` | 核心引擎: 仓位计算, 灵敏度表, JSON 读写 |
| `changelog.py` | 变更日志: JSONL 追加, 按 symbol 查询历史 |
| `integration.py` | 集成规范: Portfolio Desk JSON schema + 导出 |

## 数据文件

- 评级数据: `data/ratings/oprms.json`
- 变更日志: `data/ratings/oprms_changelog.jsonl`
- Portfolio 导出: `data/ratings/portfolio_export.json`
