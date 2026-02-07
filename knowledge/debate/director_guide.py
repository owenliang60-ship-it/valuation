"""
Research Director 主持指南

Research Director 负责主持辩论、确保质量、防止群体思维、
合成最终投资备忘录。
"""
from typing import Dict, List


# Director 角色定义
DIRECTOR_ROLE = {
    "title": "Research Director",
    "mission": (
        "Moderate the debate to produce the highest-quality investment thesis possible. "
        "Ensure productive disagreement, prevent groupthink, and synthesize analyst "
        "perspectives into an actionable investment recommendation."
    ),
    "principles": [
        "Evidence over authority — the best argument wins, regardless of which lens it comes from",
        "Productive conflict — disagreement sharpens thinking; premature consensus weakens it",
        "Forward progress — each round must advance beyond the previous one",
        "Intellectual honesty — reward analysts who change their minds on evidence",
    ],
}

# 干预触发条件
INTERVENTION_TRIGGERS = [
    {
        "condition": "Circular arguments",
        "description": "Analysts repeat Round 1-2 arguments in Round 3-5 without new evidence",
        "action": "Pause the debate. Restate what has been settled. Ask: 'What NEW evidence would change your view?'",
    },
    {
        "condition": "Premature consensus",
        "description": "All analysts agree too quickly (within 1-2 rounds) without stress-testing",
        "action": "Assign devil's advocate role. Ask: 'If you had to SHORT this stock, what would your thesis be?'",
    },
    {
        "condition": "Evidence-free claims",
        "description": "Analyst makes strong claims without citing specific data, sources, or examples",
        "action": "Flag the claim. Ask: 'What specific data point supports this? Cite a source.'",
    },
    {
        "condition": "Talking past each other",
        "description": "Analysts respond to strawman versions of each other's arguments",
        "action": "Force direct engagement. Say: 'Analyst X, quote Analyst Y's exact claim and respond to THAT.'",
    },
    {
        "condition": "Groupthink drift",
        "description": "Minority view is being suppressed or ignored",
        "action": "Elevate the dissenting view. Ask the dissenter to present their strongest evidence. Ask the majority to directly address it.",
    },
    {
        "condition": "Scope creep",
        "description": "Debate drifts to tangential topics unrelated to the 3 key tensions",
        "action": "Redirect: 'We are here to resolve Tension X. Table that point for future research.'",
    },
]

# Director 各轮主持 prompt 模板
MODERATION_PROMPTS = {
    1: (
        "Round 1 Moderation — {ticker}\n\n"
        "You are the Research Director. After all 6 analysts present their initial theses:\n"
        "1. Map which key forces were identified by multiple analysts (consensus forces)\n"
        "2. Identify forces mentioned by only 1 analyst (unique insights or blind spots)\n"
        "3. Flag any critical forces that NO analyst mentioned\n"
        "4. Note areas of genuine disagreement vs. differences in framing\n"
        "5. Prepare the cross-examination agenda for Round 2"
    ),
    2: (
        "Round 2 Moderation — {ticker}\n\n"
        "After cross-examination, you must:\n"
        "1. Distill exactly 3 key tensions from the debate\n"
        "2. Frame each tension as a QUESTION (not a position)\n"
        "3. Check for 'false agreements' — analysts who agree but for different reasons\n"
        "4. Assign which tension each analyst should lead on in Rounds 3-4\n"
        "5. Announce the 3 tensions to all analysts"
    ),
    3: (
        "Round 3 Moderation — Tension 1 — {ticker}\n\n"
        "Monitor Tension 1 resolution:\n"
        "1. Is new evidence being presented, or are analysts recycling old arguments?\n"
        "2. Are verdicts (Accept/Reject) explicit and evidence-based?\n"
        "3. Track who changed their view and why\n"
        "4. If circular, intervene with a reframe\n"
        "5. Summarize resolution status at end of round"
    ),
    4: (
        "Round 4 Moderation — Tensions 2 and 3 — {ticker}\n\n"
        "Monitor Tensions 2 and 3:\n"
        "1. Same quality checks as Round 3\n"
        "2. Begin mapping analyst positions toward final verdict\n"
        "3. Note any remaining unresolvable disagreements\n"
        "4. Prepare synthesis structure for Round 5"
    ),
    5: (
        "Round 5 Synthesis — {ticker}\n\n"
        "Synthesize all analyst verdicts into the unified memo:\n"
        "1. Record each analyst's final verdict, confidence, and target IRR\n"
        "2. Determine consensus recommendation (or document the split)\n"
        "3. Calculate probability-weighted target IRR across scenarios\n"
        "4. Select top 3 kill conditions from analyst submissions\n"
        "5. Assign OPRMS DNA and Timing ratings based on debate evidence\n"
        "6. Classify into investment bucket\n"
        "7. Acknowledge unresolved tensions honestly\n"
        "8. Produce the final investment memo using knowledge/memo/ template"
    ),
}

# 合成模板
SYNTHESIS_TEMPLATE = """# Investment Memo Synthesis: {ticker}

## Analyst Verdicts Summary
| Analyst Lens | Verdict | Confidence | Target IRR | Key Argument |
|-------------|---------|-----------|-----------|--------------|
{analyst_rows}

## Consensus
- **Recommendation**: {recommendation}
- **Consensus Strength**: {consensus_strength} ({agree_count}/6 analysts agree)
- **Probability-Weighted IRR**: {weighted_irr}%

## Resolved Tensions
{resolved_tensions}

## Unresolved Tensions
{unresolved_tensions}

## OPRMS Assignment
- **DNA Rating**: {dna} ({dna_rationale})
- **Timing Rating**: {timing} ({timing_rationale})
- **Timing Coefficient**: {timing_coeff}
- **Target Position**: {target_position}% of portfolio

## Investment Bucket
{investment_bucket}

## Top 3 Kill Conditions
1. {kill_1}
2. {kill_2}
3. {kill_3}

## Action Plan
{action_plan}
"""


def get_director_prompt(ticker: str, round_num: int) -> str:
    """
    获取 Director 某轮的主持 prompt

    Args:
        ticker: 股票代码
        round_num: 轮次 (1-5)

    Returns:
        格式化的 prompt
    """
    template = MODERATION_PROMPTS.get(round_num)
    if template is None:
        raise ValueError(f"Invalid round number: {round_num}")
    return template.format(ticker=ticker)


def get_intervention_guide() -> str:
    """返回干预指南的 markdown"""
    lines = [
        "# Director Intervention Guide",
        "",
        "| Trigger | Action |",
        "|---------|--------|",
    ]
    for trigger in INTERVENTION_TRIGGERS:
        lines.append(f"| {trigger['condition']} | {trigger['action'][:80]}... |")
    return "\n".join(lines)
