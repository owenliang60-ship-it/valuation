"""
投资备忘录模板 — 必需章节和骨架生成

每份备忘录必须包含: 变异观点、Kill Conditions、3 个关键张力、
多种估值方法、带进出规则的行动价格。
"""
from typing import List


# 四种投资桶分类
INVESTMENT_BUCKETS = [
    "Long-term Compounder",   # 质量复利，3+ 年
    "Catalyst-Driven Long",   # 事件驱动做多，6-18 月
    "Short Position",         # 做空，高估+已定义风险
    "Secular Short",          # 结构性做空，3-5+ 年
]

# 必需章节 (按顺序)
MEMO_SECTIONS = [
    {
        "id": "executive_summary",
        "title": "Executive Summary",
        "description": "Ticker, investment bucket, variant view, target IRR, action price, one-paragraph thesis.",
        "required": True,
    },
    {
        "id": "variant_view",
        "title": "Variant View",
        "description": "What does the market believe, and why is the market wrong? This is the single most important section.",
        "required": True,
    },
    {
        "id": "thesis",
        "title": "Investment Thesis",
        "description": "Falsifiable thesis statement. 3 key forces driving the investment. Clear causal chain.",
        "required": True,
    },
    {
        "id": "evidence",
        "title": "Evidence Base",
        "description": "3+ primary sources, 8-10+ total. Organized by evidence hierarchy. Fact-checked.",
        "required": True,
    },
    {
        "id": "valuation",
        "title": "Valuation",
        "description": "Multiple methods (DCF, comparables, reverse DCF). Sensitivity tables. IRR calculation.",
        "required": True,
    },
    {
        "id": "tensions",
        "title": "Key Analytical Tensions",
        "description": "3 substantive debates. Each with: the tension (question), case for, case against, resolution.",
        "required": True,
    },
    {
        "id": "risk_framework",
        "title": "Risk Framework",
        "description": "Kill conditions (observable, measurable). Downside scenarios. Position sizing rationale.",
        "required": True,
    },
    {
        "id": "action_plan",
        "title": "Action Plan",
        "description": "Action price, entry rules, exit rules, observable milestones, review cadence.",
        "required": True,
    },
]


