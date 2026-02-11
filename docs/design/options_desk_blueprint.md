# 期权交易台设计蓝图

> 创建日期: 2026-02-11
> 状态: 概念设计，待详细规划
> 触发: NET 分析启发 — 给定标的+看法，推荐期权策略

---

## 核心需求

给定一个标的 + 对该标的的看法（时间周期 + 涨跌预期），期权交易台根据波动率数据和股票特点推荐合适的策略。

## 核心流程

```
输入                    引擎                      输出
─────────────────    ─────────────────    ─────────────────
Ticker: NET          ┌─ Vol Analysis ─┐   策略推荐 Top 3
View: 看多            │  IV Rank/Pctl  │   ├─ 具体行权价+到期日
Timeframe: 6M        │  IV vs HV      │   ├─ Greeks Profile
Magnitude: +15-25%   │  Term Structure│   ├─ Max P&L + Breakeven
Conviction: 中高      │  Skew          │   ├─ P&L 图
OPRMS context ──────→│  Earnings Cal  │──→├─ 风险场景分析
                     │  ──────────── │   └─ Kill Conditions
                     │  Strategy     │
                     │  Selector     │
                     └───────────────┘
```

## 策略选择决策树

```
                    ┌─ IV Rank > 50%? ─┐
                    │                   │
                  YES                  NO
                    │                   │
            卖权利金优先           买权利金优先
                    │                   │
        ┌──── 方向？────┐      ┌──── 方向？────┐
        │       │       │      │       │       │
      Bull    Neutral  Bear  Bull   Neutral   Bear
        │       │       │      │       │       │
   Put Credit  Iron   Call   Bull    Long    Bear
   Spread    Condor  Credit  Call   Straddle  Put
   /Naked Put        Spread  Spread /Calendar Spread
                                    /LEAPS
```

### 第二层决策因子

| 因子 | 影响 |
|------|------|
| **时间窗口** | <1M → weeklies/monthlies, 3-6M → 季度, >6M → LEAPS |
| **Conviction** | 高 → 集中、directional; 低 → spread、defined risk |
| **Earnings 距离** | <2 周 → 避免或专门做 earnings play; >1M → 正常策略 |
| **IV Term Structure** | Backwardation → 卖近买远 (calendar); Contango → 正常 |
| **Skew** | Put skew 陡 → put credit spread 性价比好; Flat → call debit spread |
| **OPRMS DNA** | S/A → 可以卖 put 接货; B/C → 避免无限下行敞口 |
| **Regime** | CRISIS/RISK_OFF → 缩小 position, 加宽 spread; RISK_ON → 正常 |

## 模块设计

```
terminal/
├── options/                    # 期权交易台
│   ├── data/                   # 数据层
│   │   ├── chain_fetcher.py    # 期权链获取
│   │   ├── vol_surface.py      # 波动率曲面构建
│   │   └── greeks.py           # Greeks 计算/验证
│   ├── analysis/               # 分析层
│   │   ├── iv_analysis.py      # IV rank/pctl, HV vs IV, term structure
│   │   ├── skew_analysis.py    # Put/call skew 分析
│   │   └── earnings_vol.py     # Earnings implied move 计算
│   ├── strategy/               # 策略层
│   │   ├── selector.py         # 决策树：view → strategy candidates
│   │   ├── optimizer.py        # 行权价/到期日优化
│   │   ├── pnl.py              # P&L profile 计算
│   │   └── templates.py        # 策略模板定义
│   ├── risk/                   # 风控层
│   │   ├── position_sizer.py   # 期权仓位计算 (与 OPRMS 集成)
│   │   ├── scenario.py         # 压力测试
│   │   └── greeks_monitor.py   # 组合 Greeks 监控
│   └── commands.py             # 顶层入口
```

## 与现有系统集成

| 集成点 | 方式 |
|--------|------|
| OPRMS → Position Sizing | DNA/Timing 决定期权名义敞口上限 |
| Macro Regime → Strategy Filter | CRISIS 时禁用裸卖策略，强制 defined risk |
| Earnings Calendar → Expiry Selection | 自动避开/利用财报日期 |
| Analysis Pipeline → View Input | deep analysis 结论直接喂给期权台 |
| Monitor → Greeks Alerts | portfolio monitor 扩展期权 Greeks 监控 |

## 数据源需求

需要: 期权链、Greeks、历史 IV、波动率曲面
当前 FMP 不支持期权数据，需要新数据源。

详见: `docs/design/options_data_research.md`（待调研）

## 分阶段路线

1. **P0**: 选定数据源，写 chain_fetcher
2. **P1**: IV 分析模块 + 策略选择器（决策树）
3. **P2**: P&L 计算 + 行权价优化 + OPRMS 集成
4. **P3**: Greeks 监控 + 压力测试 + 展期提醒

## NET 启发案例

View: 看多 AI agent 论点，$180 估值偏高，愿意回调入场，6-12 月

推荐策略组合:
1. **Sell Put $155-160 (3-4M)** — 收租等回调，被 assign 就是目标价入场
2. **Bull Call Spread $185/$220 (6M)** — 定义风险捕捉上行
3. **组合: Risk Reversal 变体** — 卖 put 收入 fund call spread
