"""
分析师参与规则 — 辩论行为准则

确保辩论是高质量的、基于证据的、有建设性的。
"""
from typing import Dict, List


# 核心参与规则
ENGAGEMENT_RULES = [
    {
        "id": "quote_before_respond",
        "rule": "Quote the exact critique or claim you are responding to before stating your response.",
        "rationale": "Prevents strawmanning. Forces engagement with the actual argument, not a caricature.",
        "example": (
            'Analyst 2 claimed: "NVDA\'s data center revenue growth will decelerate to 20% by 2027." '
            "I REJECT this claim. My evidence: ..."
        ),
    },
    {
        "id": "explicit_verdict",
        "rule": "State an explicit verdict on each critique: ACCEPT, REJECT, or PARTIALLY ACCEPT.",
        "rationale": "No ambiguity. Readers must know exactly where you stand.",
        "example": "PARTIALLY ACCEPT: The deceleration risk is real for enterprise GPU, but hyperscaler demand offsets it.",
    },
    {
        "id": "acknowledge_errors",
        "rule": "When evidence disproves your position, acknowledge the error explicitly and update your view.",
        "rationale": "Intellectual honesty. Changing your mind on evidence is strength, not weakness.",
        "example": "I was wrong about the margin trajectory. Q3 data shows 75% gross margin, not the 68% I projected. Updating my model.",
    },
    {
        "id": "new_evidence_required",
        "rule": "In Rounds 3-5, every claim must be supported by new evidence not cited in previous rounds.",
        "rationale": "Prevents circular arguments. Forces research depth.",
        "example": "New evidence: Patent filing US2025/0123456 (filed Jan 2026) shows NVDA expanding into robotics inference chips.",
    },
    {
        "id": "no_hedge_language",
        "rule": "No hedge words on your beliefs. State convictions directly.",
        "rationale": "Hedging obscures signal. If you are uncertain, quantify the uncertainty (60% confident) instead of hedging.",
        "bad_example": "It might be possible that revenue could potentially exceed expectations.",
        "good_example": "Revenue will exceed consensus by 15% (confidence: 75%).",
    },
    {
        "id": "one_idea_per_block",
        "rule": "One idea per response block. Structure arguments as numbered points.",
        "rationale": "Prevents wall-of-text syndrome. Makes it easy for others to quote and respond.",
    },
    {
        "id": "no_relitigating",
        "rule": "In Enrichment rounds (3-5), do not re-litigate debates that were resolved in Discovery.",
        "rationale": "Forward progress only. If a point was accepted by consensus in Round 2, build on it.",
    },
    {
        "id": "falsifiable_claims",
        "rule": "Every thesis statement must be falsifiable with observable, measurable criteria.",
        "rationale": "Unfalsifiable claims are worthless for investment decisions.",
        "bad_example": "NVDA is a great company with good management.",
        "good_example": "NVDA will grow data center revenue >30% YoY through FY2027, evidenced by hyperscaler CAPEX commitments.",
    },
]


def format_analyst_response_template(analyst_lens: str, round_num: int) -> str:
    """
    生成分析师回复的格式模板

    Args:
        analyst_lens: 分析师哲学透镜名称
        round_num: 当前轮次

    Returns:
        markdown 格式的回复模板
    """
    lines = [
        f"## {analyst_lens} Analyst — Round {round_num}",
        "",
    ]

    if round_num == 1:
        lines.extend([
            "### My Thesis",
            "[Falsifiable thesis statement]",
            "",
            "### Key Forces (from my lens)",
            "1. **[Force 1]**: [Evidence]",
            "2. **[Force 2]**: [Evidence]",
            "3. **[Force 3]**: [Evidence]",
            "",
            "### Initial Recommendation",
            "- Verdict: [BUY / HOLD / SELL / PASS]",
            "- Target IRR: [X%]",
            "- Confidence: [HIGH / MEDIUM / LOW]",
        ])
    elif round_num == 2:
        lines.extend([
            "### Response to Other Analysts",
            "",
            "**Re: [Analyst Name]'s claim that \"[exact quote]\"**",
            "- Verdict: [ACCEPT / REJECT / PARTIALLY ACCEPT]",
            "- My counter-evidence: [...]",
            "",
            "### Blind Spots I Identified",
            "1. [What other analyses missed]",
            "",
            "### Updated View",
            "[Any changes from Round 1]",
        ])
    else:  # Rounds 3-5
        lines.extend([
            "### Addressing Tension: [Tension statement]",
            "",
            "**Responding to: \"[exact quote from previous round]\"**",
            "- Verdict: [ACCEPT / REJECT / PARTIALLY ACCEPT]",
            "- NEW evidence (not cited before): [...]",
            "",
        ])
        if round_num == 5:
            lines.extend([
                "### FINAL Verdict",
                "- Recommendation: [BUY / HOLD / SELL / PASS]",
                "- Confidence: [HIGH / MEDIUM / LOW]",
                "- Target IRR: [X%]",
                "- Key evidence that shaped my view: [...]",
                "- Biggest remaining risk: [...]",
                "- Critical kill condition: [...]",
            ])

    return "\n".join(lines)


def get_rules_summary() -> str:
    """返回规则摘要的 markdown"""
    lines = [
        "# Analyst Engagement Rules",
        "",
        "| # | Rule | Rationale |",
        "|---|------|-----------|",
    ]

    for i, rule in enumerate(ENGAGEMENT_RULES, 1):
        lines.append(f"| {i} | {rule['rule'][:80]} | {rule['rationale'][:60]} |")

    return "\n".join(lines)
