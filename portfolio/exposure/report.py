"""
Exposure report generator — markdown-formatted portfolio exposure summaries.
"""
from typing import List, Optional

from portfolio.holdings.schema import Position
from portfolio.exposure.analyzer import ExposureAnalyzer
from portfolio.exposure.alerts import run_all_checks, Alert


def generate_exposure_summary(positions: List[Position]) -> str:
    """
    Generate a markdown exposure summary.

    Includes: sector breakdown, top positions, bucket allocation, geography.
    """
    if not positions:
        return "# Portfolio Exposure Summary\n\nNo positions in portfolio."

    analyzer = ExposureAnalyzer(positions)
    total_value = sum(p.market_value for p in positions)

    lines = []
    lines.append("# Portfolio Exposure Summary")
    lines.append("")
    lines.append(f"**Positions**: {len(positions)} | **Total Value**: ${total_value:,.0f}")
    lines.append("")

    # Sector breakdown
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

    # Top positions
    lines.append("## Top Positions by Weight")
    lines.append("")
    lines.append("| Symbol | DNA | Weight | Max | Utilization | Bucket |")
    lines.append("|--------|-----|-------:|----:|------------:|--------|")
    sorted_pos = sorted(positions, key=lambda p: -p.current_weight)
    for p in sorted_pos[:10]:
        util = (p.current_weight / p.max_weight * 100) if p.max_weight > 0 else 0
        lines.append(
            f"| {p.symbol} | {p.dna_rating} | "
            f"{p.current_weight*100:.1f}% | {p.max_weight*100:.0f}% | "
            f"{util:.0f}% | {p.investment_bucket} |"
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

    # Geography
    geo = analyzer.by_geography()
    if len(geo) > 1:
        lines.append("## Geographic Exposure")
        lines.append("")
        lines.append("| Country | Count | Weight |")
        lines.append("|---------|------:|-------:|")
        for country, info in geo.items():
            lines.append(
                f"| {country} | {info['count']} | {info['weight']*100:.1f}% |"
            )
        lines.append("")

    # Diversification
    corr_info = analyzer.correlation_adjusted_exposure()
    lines.append("## Diversification")
    lines.append("")
    lines.append(
        f"- **Actual positions**: {corr_info['actual_positions']}"
    )
    lines.append(
        f"- **Effective positions** (correlation-adjusted): "
        f"{corr_info['effective_positions']}"
    )
    lines.append(
        f"- **Diversification ratio**: "
        f"{corr_info['diversification_ratio']*100:.1f}%"
    )
    lines.append(
        f"- **HHI**: {corr_info['hhi']:.4f}"
    )
    lines.append("")

    return "\n".join(lines)


def generate_concentration_report(positions: List[Position]) -> str:
    """
    Generate a detailed concentration analysis with alerts.
    """
    if not positions:
        return "# Concentration Report\n\nNo positions in portfolio."

    analyzer = ExposureAnalyzer(positions)
    alerts = run_all_checks(positions)

    lines = []
    lines.append("# Concentration Report")
    lines.append("")

    # Alert summary
    critical = [a for a in alerts if a.level.value == "CRITICAL"]
    warnings = [a for a in alerts if a.level.value == "WARNING"]
    infos = [a for a in alerts if a.level.value == "INFO"]

    lines.append("## Alert Summary")
    lines.append("")
    lines.append(
        f"**CRITICAL**: {len(critical)} | "
        f"**WARNING**: {len(warnings)} | "
        f"**INFO**: {len(infos)}"
    )
    lines.append("")

    if critical:
        lines.append("### CRITICAL Alerts")
        lines.append("")
        for a in critical:
            lines.append(f"- **[{a.rule_name}]** {a.message}")
        lines.append("")

    if warnings:
        lines.append("### Warnings")
        lines.append("")
        for a in warnings:
            lines.append(f"- **[{a.rule_name}]** {a.message}")
        lines.append("")

    if infos:
        lines.append("### Informational")
        lines.append("")
        for a in infos:
            lines.append(f"- [{a.rule_name}] {a.message}")
        lines.append("")

    # Position limit utilization
    lines.append("## Position Limit Utilization (OPRMS DNA)")
    lines.append("")
    lines.append("| Symbol | DNA | Weight | Max | Utilization | Status |")
    lines.append("|--------|-----|-------:|----:|------------:|--------|")
    for p in sorted(positions, key=lambda p: -p.current_weight):
        max_w = p.max_weight
        util = (p.current_weight / max_w) if max_w > 0 else 0
        if util >= 1.0:
            status = "OVER LIMIT"
        elif util >= 0.8:
            status = "Near limit"
        else:
            status = "OK"
        lines.append(
            f"| {p.symbol} | {p.dna_rating} | "
            f"{p.current_weight*100:.1f}% | {p.max_weight*100:.0f}% | "
            f"{util*100:.0f}% | {status} |"
        )
    lines.append("")

    # Top-3 concentration
    top3 = analyzer.top_n_concentration(3)
    lines.append("## Top-3 Concentration")
    lines.append("")
    lines.append(
        f"Combined weight: **{top3['combined_weight']*100:.1f}%** "
        f"({'OK' if top3['combined_weight'] <= 0.60 else 'HIGH'})"
    )
    lines.append("")
    for p in top3["positions"]:
        lines.append(f"- {p['symbol']}: {p['weight']*100:.1f}%")
    lines.append("")

    # Kill conditions audit
    lines.append("## Kill Conditions Audit")
    lines.append("")
    for p in positions:
        if p.kill_conditions:
            lines.append(f"### {p.symbol}")
            for kc in p.kill_conditions:
                lines.append(f"- {kc}")
            lines.append("")
        else:
            lines.append(f"### {p.symbol} -- **NO KILL CONDITIONS DEFINED**")
            lines.append("")

    return "\n".join(lines)
