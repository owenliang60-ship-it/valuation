# 研究辩论协议

5 轮迭代辩论结构，6 位 AI 分析师各持不同投资哲学，由 Research Director 主持。

## 辩论流程

```
Round 1 (Discovery) — 各分析师独立陈述论点
    |
Round 2 (Discovery) — 交叉质询，识别 3 个关键张力
    |
Round 3 (Enrichment) — 深入张力 1，新证据 + 显式裁决
    |
Round 4 (Enrichment) — 深入张力 2 和 3
    |
Round 5 (Enrichment) — 最终裁决 + Director 合成投资备忘录
```

## 阶段说明

### Discovery (Round 1-2)
- 广泛探索，识别关键力量
- 每位分析师从自己的哲学出发独立分析
- Round 2 交叉质询后，Director 提炼出 3 个关键张力

### Enrichment (Round 3-5)
- 针对每个张力深入辩论
- 必须提出新证据，不得重复旧论点
- 显式裁决: ACCEPT / REJECT / PARTIALLY ACCEPT
- Round 5 合成最终投资备忘录

## 分析师参与规则 (核心 8 条)

1. **引用再回复** -- 回复前引用对方原文
2. **显式裁决** -- ACCEPT / REJECT / PARTIALLY ACCEPT
3. **承认错误** -- 证据推翻时坦然修正
4. **新证据要求** -- Round 3+ 每个主张需要新证据
5. **禁止对冲** -- 不用 might, could, perhaps
6. **一点一块** -- 每个回复块只讲一个观点
7. **禁止翻旧账** -- Enrichment 阶段不重新辩论已解决的问题
8. **可证伪主张** -- 每个论点必须有可观测、可衡量的判断标准

## Research Director 职责

- 主持辩论，确保高质量争论
- 防止群体思维、循环论证
- Round 2 结束时提炼 3 个关键张力
- Round 5 合成最终投资备忘录 + OPRMS 评级
- 干预触发: 循环论证、过早共识、无证据主张、答非所问

## 文件说明

| 文件 | 职能 |
|------|------|
| `protocol.py` | 5 轮辩论结构、prompt 生成、协议概述 |
| `analyst_rules.py` | 8 条参与规则 + 回复格式模板 |
| `director_guide.py` | Director 角色、干预触发、各轮主持 prompt、合成模板 |

## 与其他模块的关系

- **philosophies/**: 6 个分析师透镜，每位对应一种哲学
- **memo/**: Round 5 合成使用 memo 模板和评分体系
- **oprms/**: Director 在 Round 5 分配 OPRMS DNA 和 Timing 评级
