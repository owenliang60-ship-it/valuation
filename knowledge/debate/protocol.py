"""
5 轮辩论协议 — 从 Discovery 到 Enrichment

基于 BidClub Ticker-to-Thesis 框架:
- Round 1-2: Discovery — 广泛探索，每位分析师独立陈述
- Round 3-5: Enrichment — 深化证据，解决张力，达成共识或明确分歧
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class DebateRound:
    """单轮辩论定义"""
    round_number: int
    phase: str           # "discovery" | "enrichment"
    title: str
    objectives: List[str]
    analyst_instructions: str
    director_focus: str  # Research Director 本轮关注点


# 5 轮辩论定义
ROUNDS: List[DebateRound] = [
    DebateRound(
        round_number=1,
        phase="discovery",
        title="Initial Thesis Presentation",
        objectives=[
            "Each analyst presents their independent thesis from their philosophy lens",
            "Identify the 3-5 key forces that will drive this investment",
            "Surface initial areas of agreement and disagreement",
        ],
        analyst_instructions=(
            "Present your thesis on {ticker} from your {lens_name} perspective. "
            "State your view as a falsifiable claim. Identify 2-3 key forces "
            "you believe will drive the outcome. Do NOT try to address other "
            "lenses yet — focus on your strongest argument from your own framework."
        ),
        director_focus=(
            "Map the landscape: which forces do multiple analysts identify? "
            "Where are the genuine disagreements vs. differences in framing? "
            "Flag any key forces that no analyst mentioned but should be explored."
        ),
    ),
    DebateRound(
        round_number=2,
        phase="discovery",
        title="Cross-Examination and Gap Identification",
        objectives=[
            "Analysts respond to each other's Round 1 presentations",
            "Identify blind spots in each lens's analysis",
            "Narrow down to 3 key tensions that must be resolved",
        ],
        analyst_instructions=(
            "Review the other analysts' Round 1 theses. For each one:\n"
            "1. Quote their specific claim\n"
            "2. State whether you AGREE, DISAGREE, or PARTIALLY AGREE\n"
            "3. Provide counter-evidence or supporting evidence from your lens\n"
            "4. Identify what their analysis missed that your framework catches\n\n"
            "Be direct. No diplomatic hedging. Quote exact claims before responding."
        ),
        director_focus=(
            "Distill the 3 most important tensions from the cross-examination. "
            "These become the focus for Rounds 3-5. Ensure tensions are framed as "
            "questions, not positions. Check: are there any 'false agreements' where "
            "analysts agree for different reasons?"
        ),
    ),
    DebateRound(
        round_number=3,
        phase="enrichment",
        title="Deep Dive — Tension 1",
        objectives=[
            "Resolve (or sharpen) the first key tension identified in Round 2",
            "Bring NEW evidence — no restating Round 1-2 arguments",
            "Each analyst must explicitly Accept or Reject the opposing view",
        ],
        analyst_instructions=(
            "Focus on Tension 1: {tension_1}\n\n"
            "Rules for this round:\n"
            "- You MUST bring new evidence not cited in Rounds 1-2\n"
            "- Quote the specific critique you are responding to\n"
            "- State your verdict: ACCEPT / REJECT / PARTIALLY ACCEPT\n"
            "- If you accept a critique, acknowledge what you got wrong\n"
            "- If you reject, provide specific counter-evidence\n"
            "- Do NOT re-litigate settled debates from previous rounds"
        ),
        director_focus=(
            "Is Tension 1 resolving with evidence, or are analysts talking past each other? "
            "If circular, intervene with a reframe. Track which analysts changed their view "
            "and whether the change was evidence-based."
        ),
    ),
    DebateRound(
        round_number=4,
        phase="enrichment",
        title="Deep Dive — Tension 2 and 3",
        objectives=[
            "Resolve tensions 2 and 3",
            "Continue requiring new evidence for each claim",
            "Begin converging on investment verdict",
        ],
        analyst_instructions=(
            "Focus on Tensions 2 and 3:\n"
            "- Tension 2: {tension_2}\n"
            "- Tension 3: {tension_3}\n\n"
            "Same rules as Round 3: new evidence, quote critiques, "
            "explicit verdicts, acknowledge errors. Additionally:\n"
            "- Begin stating your overall investment recommendation\n"
            "- If you changed your view from Round 1, explain what evidence caused the change"
        ),
        director_focus=(
            "Are tensions resolving? Map each analyst's current position: "
            "BUY / HOLD / SELL / PASS. Identify any remaining genuine disagreements "
            "vs. differences in emphasis. Prepare synthesis structure."
        ),
    ),
    DebateRound(
        round_number=5,
        phase="enrichment",
        title="Final Verdict and Synthesis",
        objectives=[
            "Each analyst delivers final recommendation with confidence level",
            "Research Director synthesizes into unified memo recommendation",
            "Produce actionable output: verdict, price target, sizing, kill conditions",
        ],
        analyst_instructions=(
            "Deliver your FINAL verdict on {ticker}:\n"
            "1. Recommendation: BUY / HOLD / SELL / PASS\n"
            "2. Confidence: HIGH / MEDIUM / LOW\n"
            "3. Target IRR: X%\n"
            "4. Key evidence that shaped your final view\n"
            "5. Biggest remaining risk\n"
            "6. One kill condition you consider most critical\n\n"
            "If your view changed during the debate, state what changed and why. "
            "No hedging — commit to a position."
        ),
        director_focus=(
            "Synthesize all analyst verdicts into a unified memo:\n"
            "1. Consensus recommendation (or document the split)\n"
            "2. Probability-weighted target IRR\n"
            "3. Top 3 kill conditions\n"
            "4. Position sizing recommendation via OPRMS\n"
            "5. Investment bucket classification\n"
            "6. Key tensions that remain unresolved (acknowledge them)"
        ),
    ),
]


def get_round(round_number: int) -> Optional[DebateRound]:
    """获取指定轮次的辩论定义"""
    for r in ROUNDS:
        if r.round_number == round_number:
            return r
    return None


def generate_round_prompt(
    round_num: int,
    ticker: str,
    lens_name: str = "",
    tensions: Optional[List[str]] = None,
    previous_summary: str = "",
) -> str:
    """
    生成某一轮辩论的 prompt

    Args:
        round_num: 轮次 (1-5)
        ticker: 股票代码
        lens_name: 分析师的哲学透镜名称
        tensions: 3 个关键张力 (Round 3+ 需要)
        previous_summary: 前几轮的摘要

    Returns:
        格式化的 prompt 字符串
    """
    debate_round = get_round(round_num)
    if debate_round is None:
        raise ValueError(f"Invalid round number: {round_num}")

    tensions = tensions or ["[Tension 1 TBD]", "[Tension 2 TBD]", "[Tension 3 TBD]"]

    instructions = debate_round.analyst_instructions.format(
        ticker=ticker,
        lens_name=lens_name,
        tension_1=tensions[0] if len(tensions) > 0 else "",
        tension_2=tensions[1] if len(tensions) > 1 else "",
        tension_3=tensions[2] if len(tensions) > 2 else "",
    )

    objectives_block = "\n".join(f"- {obj}" for obj in debate_round.objectives)

    lines = [
        f"# Round {round_num}: {debate_round.title}",
        f"**Phase**: {debate_round.phase.title()} | **Ticker**: {ticker}",
        "",
        "## Objectives",
        objectives_block,
        "",
    ]

    if previous_summary:
        lines.extend([
            "## Previous Rounds Summary",
            previous_summary,
            "",
        ])

    lines.extend([
        "## Your Instructions",
        instructions,
        "",
    ])

    return "\n".join(lines)


def get_protocol_summary() -> str:
    """返回完整辩论协议的 markdown 概述"""
    lines = [
        "# Research Debate Protocol — 5 Rounds",
        "",
        "| Round | Phase | Title | Focus |",
        "|-------|-------|-------|-------|",
    ]

    for r in ROUNDS:
        objectives_short = r.objectives[0][:60] + "..." if len(r.objectives[0]) > 60 else r.objectives[0]
        lines.append(f"| {r.round_number} | {r.phase.title()} | {r.title} | {objectives_short} |")

    lines.extend([
        "",
        "## Phase Descriptions",
        "",
        "### Discovery (Rounds 1-2)",
        "Broad exploration. Each analyst presents independently, then cross-examines.",
        "Output: 3 key tensions to resolve.",
        "",
        "### Enrichment (Rounds 3-5)",
        "Deep dives into each tension. New evidence required. Explicit verdicts.",
        "Output: Unified investment memo with actionable recommendation.",
    ])

    return "\n".join(lines)
