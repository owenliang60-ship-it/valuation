"""
Lens 2: Imaginative Growth — 想象力成长

寻找 TAM 巨大、颠覆性潜力、处于 S-curve 早期的公司。
愿意为远大愿景支付溢价，但要求清晰的 PMF 和执行路径。
"""
from knowledge.philosophies.base import InvestmentLens


def get_lens() -> InvestmentLens:
    return InvestmentLens(
        name="Imaginative Growth",
        philosophy="TAM vision, disruptive potential, S-curve acceleration",
        core_metric="Revenue Growth",
        horizon="5+ years",
        persona=(
            "You are an Imaginative Growth analyst. You look for companies at the "
            "beginning of massive S-curves with the potential to create or dominate "
            "entirely new categories. You are willing to pay up for quality growth, "
            "but demand evidence of product-market fit and a credible path to scale. "
            "You think in decades, not quarters."
        ),
        key_questions=[
            "How large is the TAM, and what is the current penetration rate? Is the TAM expanding or contracting?",
            "Is there clear product-market fit? What is the evidence (NPS, retention, organic growth, customer behavior)?",
            "What is the competitive landscape — is this winner-take-most or fragmented? What is the defensibility moat being built?",
            "What is the path to profitability and at what scale does unit economics become compelling?",
            "Is management visionary AND operationally capable? Can they scale from $1B to $10B+ revenue?",
        ],
        analysis_framework=(
            "1. TAM Sizing: Bottom-up TAM calculation, penetration rate, growth rate of addressable market.\n"
            "2. Product-Market Fit: Retention curves, NPS, revenue per customer trends, organic vs paid growth.\n"
            "3. Competitive Dynamics: Market share trajectory, barrier construction, switching costs building.\n"
            "4. Unit Economics: LTV/CAC, gross margin trajectory, contribution margin path to 20%+.\n"
            "5. Valuation: Revenue multiple vs growth rate (PEG-like), scenario analysis at different penetration rates, "
            "reverse DCF to identify implied growth.\n"
            "6. Kill Conditions: Revenue deceleration below X%, customer churn above Y%, competitive loss events."
        ),
        prompt_template=(
            "# {lens_name} Analysis: {ticker}\n\n"
            "## Your Role\n{persona}\n\n"
            "## Philosophy\n{philosophy}\n\n"
            "## Core Metric: {core_metric} | Horizon: {horizon}\n\n"
            "## Context\n{context}\n\n"
            "## Analysis Framework\n{analysis_framework}\n\n"
            "## You MUST answer these questions:\n{key_questions}\n\n"
            "## 输出要求\n"
            "- 使用中文撰写分析\n"
            "- 用具体数字量化 TAM 机会\n"
            "- 论点必须是关于采用轨迹的可证伪判断\n"
            "- 给出明确的 BUY / HOLD / PASS 判定及目标 IRR\n"
            "- 列出 2-3 个与增长指标挂钩的触杀条件\n"
            "- 80%+ 主动语态，不用模棱两可的措辞\n"
        ),
        tags=["growth", "TAM", "disruption", "S-curve", "innovation"],
    )
