"""
Periodic review framework — weekly, monthly, quarterly portfolio reviews.

Generates markdown reports at different cadences:
- Weekly: quick snapshot (value, P&L, top movers, weight drift)
- Monthly: deeper analysis (benchmark comparison, sector attribution, kill conditions)
- Quarterly: comprehensive (full attribution, OPRMS review, rebalance recommendations)
"""
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional

from portfolio.holdings.schema import Position, OPRMS_DNA_LIMITS
from portfolio.holdings.manager import (
    load_holdings,
    refresh_prices,
    get_portfolio_value,
    calculate_target_weight,
)
from portfolio.exposure.analyzer import ExposureAnalyzer
from portfolio.exposure.alerts import run_all_checks

logger = logging.getLogger(__name__)


class ReviewCadence(str, Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


# Review intervals in days
_CADENCE_DAYS = {
    ReviewCadence.WEEKLY: 7,
    ReviewCadence.MONTHLY: 30,
    ReviewCadence.QUARTERLY: 90,
}


def get_next_review_date(cadence: ReviewCadence, last_review: str) -> str:
    """
    Calculate the next review date.

    Args:
        cadence: Review frequency
        last_review: Last review date as YYYY-MM-DD

    Returns:
        Next review date as YYYY-MM-DD
    """
    try:
        last = datetime.strptime(last_review, "%Y-%m-%d")
    except ValueError:
        last = datetime.now()

    days = _CADENCE_DAYS[cadence]
    next_date = last + timedelta(days=days)
    return next_date.strftime("%Y-%m-%d")


def check_rebalance_needed(
    positions: Optional[List[Position]] = None,
    drift_threshold: float = 0.03,
) -> List[dict]:
    """
    Flag positions with weight drift exceeding threshold.

    Args:
        positions: Portfolio positions (loads from file if None)
        drift_threshold: Absolute weight drift to flag (default 3%)

    Returns:
        List of positions needing rebalance with drift details.
    """
    if positions is None:
        positions = refresh_prices(load_holdings())

    needs_rebalance = []
    for p in positions:
        drift = p.current_weight - p.target_weight
        if abs(drift) > drift_threshold:
            needs_rebalance.append({
                "symbol": p.symbol,
                "current_weight": p.current_weight,
                "target_weight": p.target_weight,
                "drift": drift,
                "direction": "overweight" if drift > 0 else "underweight",
                "shares_to_adjust": _estimate_shares_adjustment(p, drift),
            })

    return sorted(needs_rebalance, key=lambda x: -abs(x["drift"]))


def generate_weekly_snapshot(positions: Optional[List[Position]] = None) -> str:
    """
    Weekly snapshot — quick status.

    Includes: portfolio value, position count, top movers, weight drift.
    """
    if positions is None:
        positions = refresh_prices(load_holdings())

    if not positions:
        return "# Weekly Snapshot\n\nNo positions in portfolio."

    today = datetime.now().strftime("%Y-%m-%d")
    total_value = sum(p.market_value for p in positions)
    total_cost = sum(p.shares * p.cost_basis for p in positions)
    total_pnl = total_value - total_cost
    total_pnl_pct = total_pnl / total_cost if total_cost > 0 else 0

    lines = []
    lines.append(f"# Weekly Snapshot ({today})")
    lines.append("")
    lines.append(f"**Portfolio Value**: ${total_value:,.0f}")
    lines.append(f"**Total P&L**: ${total_pnl:,.0f} ({total_pnl_pct*100:+.1f}%)")
    lines.append(f"**Positions**: {len(positions)}")
    lines.append("")

    # Top positions by weight
    lines.append("## Current Positions")
    lines.append("")
    lines.append("| Symbol | Weight | Target | Drift | P&L % | Bucket |")
    lines.append("|--------|-------:|-------:|------:|------:|--------|")
    for p in sorted(positions, key=lambda p: -p.current_weight):
        drift = p.current_weight - p.target_weight
        drift_str = f"{drift*100:+.1f}%"
        pnl_pct = p.unrealized_pnl_pct * 100
        lines.append(
            f"| {p.symbol} | {p.current_weight*100:.1f}% | "
            f"{p.target_weight*100:.1f}% | {drift_str} | "
            f"{pnl_pct:+.1f}% | {p.investment_bucket} |"
        )
    lines.append("")

    # Weight drift alerts
    rebalance = check_rebalance_needed(positions)
    if rebalance:
        lines.append("## Rebalance Needed")
        lines.append("")
        for r in rebalance:
            lines.append(
                f"- **{r['symbol']}**: {r['direction']} by "
                f"{abs(r['drift'])*100:.1f}% "
                f"(current {r['current_weight']*100:.1f}% vs "
                f"target {r['target_weight']*100:.1f}%)"
            )
        lines.append("")

    return "\n".join(lines)


def generate_monthly_review(
    positions: Optional[List[Position]] = None,
) -> str:
    """
    Monthly review — deeper analysis.

    Includes: weekly snapshot content + sector attribution, alerts, kill condition check.
    """
    if positions is None:
        positions = refresh_prices(load_holdings())

    if not positions:
        return "# Monthly Review\n\nNo positions in portfolio."

    today = datetime.now().strftime("%Y-%m-%d")
    total_value = sum(p.market_value for p in positions)

    lines = []
    lines.append(f"# Monthly Review ({today})")
    lines.append("")
    lines.append(f"**Portfolio Value**: ${total_value:,.0f}")
    lines.append(f"**Positions**: {len(positions)}")
    lines.append("")

    # Sector exposure
    analyzer = ExposureAnalyzer(positions)
    lines.append("## Sector Exposure")
    lines.append("")
    lines.append("| Sector | Count | Weight | Value |")
    lines.append("|--------|------:|-------:|------:|")
    for sector, info in analyzer.by_sector().items():
        lines.append(
            f"| {sector} | {info['count']} | "
            f"{info['weight']*100:.1f}% | ${info['value']:,.0f} |"
        )
    lines.append("")

    # Bucket allocation
    lines.append("## Bucket Allocation")
    lines.append("")
    lines.append("| Bucket | Count | Weight |")
    lines.append("|--------|------:|-------:|")
    for bucket, info in analyzer.by_bucket().items():
        lines.append(
            f"| {bucket} | {info['count']} | {info['weight']*100:.1f}% |"
        )
    lines.append("")

    # Alerts
    alerts = run_all_checks(positions)
    if alerts:
        lines.append("## Risk Alerts")
        lines.append("")
        for a in alerts:
            prefix = f"**{a.level.value}**" if a.level.value != "INFO" else a.level.value
            lines.append(f"- [{prefix}] {a.message}")
        lines.append("")

    # Kill conditions status
    lines.append("## Kill Conditions Status")
    lines.append("")
    for p in positions:
        if p.kill_conditions:
            lines.append(f"### {p.symbol} (DNA: {p.dna_rating})")
            for kc in p.kill_conditions:
                lines.append(f"- [ ] {kc}")
            lines.append("")
        else:
            lines.append(f"### {p.symbol} -- MISSING KILL CONDITIONS")
            lines.append("")

    # Rebalance recommendations
    rebalance = check_rebalance_needed(positions)
    if rebalance:
        lines.append("## Rebalance Recommendations")
        lines.append("")
        for r in rebalance:
            action = "Trim" if r["direction"] == "overweight" else "Add to"
            lines.append(
                f"- {action} **{r['symbol']}**: "
                f"{r['direction']} by {abs(r['drift'])*100:.1f}%"
            )
        lines.append("")

    return "\n".join(lines)


def generate_quarterly_review(
    positions: Optional[List[Position]] = None,
) -> str:
    """
    Quarterly review — comprehensive.

    Includes: monthly content + OPRMS rating review, full position audit,
    rebalance plan, forward-looking assessment.
    """
    if positions is None:
        positions = refresh_prices(load_holdings())

    if not positions:
        return "# Quarterly Review\n\nNo positions in portfolio."

    today = datetime.now().strftime("%Y-%m-%d")
    total_value = sum(p.market_value for p in positions)
    total_cost = sum(p.shares * p.cost_basis for p in positions)

    lines = []
    lines.append(f"# Quarterly Review ({today})")
    lines.append("")
    lines.append(f"**Portfolio Value**: ${total_value:,.0f}")
    lines.append(f"**Total Cost Basis**: ${total_cost:,.0f}")
    lines.append(f"**Total P&L**: ${total_value - total_cost:,.0f}")
    lines.append(f"**Positions**: {len(positions)}")
    lines.append("")

    # OPRMS Rating Review
    lines.append("## OPRMS Rating Review")
    lines.append("")
    lines.append("Review each position's DNA and Timing ratings. Are they still accurate?")
    lines.append("")
    lines.append("| Symbol | DNA | Timing | Target Wt | Current Wt | Max Wt | Action Needed? |")
    lines.append("|--------|-----|--------|----------:|----------:|-------:|----------------|")
    for p in sorted(positions, key=lambda p: -p.current_weight):
        target = calculate_target_weight(p.dna_rating, p.timing_rating)
        action = ""
        drift = abs(p.current_weight - target)
        if drift > 0.03:
            action = "Rebalance"
        lines.append(
            f"| {p.symbol} | {p.dna_rating} | {p.timing_rating} | "
            f"{target*100:.1f}% | {p.current_weight*100:.1f}% | "
            f"{p.max_weight*100:.0f}% | {action} |"
        )
    lines.append("")

    # Full position audit
    lines.append("## Full Position Audit")
    lines.append("")
    for p in sorted(positions, key=lambda p: -p.market_value):
        lines.append(f"### {p.symbol} — {p.company_name}")
        lines.append("")
        lines.append(f"- **Bucket**: {p.investment_bucket}")
        lines.append(f"- **DNA**: {p.dna_rating} | **Timing**: {p.timing_rating}")
        lines.append(f"- **Entry**: ${p.cost_basis:.2f} on {p.entry_date}")
        lines.append(f"- **Current**: ${p.current_price:.2f} ({p.unrealized_pnl_pct*100:+.1f}%)")
        lines.append(f"- **Weight**: {p.current_weight*100:.1f}% (target: {p.target_weight*100:.1f}%)")
        lines.append(f"- **Memo**: {p.memo_id or 'None'}")
        lines.append(f"- **Last Review**: {p.last_review_date or 'Never'}")

        if p.kill_conditions:
            lines.append("- **Kill Conditions**:")
            for kc in p.kill_conditions:
                lines.append(f"  - [ ] {kc}")
        else:
            lines.append("- **Kill Conditions**: NONE DEFINED")

        lines.append(f"- **Notes**: {p.notes or 'None'}")
        lines.append("")
        lines.append("**Quarterly Question**: Should this position be maintained, added to, trimmed, or closed?")
        lines.append("")

    # Diversification
    analyzer = ExposureAnalyzer(positions)
    corr_info = analyzer.correlation_adjusted_exposure()
    lines.append("## Diversification Assessment")
    lines.append("")
    lines.append(f"- Actual positions: {corr_info['actual_positions']}")
    lines.append(f"- Effective positions (correlation-adjusted): {corr_info['effective_positions']}")
    lines.append(f"- Diversification ratio: {corr_info['diversification_ratio']*100:.1f}%")
    lines.append(f"- HHI: {corr_info['hhi']:.4f}")
    lines.append("")

    # Alerts
    alerts = run_all_checks(positions)
    if alerts:
        lines.append("## Outstanding Alerts")
        lines.append("")
        for a in alerts:
            lines.append(f"- **[{a.level.value}]** [{a.rule_name}] {a.message}")
        lines.append("")

    # Action items template
    lines.append("## Action Items")
    lines.append("")
    lines.append("- [ ] Review and update all OPRMS ratings")
    lines.append("- [ ] Verify all kill conditions are still relevant")
    lines.append("- [ ] Execute rebalance trades if needed")
    lines.append("- [ ] Update investment memos for material changes")
    lines.append("- [ ] Assess bucket allocation vs market regime")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _estimate_shares_adjustment(position: Position, weight_drift: float) -> str:
    """Estimate shares to buy/sell to correct drift."""
    if position.current_price <= 0:
        return "N/A (no price)"

    # Rough estimate: drift * total_value / price
    # Since we don't know total portfolio value here, express in relative terms
    if weight_drift > 0:
        return f"Sell ~{abs(weight_drift)*100:.1f}% of portfolio value"
    else:
        return f"Buy ~{abs(weight_drift)*100:.1f}% of portfolio value"
