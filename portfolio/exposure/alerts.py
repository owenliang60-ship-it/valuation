"""
Exposure alert engine — 7 rules for concentration risk detection.

Each rule returns Alert objects with severity levels:
- INFO: informational, no action required
- WARNING: approaching limit, review recommended
- CRITICAL: limit breached, immediate action required
"""
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional

from portfolio.holdings.schema import Position
from portfolio.exposure.analyzer import ExposureAnalyzer

logger = logging.getLogger(__name__)


class AlertLevel(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


@dataclass
class Alert:
    """A single exposure alert."""
    level: AlertLevel
    rule_name: str
    message: str
    positions_affected: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "level": self.level.value,
            "rule_name": self.rule_name,
            "message": self.message,
            "positions_affected": self.positions_affected,
        }


def run_all_checks(positions: List[Position]) -> List[Alert]:
    """
    Execute all 7 alert rules against current holdings.

    Rules:
    1. Single position exceeds DNA limit (CRITICAL)
    2. Single position >= 80% of DNA limit (WARNING)
    3. Sector > 40% (WARNING), > 50% (CRITICAL)
    4. Top 3 positions > 60% of portfolio (WARNING)
    5. All positions in same bucket (WARNING)
    6. Position with no kill conditions (WARNING)
    7. Position not reviewed in 30+ days (INFO)

    Returns:
        Sorted list of Alert objects (CRITICAL first).
    """
    if not positions:
        return []

    alerts = []
    analyzer = ExposureAnalyzer(positions)

    # Rule 1 & 2: Single position vs DNA limit
    alerts.extend(_check_position_limits(analyzer))

    # Rule 3: Sector concentration
    alerts.extend(_check_sector_concentration(analyzer))

    # Rule 4: Top-3 concentration
    alerts.extend(_check_top_n_concentration(analyzer))

    # Rule 5: Bucket diversification
    alerts.extend(_check_bucket_diversification(positions))

    # Rule 6: Missing kill conditions
    alerts.extend(_check_kill_conditions(positions))

    # Rule 7: Stale reviews
    alerts.extend(_check_review_dates(positions))

    # Sort: CRITICAL > WARNING > INFO
    priority = {AlertLevel.CRITICAL: 0, AlertLevel.WARNING: 1, AlertLevel.INFO: 2}
    alerts.sort(key=lambda a: priority.get(a.level, 99))

    return alerts


# ---------------------------------------------------------------------------
# Individual rule implementations
# ---------------------------------------------------------------------------

def _check_position_limits(analyzer: ExposureAnalyzer) -> List[Alert]:
    """Rules 1 & 2: position weight vs OPRMS DNA limit."""
    alerts = []
    violations = analyzer.single_position_check()
    for v in violations:
        level = AlertLevel.CRITICAL if v["severity"] == "CRITICAL" else AlertLevel.WARNING
        pct = v["current_weight"] * 100
        max_pct = v["max_weight"] * 100
        util = v["utilization"] * 100

        if level == AlertLevel.CRITICAL:
            msg = (
                f"{v['symbol']} at {pct:.1f}% exceeds DNA limit of {max_pct:.1f}% "
                f"({util:.0f}% utilization). Reduce position."
            )
        else:
            msg = (
                f"{v['symbol']} at {pct:.1f}% is approaching DNA limit of {max_pct:.1f}% "
                f"({util:.0f}% utilization). Monitor closely."
            )

        alerts.append(Alert(
            level=level,
            rule_name="position_limit",
            message=msg,
            positions_affected=[v["symbol"]],
        ))
    return alerts


def _check_sector_concentration(analyzer: ExposureAnalyzer) -> List[Alert]:
    """Rule 3: sector weight > 40% warning, > 50% critical."""
    alerts = []
    violations = analyzer.sector_concentration_check(max_sector_pct=0.40)
    for v in violations:
        level = AlertLevel.CRITICAL if v["severity"] == "CRITICAL" else AlertLevel.WARNING
        pct = v["weight"] * 100
        msg = (
            f"Sector '{v['sector']}' at {pct:.1f}% of portfolio "
            f"({'exceeds 50%' if level == AlertLevel.CRITICAL else 'exceeds 40%'}). "
            f"Positions: {', '.join(v['symbols'])}"
        )
        alerts.append(Alert(
            level=level,
            rule_name="sector_concentration",
            message=msg,
            positions_affected=v["symbols"],
        ))
    return alerts


def _check_top_n_concentration(analyzer: ExposureAnalyzer) -> List[Alert]:
    """Rule 4: top 3 positions > 60% of portfolio."""
    alerts = []
    info = analyzer.top_n_concentration(n=3)
    if info["combined_weight"] > 0.60:
        pct = info["combined_weight"] * 100
        symbols = [p["symbol"] for p in info["positions"]]
        alerts.append(Alert(
            level=AlertLevel.WARNING,
            rule_name="top_3_concentration",
            message=(
                f"Top 3 positions ({', '.join(symbols)}) account for {pct:.1f}% "
                f"of portfolio. Consider diversifying."
            ),
            positions_affected=symbols,
        ))
    return alerts


def _check_bucket_diversification(positions: List[Position]) -> List[Alert]:
    """Rule 5: all positions in the same investment bucket."""
    alerts = []
    if len(positions) < 2:
        return alerts

    buckets = set(p.investment_bucket for p in positions)
    if len(buckets) == 1:
        bucket_name = list(buckets)[0]
        alerts.append(Alert(
            level=AlertLevel.WARNING,
            rule_name="bucket_diversification",
            message=(
                f"All {len(positions)} positions are in '{bucket_name}' bucket. "
                f"Consider diversifying across investment horizons."
            ),
            positions_affected=[p.symbol for p in positions],
        ))
    return alerts


def _check_kill_conditions(positions: List[Position]) -> List[Alert]:
    """Rule 6: positions without defined kill conditions."""
    alerts = []
    for p in positions:
        if not p.kill_conditions:
            alerts.append(Alert(
                level=AlertLevel.WARNING,
                rule_name="missing_kill_conditions",
                message=(
                    f"{p.symbol} has no kill conditions defined. "
                    f"Every position must have observable invalidation triggers."
                ),
                positions_affected=[p.symbol],
            ))
    return alerts


def _check_review_dates(positions: List[Position], stale_days: int = 30) -> List[Alert]:
    """Rule 7: positions not reviewed in 30+ days."""
    alerts = []
    now = datetime.now()

    for p in positions:
        if not p.last_review_date:
            alerts.append(Alert(
                level=AlertLevel.INFO,
                rule_name="stale_review",
                message=f"{p.symbol} has never been reviewed. Schedule a review.",
                positions_affected=[p.symbol],
            ))
            continue

        try:
            last_review = datetime.strptime(p.last_review_date, "%Y-%m-%d")
            days_since = (now - last_review).days
            if days_since > stale_days:
                alerts.append(Alert(
                    level=AlertLevel.INFO,
                    rule_name="stale_review",
                    message=(
                        f"{p.symbol} last reviewed {days_since} days ago "
                        f"({p.last_review_date}). Review overdue."
                    ),
                    positions_affected=[p.symbol],
                ))
        except ValueError:
            pass  # Malformed date, skip

    return alerts
