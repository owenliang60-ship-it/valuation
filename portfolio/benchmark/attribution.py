"""
Alpha attribution — Brinson-style decomposition of portfolio returns.

Decomposes active return into:
- Stock selection effect: value from picking different stocks than benchmark
- Timing effect: value from entry/exit timing decisions
- Sizing effect: value from over/under-weighting positions vs OPRMS targets
"""
import logging
from typing import Dict, List, Optional

import pandas as pd
import numpy as np

from portfolio.holdings.schema import Position
from portfolio.holdings.history import get_position_history

logger = logging.getLogger(__name__)


class AttributionEngine:
    """Brinson-style alpha attribution analysis."""

    def __init__(self, positions: List[Position]):
        self.positions = positions

    def stock_selection_effect(
        self,
        position_returns: Dict[str, float],
        benchmark_return: float,
    ) -> Dict[str, float]:
        """
        Measure value added from stock selection.

        For each position, compares its return against the benchmark return,
        weighted by the position's weight.

        Args:
            position_returns: {symbol: period_return} for each position
            benchmark_return: benchmark period return

        Returns:
            {"total": float, "by_position": {symbol: contribution}}
        """
        by_position = {}
        total = 0.0

        for p in self.positions:
            if p.symbol in position_returns:
                stock_ret = position_returns[p.symbol]
                # Selection effect = weight * (stock return - benchmark return)
                effect = p.current_weight * (stock_ret - benchmark_return)
                by_position[p.symbol] = round(effect, 6)
                total += effect

        return {
            "total": round(total, 6),
            "by_position": dict(sorted(by_position.items(), key=lambda x: -abs(x[1]))),
        }

    def sizing_effect(
        self,
        position_returns: Dict[str, float],
        benchmark_return: float,
    ) -> Dict[str, float]:
        """
        Measure value added/lost from over/under-weighting vs OPRMS targets.

        Compares actual weight to target weight for each position.

        Args:
            position_returns: {symbol: period_return}
            benchmark_return: benchmark period return

        Returns:
            {"total": float, "by_position": {symbol: {"effect": ..., "drift": ...}}}
        """
        by_position = {}
        total = 0.0

        for p in self.positions:
            if p.symbol in position_returns:
                stock_ret = position_returns[p.symbol]
                # Sizing effect = (actual_weight - target_weight) * (stock_return - benchmark_return)
                weight_diff = p.current_weight - p.target_weight
                effect = weight_diff * (stock_ret - benchmark_return)
                by_position[p.symbol] = {
                    "effect": round(effect, 6),
                    "actual_weight": p.current_weight,
                    "target_weight": p.target_weight,
                    "drift": round(weight_diff, 6),
                }
                total += effect

        return {
            "total": round(total, 6),
            "by_position": dict(sorted(
                by_position.items(), key=lambda x: -abs(x[1]["effect"])
            )),
        }

    def timing_effect_from_history(
        self,
        price_data: Dict[str, pd.DataFrame],
        start_date: str,
        end_date: str,
    ) -> Dict[str, float]:
        """
        Estimate timing effect from position history.

        Compares actual entry prices against average prices over the period.
        Positive = entered at below-average price (good timing).

        Args:
            price_data: {symbol: DataFrame with date/close columns}
            start_date: period start (YYYY-MM-DD)
            end_date: period end (YYYY-MM-DD)

        Returns:
            {"total": float, "by_position": {symbol: {"effect": ..., "avg_price": ..., "entry_price": ...}}}
        """
        by_position = {}
        total = 0.0

        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)

        for p in self.positions:
            if p.symbol not in price_data or p.cost_basis <= 0:
                continue

            df = price_data[p.symbol]
            df = df[(df["date"] >= start) & (df["date"] <= end)]

            if df.empty:
                continue

            avg_price = df["close"].mean()
            if avg_price <= 0:
                continue

            # Timing effect = (avg_price - entry_price) / avg_price * weight
            timing = (avg_price - p.cost_basis) / avg_price * p.current_weight
            by_position[p.symbol] = {
                "effect": round(timing, 6),
                "avg_price": round(avg_price, 2),
                "entry_price": p.cost_basis,
            }
            total += timing

        return {
            "total": round(total, 6),
            "by_position": dict(sorted(
                by_position.items(), key=lambda x: -abs(x[1]["effect"])
            )),
        }

    def decompose_alpha(
        self,
        position_returns: Dict[str, float],
        benchmark_return: float,
        price_data: Optional[Dict[str, pd.DataFrame]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> dict:
        """
        Full alpha attribution breakdown.

        Returns:
            {
                "total_active_return": float,
                "stock_selection": {...},
                "sizing": {...},
                "timing": {...},  (only if price_data provided)
                "residual": float,
            }
        """
        # Total active return
        portfolio_return = sum(
            p.current_weight * position_returns.get(p.symbol, 0)
            for p in self.positions
        )
        active_return = portfolio_return - benchmark_return

        # Stock selection
        selection = self.stock_selection_effect(position_returns, benchmark_return)

        # Sizing
        sizing = self.sizing_effect(position_returns, benchmark_return)

        result = {
            "total_active_return": round(active_return, 6),
            "portfolio_return": round(portfolio_return, 6),
            "benchmark_return": round(benchmark_return, 6),
            "stock_selection": selection,
            "sizing": sizing,
        }

        # Timing (optional, needs price data)
        if price_data and start_date and end_date:
            timing = self.timing_effect_from_history(price_data, start_date, end_date)
            result["timing"] = timing
            # Residual = active - selection - sizing - timing
            result["residual"] = round(
                active_return - selection["total"] - sizing["total"] - timing["total"],
                6,
            )
        else:
            result["timing"] = {"total": 0, "note": "Price data not provided for timing analysis"}
            result["residual"] = round(
                active_return - selection["total"] - sizing["total"],
                6,
            )

        return result
