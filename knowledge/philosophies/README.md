# 六大投资哲学透镜

基于 BidClub Ticker-to-Thesis 框架，6 位 AI 分析师各持一种投资哲学，从不同角度辩论同一只股票。

## 透镜总览

| # | 透镜 | 哲学 | 核心指标 | 投资期限 |
|---|------|------|---------|---------|
| 1 | Quality Compounder | 持久护城河，20+ 年复利 | ROIC | 永久 |
| 2 | Imaginative Growth | TAM 愿景，颠覆性潜力 | Revenue Growth | 5+ 年 |
| 3 | Fundamental L/S | Tiger Cub 对冲，相对价值 | EV/EBITDA | 1-3 年 |
| 4 | Deep Value | 安全边际，逆向投资 | Replacement Cost | 不定 |
| 5 | Event-Driven | 企业事件催化剂 | Catalyst Timeline | 6-18 月 |
| 6 | Macro-Tactical | Fed 政策，流动性 regime | Macro Alignment | Regime 依赖 |

## 用法

```python
from knowledge.philosophies import get_all_lenses, format_prompt

# 获取所有透镜
lenses = get_all_lenses()

# 用某个透镜生成分析 prompt
lens = lenses[0]  # Quality Compounder
prompt = format_prompt(lens, ticker="NVDA", context={
    "Financial Summary": "Revenue $60B, ROIC 45%, ...",
    "Recent News": "New GPU architecture announced...",
})
```

## 与辩论协议的关系

每个透镜对应一位 AI 分析师。在 `knowledge/debate/` 的 5 轮辩论中：
- Round 1-2 (Discovery): 每位分析师从自己的哲学出发提出独立论点
- Round 3-5 (Enrichment): 针对分歧深入辩论，用证据解决张力

## 文件说明

| 文件 | 内容 |
|------|------|
| `base.py` | InvestmentLens 数据模型 + prompt 填充工具 |
| `quality_compounder.py` | Buffett/Munger 风格质量复利 |
| `imaginative_growth.py` | 想象力成长，S-curve 早期 |
| `fundamental_ls.py` | Tiger Cub 基本面多空 |
| `deep_value.py` | Graham/Klarman 深度价值 |
| `event_driven.py` | 事件驱动催化剂 |
| `macro_tactical.py` | 宏观战术 regime |
