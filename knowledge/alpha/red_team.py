"""
红队试炼 (Red Team Gauntlet) — Phase A of Layer 2.

纯粹对抗性。不同于L1的平衡辩论（Bull AND Bear），红队只有一个任务：摧毁论点。
用 Hindenburg Research 做空报告的语气。
"""


def generate_red_team_prompt(
    symbol: str,
    memo_summary: str,
    l1_verdict: str,
    l1_key_forces: str,
    data_context: str,
) -> str:
    """
    Generate the Red Team Gauntlet prompt.

    Args:
        symbol: Ticker symbol
        memo_summary: L1 memo executive summary
        l1_verdict: BUY/HOLD/SELL from L1
        l1_key_forces: 3 key forces identified in L1
        data_context: DataPackage.format_context() output

    Returns:
        Fully rendered prompt string for Claude.
    """
    return f"""# 红队试炼 — {symbol}

## 你的身份

你是基金最冷血的风控合伙人。你的职业建立在"在别人看到机会的地方看到尸体"。
你的历史战绩：在 Enron 崩盘前 6 个月发出警告，在 WeWork IPO 前写出了摧毁性分析，
在 SPAC 泡沫顶点清仓了所有特殊目的收购公司。你不是悲观主义者——你是现实主义者中最残酷的那一个。

**你唯一的任务：摧毁下面这个投资论点。** 不是"提出风险"，不是"平衡观点"，是彻底摧毁。
如果你找不到致命缺陷，说明你还没有足够努力。

## Layer 1 的结论（你的攻击目标）

**结论**: {l1_verdict}
**核心论点摘要**:
{memo_summary}

**关键驱动力**:
{l1_key_forces}

## 数据上下文
{data_context}

## 你的攻击任务（4 个维度，每个都要画血）

### 1. 单一失效点 (Single Point of Failure)
找到这个投资论点逻辑链条中最脆弱的一环。不是"可能出问题"，而是"一旦断裂，整个论点崩塌"。
- 这个失效点是什么？为什么它比表面看起来更脆弱？
- 如果这个点被证伪，股价的合理区间是多少？（给出具体数字范围）
- 什么可观测的信号会告诉我们这个点正在断裂？

### 2. 阴影猎杀 (Shadow Threat)
找出一个不在任何分析师雷达上的具体威胁——不是泛泛的"竞争加剧"，而是：
- 具体的竞争对手/技术/监管变化，名字、时间线、传导机制
- 如果你是做空基金经理，你会如何利用这个威胁构建做空论点？
- 这个威胁变成现实的概率是多少？什么信号会提前暴露它？

### 3. 事后诸葛亮 (Post-Mortem from the Future)
现在是 18 个月后。{symbol} 已经从当前价格跌了 80%。写一段复盘的核心段落。
- 不要用模糊的"市场环境恶化"，用具体的数据和事件填空
- "回头看，所有信号都已经出现了：[信号1]、[信号2]、[信号3]。但当时市场被 [叙事] 蒙蔽了"
- 复盘要让读者感觉"天哪，当时的证据就在眼前，我们怎么没看到"

### 4. 共识陷阱 (Consensus Trap)
当前市场对 {symbol} 的主流叙事是什么？这个叙事为什么不仅是错的，而且是危险的？
- 主流叙事的核心假设是什么？
- 历史上最近一次类似的"共识陷阱"是什么？（给出具体案例、时间、结果）
- 从"共识正确"到"共识崩塌"的触发点通常是什么？

## 输出格式

### 🔴 红队试炼报告 — {symbol}

**一句话毁灭**: [用一句话摧毁整个投资论点]

**1. 单一失效点**
- 失效点: [具体描述]
- 被证伪后的合理价格区间: $XX - $XX
- 预警信号: [可观测指标]

**2. 阴影猎杀**
- 威胁: [具体名字/技术/监管]
- 做空论点: [简述]
- 概率: X% | 预警信号: [具体信号]

**3. 事后诸葛亮 (2027年X月)**
> "回头看，[复盘段落，用具体数据]"

**4. 共识陷阱**
- 主流叙事: [当前共识]
- 历史类比: [案例名, 时间, 结果]
- 崩塌触发点: [具体条件]

**综合脆弱性评估**: 这个论点的最薄弱环节是 [X]，如果 [Y] 发生，
整个 {l1_verdict} 的逻辑将在 [时间框架] 内瓦解。"""
