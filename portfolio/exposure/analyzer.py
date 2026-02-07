"""
Exposure analyzer — aggregate and check portfolio concentration.

Reads holdings from portfolio/holdings/ and profiles from Data Desk.
Provides sector, industry, bucket, and geography breakdowns.
Includes OPRMS-aware position limit checks and optional correlation adjustment.
"""
import json
import logging
import math
from pathlib import Path
from typing import List, Dict, Optional

from portfolio.holdings.schema import Position, OPRMS_DNA_LIMITS

logger = logging.getLogger(__name__)

_PROJECT_ROOT = Path(__file__).parent.parent.parent


class ExposureAnalyzer:
    """Analyze portfolio exposure across multiple dimensions."""

    def __init__(self, positions: List[Position]):
        self.positions = positions
        self._profiles = self._load_profiles()

    def by_sector(self) -> Dict[str, dict]:
        """
        Aggregate exposure by GICS sector.

        Returns:
            {sector: {"count": N, "weight": 0.XX, "value": NNN, "symbols": [...]}}
        """
        return self._aggregate("sector")

    def by_industry(self) -> Dict[str, dict]:
        """Aggregate exposure by sub-industry."""
        return self._aggregate("industry")

    def by_bucket(self) -> Dict[str, dict]:
        """Aggregate exposure by investment bucket."""
        return self._aggregate("investment_bucket")

    def by_geography(self) -> Dict[str, dict]:
        """
        Aggregate exposure by company HQ country.
        Uses Data Desk profiles for country field.
        """
        result = {}
        for p in self.positions:
            profile = self._profiles.get(p.symbol, {})
            country = profile.get("country", "Unknown")
            if country not in result:
                result[country] = {"count": 0, "weight": 0.0, "value": 0.0, "symbols": []}
            result[country]["count"] += 1
            result[country]["weight"] += p.current_weight
            result[country]["value"] += p.market_value
            result[country]["symbols"].append(p.symbol)

        # Sort by weight descending
        return dict(sorted(result.items(), key=lambda x: -x[1]["weight"]))

    def single_position_check(self) -> List[dict]:
        """
        Check each position against its OPRMS DNA limit.

        Returns list of violations:
            [{"symbol": ..., "current_weight": ..., "max_weight": ...,
              "utilization": ..., "severity": "WARNING"|"CRITICAL"}]
        """
        violations = []
        for p in self.positions:
            max_w = p.max_weight
            if max_w <= 0:
                continue

            utilization = p.current_weight / max_w if max_w > 0 else 0

            if utilization >= 1.0:
                violations.append({
                    "symbol": p.symbol,
                    "current_weight": p.current_weight,
                    "max_weight": max_w,
                    "utilization": utilization,
                    "severity": "CRITICAL",
                })
            elif utilization >= 0.8:
                violations.append({
                    "symbol": p.symbol,
                    "current_weight": p.current_weight,
                    "max_weight": max_w,
                    "utilization": utilization,
                    "severity": "WARNING",
                })

        return sorted(violations, key=lambda x: -x["utilization"])

    def sector_concentration_check(self, max_sector_pct: float = 0.40) -> List[dict]:
        """
        Flag sectors exceeding concentration threshold.

        Args:
            max_sector_pct: Warning threshold as decimal (0.40 = 40%)

        Returns:
            [{"sector": ..., "weight": ..., "threshold": ..., "severity": ...}]
        """
        sector_exp = self.by_sector()
        violations = []
        for sector, info in sector_exp.items():
            weight = info["weight"]
            if weight >= max_sector_pct * 1.25:  # 50% = CRITICAL
                violations.append({
                    "sector": sector,
                    "weight": weight,
                    "threshold": max_sector_pct,
                    "severity": "CRITICAL",
                    "symbols": info["symbols"],
                })
            elif weight >= max_sector_pct:
                violations.append({
                    "sector": sector,
                    "weight": weight,
                    "threshold": max_sector_pct,
                    "severity": "WARNING",
                    "symbols": info["symbols"],
                })

        return sorted(violations, key=lambda x: -x["weight"])

    def top_n_concentration(self, n: int = 3) -> dict:
        """
        Check if top N positions are overly concentrated.

        Returns:
            {"top_n": N, "combined_weight": 0.XX, "positions": [...]}
        """
        sorted_positions = sorted(
            self.positions, key=lambda p: -p.current_weight
        )
        top = sorted_positions[:n]
        combined = sum(p.current_weight for p in top)
        return {
            "top_n": n,
            "combined_weight": combined,
            "positions": [
                {"symbol": p.symbol, "weight": p.current_weight}
                for p in top
            ],
        }

    def correlation_adjusted_exposure(
        self, correlation_matrix: Optional[Dict[str, Dict[str, float]]] = None
    ) -> Dict[str, float]:
        """
        Calculate effective exposure adjusted for correlations.

        If no correlation matrix is provided, falls back to a sector-based
        heuristic: same-sector positions assumed 0.6 correlated,
        cross-sector assumed 0.2.

        Returns:
            {"effective_positions": N.X, "diversification_ratio": 0.XX,
             "sector_detail": {...}}
        """
        if not self.positions:
            return {"effective_positions": 0, "diversification_ratio": 0}

        n = len(self.positions)
        weights = [p.current_weight for p in self.positions]

        # Build correlation matrix
        if correlation_matrix:
            corr = self._extract_corr_matrix(correlation_matrix)
        else:
            corr = self._sector_heuristic_corr()

        # Portfolio variance using correlation matrix
        # sigma_p^2 = sum_i sum_j w_i * w_j * rho_ij
        # (simplified: assume all individual volatilities = 1 for diversification ratio)
        port_variance = 0.0
        for i in range(n):
            for j in range(n):
                rho = corr[i][j] if i < len(corr) and j < len(corr[i]) else (1.0 if i == j else 0.3)
                port_variance += weights[i] * weights[j] * rho

        # HHI for comparison
        hhi = sum(w ** 2 for w in weights)

        # Effective number of positions = 1 / HHI (simple)
        # Correlation-adjusted: 1 / port_variance
        effective_positions = 1.0 / port_variance if port_variance > 0 else n
        diversification_ratio = effective_positions / n if n > 0 else 0

        return {
            "effective_positions": round(effective_positions, 2),
            "actual_positions": n,
            "diversification_ratio": round(diversification_ratio, 4),
            "hhi": round(hhi, 6),
            "portfolio_variance_proxy": round(port_variance, 6),
        }

    # -----------------------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------------------

    def _aggregate(self, field: str) -> Dict[str, dict]:
        """Generic aggregation by a Position field."""
        result = {}
        for p in self.positions:
            key = getattr(p, field, "Unknown") or "Unknown"
            if key not in result:
                result[key] = {"count": 0, "weight": 0.0, "value": 0.0, "symbols": []}
            result[key]["count"] += 1
            result[key]["weight"] += p.current_weight
            result[key]["value"] += p.market_value
            result[key]["symbols"].append(p.symbol)

        return dict(sorted(result.items(), key=lambda x: -x[1]["weight"]))

    def _load_profiles(self) -> dict:
        """Load profiles from Data Desk."""
        profiles_path = _PROJECT_ROOT / "data" / "fundamental" / "profiles.json"
        if not profiles_path.exists():
            return {}
        try:
            with open(profiles_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load profiles: {e}")
            return {}

    def _sector_heuristic_corr(self) -> List[List[float]]:
        """
        Build a heuristic correlation matrix based on sectors.
        Same sector = 0.6, different sector = 0.2, self = 1.0
        """
        n = len(self.positions)
        sectors = [p.sector for p in self.positions]
        corr = []
        for i in range(n):
            row = []
            for j in range(n):
                if i == j:
                    row.append(1.0)
                elif sectors[i] == sectors[j]:
                    row.append(0.6)
                else:
                    row.append(0.2)
            corr.append(row)
        return corr

    def _extract_corr_matrix(
        self, correlation_matrix: Dict[str, Dict[str, float]]
    ) -> List[List[float]]:
        """Extract correlation values for current positions from a symbol-keyed matrix."""
        n = len(self.positions)
        symbols = [p.symbol for p in self.positions]
        corr = []
        for i in range(n):
            row = []
            for j in range(n):
                if i == j:
                    row.append(1.0)
                else:
                    val = (
                        correlation_matrix
                        .get(symbols[i], {})
                        .get(symbols[j], 0.3)
                    )
                    row.append(val)
            corr.append(row)
        return corr
