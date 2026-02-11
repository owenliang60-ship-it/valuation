# 组合构建层 — Portfolio Construction (决赛圈机制)

> **状态**: 设计讨论阶段，待 Boss 确认方向
> **日期**: 2026-02-09
> **问题**: OPRMS 是独立评级系统，20 只候选股的仓位之和可能远超 100%

---

## 问题定义

当前系统能力：
- L1: 个股分析 (5 Lens + Debate + Memo) → 这只股票好不好？
- L2: 个股定价 (OPRMS + Alpha) → 值多少仓位？
- **L3: 组合构建 ← 缺失** → 20 只候选里挑哪 10 只、各放多少？

OPRMS 在"真空中"给每只股票算仓位（DNA_cap × Timing_coeff × Regime_mult），
但没有考虑候选股之间的相互关系和总资本约束。

---

## 方案选项

### 路径 A：规则驱动（推荐）

```
1. 综合分数 = f(DNA权重, Timing系数, Conviction, Alpha EV, FCF质量)
2. 按分数降序排列 → 贪心分配
3. 每加一只，检查约束:
   - 总仓位 ≤ 目标 (e.g. 90%)
   - 单一行业 ≤ 35%
   - 高相关对 (ρ > 0.7) 不能同时满仓
   - 最多 15-20 只
4. 输出: 最终持仓表 + 候补 + 淘汰原因
```

优点：逻辑透明，每个决策有明确理由，容易人工 override
缺点：不是全局最优，贪心可能错过更好的组合

### 路径 B：优化驱动

```
1. 每只候选股: 预期收益分布 (Alpha EV) + 波动率
2. 相关矩阵 (已有 correlation.py) → 协方差矩阵
3. Mean-Variance 或 Risk Parity 优化
4. OPRMS DNA cap 作为上限约束
5. 输出: 最优权重分配
```

优点：数学全局最优，考虑股票间相关性
缺点：对预期收益估计敏感，"garbage in garbage out"

### 推荐：A 为主 + B 的相关性检查为辅

理由：
- 预期收益是定性估计，不够精确到跑 MVO
- 规则驱动容易解释和 override
- 相关矩阵可以作为约束注入，不需要全量优化
- 符合"Claude 分析、Boss 决策"架构

---

## 待确认的设计参数

1. 目标总仓位：90%？80%？还是根据 regime 动态调整？
2. 最大持仓数：10-15？还是更多？
3. 行业集中度上限：35%？
4. 路径选择：规则驱动 vs 优化驱动？

---

## 技术架构（如果实施）

```
portfolio/construction/
├── scorer.py           # 综合分数计算
├── allocator.py        # 贪心分配 + 约束检查
├── constraints.py      # 约束规则定义
└── report.py           # 决赛圈报告生成

输入: data/companies/*/oprms.json + alpha.json
输出: portfolio/construction/allocation_{date}.json
```

集成点：
- terminal/commands.py 新增 `run_construction()` 命令
- 依赖: company_db (OPRMS) + correlation.py + macro_fetcher (regime)
