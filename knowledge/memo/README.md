# 投资备忘录模板

机构级投资备忘录框架，确保每份备忘录达到可执行的研究标准。

## 评分体系

| 维度 | 权重 | 衡量内容 |
|------|------|---------|
| Thesis Clarity | 25% | 可证伪的论点、显式关键力量、变异观点 |
| Evidence Quality | 25% | 3+ 主要来源、8-10+ 总来源、经事实核查 |
| Valuation Rigor | 20% | 多种方法、敏感性分析、IRR 计算 |
| Risk Framework | 15% | Kill conditions、仓位规模依据、下行情景 |
| Decision Readiness | 15% | 行动价格、进出规则、可观测里程碑 |

**目标分数**: > 7.0/10

## 必需章节

1. **Executive Summary** -- ticker, bucket, variant view, target IRR, action price
2. **Variant View** -- 市场共识 vs 我们的观点, 为什么市场错了
3. **Investment Thesis** -- 可证伪声明 + 3 个关键力量
4. **Evidence Base** -- 按层级组织的证据链
5. **Valuation** -- DCF + 可比公司 + 反向 DCF + IRR
6. **Key Analytical Tensions** -- 3 个张力 (问题 / 正方 / 反方 / 决议)
7. **Risk Framework** -- Kill conditions + 下行情景 + 仓位规模
8. **Action Plan** -- 行动价格 + 进出规则 + 里程碑 + 复查节奏

## 证据层级

| 层级 | 来源 | 最低要求 |
|------|------|---------|
| Primary | CEO 采访、财报电话会、专利、内幕交易、客户反馈 | 3+ |
| Secondary | 分析师报告、行业研究 | -- |
| Tertiary | 新闻摘要、社交媒体 | -- |
| **Total** | | **8-10+** |

## 写作标准

- 80%+ 主动语态
- 每段一个观点
- 主题句在前
- 消灭对冲词 (might, could, perhaps, arguably)
- 12,000-20,000 字符的实质分析
- 所有证据经事实核查

## IRR 门槛

- **Long**: >= 15% expected IRR
- **Short**: >= 20-25% expected IRR
- **PASS**: 达不到门槛就不做，无论定性多好

## 用法

```python
from knowledge.memo.template import generate_memo_skeleton
from knowledge.memo.scorer import check_completeness, check_writing_standards

# 生成骨架
skeleton = generate_memo_skeleton("NVDA", "Long-term Compounder")

# 检查完整性
completeness = check_completeness(memo_text)

# 检查写作标准
standards = check_writing_standards(memo_text)
```

## 文件说明

| 文件 | 职能 |
|------|------|
| `template.py` | 备忘录模板: 必需章节 + markdown 骨架生成 |
| `scorer.py` | 评分引擎: 5 维度评分 + 完整性检查 + 写作标准检查 |
| `evidence.py` | 证据层级: 分类 + 验证规则 + 格式化输出 |