def generate_memo_skeleton(ticker: str, bucket: str) -> str:
    """
    生成投资备忘录的 markdown 骨架

    Args:
        ticker: 股票代码
        bucket: 投资桶分类

    Returns:
        带所有必需章节的 markdown 模板
    """
    lines = [
        f"# Investment Memo: {ticker}",
        "",
        f"**Investment Bucket**: {bucket}",
        f"**Date**: [YYYY-MM-DD]",
        f"**Analyst**: [Name]",
        f"**OPRMS Rating**: DNA [S/A/B/C] | Timing [S/A/B/C] | Coeff [X.X]",
        "",
        "---",
        "",
    ]

    for section in MEMO_SECTIONS:
        lines.append(f"## {section['title']}")
        lines.append("")
        lines.append(f"*{section['description']}*")
        lines.append("")

        if section["id"] == "executive_summary":
            lines.extend([
                f"- **Ticker**: {ticker}",
                f"- **Bucket**: {bucket}",
                "- **Variant View**: [One sentence: what the market believes vs. your view]",
                "- **Target IRR**: [X%]",
                "- **Action Price**: $[X] (current: $[Y])",
                "- **Thesis**: [One paragraph falsifiable thesis]",
                "",
            ])
        elif section["id"] == "variant_view":
            lines.extend([
                "### Market Consensus",
                "[What does the market believe?]",
                "",
                "### Our View",
                "[Why is the market wrong? What are we seeing that others miss?]",
                "",
                "### Evidence for Variant",
                "1. [Primary evidence point]",
                "2. [Primary evidence point]",
                "3. [Primary evidence point]",
                "",
            ])
        elif section["id"] == "thesis":
            lines.extend([
                "### Falsifiable Thesis Statement",
                "[If X happens by Y date, then Z — otherwise we are wrong]",
                "",
                "### Three Key Forces",
                "1. **[Force 1]**: [Description + evidence]",
                "2. **[Force 2]**: [Description + evidence]",
                "3. **[Force 3]**: [Description + evidence]",
                "",
            ])
        elif section["id"] == "evidence":
            lines.extend([
                "### Primary Sources (3+ required)",
                "1. [CEO interview / earnings call / direct data]",
                "2. [Stakeholder signal / customer feedback]",
                "3. [Behavioral data / patent / insider activity]",
                "",
                "### Secondary Sources",
                "4. [Analyst report]",
                "5. [Industry research]",
                "...",
                "",
                "**Total sources**: [X] (minimum 8-10)",
                "",
            ])
        elif section["id"] == "valuation":
            lines.extend([
                "### Method 1: DCF",
                "| Assumption | Bear | Base | Bull |",
                "|-----------|------|------|------|",
                "| Revenue Growth | X% | Y% | Z% |",
                "| Terminal Multiple | Xa | Ya | Za |",
                "| **Fair Value** | $X | $Y | $Z |",
                "",
                "### Method 2: Comparable Companies",
                "[EV/EBITDA, P/E, P/FCF vs peers]",
                "",
                "### Method 3: Reverse DCF",
                "[What growth rate is implied by current price?]",
                "",
                "### IRR Calculation",
                "- **Base case IRR**: X% (target: >= 15% long, >= 20-25% short)",
                "- **Probability-weighted IRR**: Y%",
                "",
            ])
        elif section["id"] == "tensions":
            for i in range(1, 4):
                lines.extend([
                    f"### Tension {i}: [Question framing the debate]",
                    f"**Case For**: [Strongest argument + evidence]",
                    "",
                    f"**Case Against**: [Strongest counter-argument + evidence]",
                    "",
                    f"**Resolution**: [What tipped the scales and why]",
                    "",
                ])
        elif section["id"] == "risk_framework":
            lines.extend([
                "### Kill Conditions",
                "1. **[Condition 1]**: [Observable, measurable trigger — NOT a calendar date]",
                "2. **[Condition 2]**: [e.g., gross margin < 60% for 2 consecutive quarters]",
                "3. **[Condition 3]**: [e.g., CEO departure, key customer loss]",
                "",
                "### Downside Scenarios",
                "| Scenario | Probability | Price Target | Loss from Entry |",
                "|----------|------------|-------------|----------------|",
                "| Bear | X% | $Y | -Z% |",
                "| Stress | X% | $Y | -Z% |",
                "",
                "### Position Sizing",
                "- OPRMS DNA cap: [X%]",
                "- Timing coefficient: [Y]",
                "- Target position: [Z% of portfolio]",
                "",
            ])
        elif section["id"] == "action_plan":
            lines.extend([
                "### Entry Rules",
                "- Action price: $[X]",
                "- Entry method: [Limit / scale-in / options]",
                "- Initial size: [X% of target, scale to full on confirmation]",
                "",
                "### Exit Rules",
                "- Target exit: $[X] ([Y%] upside)",
                "- Stop loss: $[X] ([Y%] downside)",
                "- Time stop: [Review if thesis not confirmed by DATE]",
                "",
                "### Observable Milestones",
                "| Milestone | Expected By | Status |",
                "|-----------|------------|--------|",
                "| [Milestone 1] | [Date] | Pending |",
                "| [Milestone 2] | [Date] | Pending |",
                "",
                "### Review Cadence",
                "- Weekly: price action + news scan",
                "- Monthly: thesis validation check",
                "- Quarterly: full re-underwriting post earnings",
                "",
            ])

        lines.append("---")
        lines.append("")

    # Writing standards reminder
    lines.extend([
        "## Writing Standards Checklist",
        "- [ ] 80%+ active voice",
        "- [ ] No hedge words on beliefs (remove: might, could, perhaps, arguably)",
        "- [ ] One idea per paragraph",
        "- [ ] Topic sentences first",
        "- [ ] 12,000-20,000 characters of substantive analysis",
        "- [ ] All evidence fact-checked and sourced",
        f"- [ ] Target memo score: > 7.0/10",
    ])

    return "\n".join(lines)


def get_section_names() -> List[str]:
    """返回所有必需章节 ID"""
    return [s["id"] for s in MEMO_SECTIONS]
