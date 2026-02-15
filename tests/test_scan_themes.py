"""Tests for scripts/scan_themes.py — signal merge, theme matching, report formatting.

Tests:
1. has_momentum_signal: RS Rating B trigger
2. has_momentum_signal: RS Rating C trigger
3. has_momentum_signal: DV acceleration trigger
4. has_momentum_signal: RVOL sustained trigger
5. has_momentum_signal: PMARP breakout trigger
6. has_momentum_signal: no signal
7. merge_signals: converged, momentum_only, narrative_only
8. merge_signals: empty attention
9. merge_signals: empty momentum
10. match_themes: matches tickers to themes
11. match_themes: no overlap
12. format_theme_report: produces valid report
13. get_latest_week_start: returns monday
14. fetch_attention_ranking: reads from store
"""
import json
import pytest
from datetime import datetime, timedelta
from pathlib import Path
from unittest import mock

import pandas as pd

# Patch sys.path before importing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.scan_themes import (
    has_momentum_signal,
    merge_signals,
    match_themes,
    format_theme_report,
    get_latest_week_start,
    fetch_attention_ranking,
    _find_attention_score,
)


# ---------------------------------------------------------------------------
# Helpers — mock momentum results
# ---------------------------------------------------------------------------

def _make_rs_df(data):
    """Create a mock RS Rating DataFrame."""
    return pd.DataFrame(data)


def _make_dv_df(data):
    """Create a mock DV acceleration DataFrame."""
    return pd.DataFrame(data)


EMPTY_MOMENTUM = {
    "rs_rating_b": pd.DataFrame(columns=["symbol", "rs_rank"]),
    "rs_rating_c": pd.DataFrame(columns=["symbol", "rs_rank"]),
    "dv_acceleration": pd.DataFrame(columns=["symbol", "signal"]),
    "rvol_sustained": [],
    "symbols_scanned": 0,
    "price_dict_size": 0,
}

EMPTY_INDICATOR_SUMMARY = {
    "total": 0,
    "with_signals": 0,
    "errors": 0,
    "signals": {},
    "top_pmarp": [],
    "top_rvol": [],
    "low_pmarp": [],
    "pmarp_crossovers": {
        "breakout_98": [],
        "fading_98": [],
        "crashed_2": [],
        "recovery_2": [],
    },
}


# ---------------------------------------------------------------------------
# Tests: has_momentum_signal
# ---------------------------------------------------------------------------

class TestHasMomentumSignal:
    """Tests for has_momentum_signal()."""

    def test_rs_rating_b_trigger(self):
        """RS Rating B >= threshold triggers."""
        momentum = dict(EMPTY_MOMENTUM)
        momentum["rs_rating_b"] = _make_rs_df([
            {"symbol": "NVDA", "rs_rank": 95},
            {"symbol": "AAPL", "rs_rank": 50},
        ])
        assert has_momentum_signal("NVDA", momentum, EMPTY_INDICATOR_SUMMARY) is True
        assert has_momentum_signal("AAPL", momentum, EMPTY_INDICATOR_SUMMARY) is False

    def test_rs_rating_c_trigger(self):
        """RS Rating C >= threshold triggers."""
        momentum = dict(EMPTY_MOMENTUM)
        momentum["rs_rating_c"] = _make_rs_df([
            {"symbol": "TSLA", "rs_rank": 85},
        ])
        assert has_momentum_signal("TSLA", momentum, EMPTY_INDICATOR_SUMMARY) is True

    def test_dv_acceleration_trigger(self):
        """DV acceleration signal=True triggers."""
        momentum = dict(EMPTY_MOMENTUM)
        momentum["dv_acceleration"] = _make_dv_df([
            {"symbol": "AMD", "signal": True, "ratio": 2.0},
            {"symbol": "INTC", "signal": False, "ratio": 1.0},
        ])
        assert has_momentum_signal("AMD", momentum, EMPTY_INDICATOR_SUMMARY) is True
        assert has_momentum_signal("INTC", momentum, EMPTY_INDICATOR_SUMMARY) is False

    def test_rvol_sustained_trigger(self):
        """RVOL sustained entry triggers."""
        momentum = dict(EMPTY_MOMENTUM)
        momentum["rvol_sustained"] = [
            {"symbol": "META", "level": "sustained_3d", "values": [3.0, 2.5, 2.1]},
        ]
        assert has_momentum_signal("META", momentum, EMPTY_INDICATOR_SUMMARY) is True
        assert has_momentum_signal("GOOG", momentum, EMPTY_INDICATOR_SUMMARY) is False

    def test_pmarp_breakout_trigger(self):
        """PMARP breakout_98 triggers."""
        summary = dict(EMPTY_INDICATOR_SUMMARY)
        summary["pmarp_crossovers"] = {
            "breakout_98": [{"symbol": "AVGO", "value": 99.0}],
            "fading_98": [],
            "crashed_2": [],
            "recovery_2": [],
        }
        assert has_momentum_signal("AVGO", EMPTY_MOMENTUM, summary) is True

    def test_pmarp_recovery_trigger(self):
        """PMARP recovery_2 triggers."""
        summary = dict(EMPTY_INDICATOR_SUMMARY)
        summary["pmarp_crossovers"] = {
            "breakout_98": [],
            "fading_98": [],
            "crashed_2": [],
            "recovery_2": [{"symbol": "BA", "value": 3.0}],
        }
        assert has_momentum_signal("BA", EMPTY_MOMENTUM, summary) is True

    def test_no_signal(self):
        """No signal for unlisted ticker."""
        assert has_momentum_signal("ZZZZZ", EMPTY_MOMENTUM, EMPTY_INDICATOR_SUMMARY) is False

    def test_custom_threshold(self):
        """Custom RS threshold works."""
        momentum = dict(EMPTY_MOMENTUM)
        momentum["rs_rating_b"] = _make_rs_df([
            {"symbol": "NVDA", "rs_rank": 70},
        ])
        # Default threshold 80 — should NOT trigger
        assert has_momentum_signal("NVDA", momentum, EMPTY_INDICATOR_SUMMARY, rs_threshold=80) is False
        # Lowered threshold 60 — should trigger
        assert has_momentum_signal("NVDA", momentum, EMPTY_INDICATOR_SUMMARY, rs_threshold=60) is True


# ---------------------------------------------------------------------------
# Tests: merge_signals
# ---------------------------------------------------------------------------

class TestMergeSignals:
    """Tests for merge_signals()."""

    def test_full_merge(self):
        """Converged, momentum_only, narrative_only all populated correctly."""
        attention = [
            {"ticker": "NVDA", "composite_score": 3.0},
            {"ticker": "IONQ", "composite_score": 2.0},
        ]
        momentum = dict(EMPTY_MOMENTUM)
        momentum["rs_rating_b"] = _make_rs_df([
            {"symbol": "NVDA", "rs_rank": 95},
            {"symbol": "TSLA", "rs_rank": 85},
        ])
        symbols = ["NVDA", "TSLA", "AAPL", "IONQ"]

        result = merge_signals(attention, momentum, EMPTY_INDICATOR_SUMMARY, symbols)

        assert "NVDA" in result["converged"]       # in both
        assert "TSLA" in result["momentum_only"]    # momentum only
        assert "IONQ" in result["narrative_only"]   # attention only
        assert "AAPL" not in result["converged"]
        assert "AAPL" not in result["momentum_only"]

    def test_empty_attention(self):
        """No attention data -> no converged, no narrative_only."""
        momentum = dict(EMPTY_MOMENTUM)
        momentum["rs_rating_b"] = _make_rs_df([
            {"symbol": "NVDA", "rs_rank": 90},
        ])
        result = merge_signals([], momentum, EMPTY_INDICATOR_SUMMARY, ["NVDA"])

        assert result["converged"] == []
        assert result["momentum_only"] == ["NVDA"]
        assert result["narrative_only"] == []

    def test_empty_momentum(self):
        """No momentum signals -> all attention goes to narrative_only."""
        attention = [{"ticker": "IONQ", "composite_score": 2.0}]
        result = merge_signals(attention, EMPTY_MOMENTUM, EMPTY_INDICATOR_SUMMARY, ["AAPL"])

        assert result["converged"] == []
        assert result["momentum_only"] == []
        assert result["narrative_only"] == ["IONQ"]

    def test_both_empty(self):
        """Both engines empty -> all categories empty."""
        result = merge_signals([], EMPTY_MOMENTUM, EMPTY_INDICATOR_SUMMARY, [])
        assert result["converged"] == []
        assert result["momentum_only"] == []
        assert result["narrative_only"] == []


# ---------------------------------------------------------------------------
# Tests: match_themes
# ---------------------------------------------------------------------------

class TestMatchThemes:
    """Tests for match_themes()."""

    def test_matches_tickers_to_themes(self):
        """Tickers are matched to correct themes."""
        seed = {
            "ai_chip": {"keywords": ["GPU"], "tickers": ["NVDA", "AMD"]},
            "memory": {"keywords": ["DRAM"], "tickers": ["MU"]},
            "fintech": {"keywords": ["payments"], "tickers": ["V", "MA"]},
        }
        result = match_themes(["NVDA", "MU", "AAPL"], seed=seed)

        assert "ai_chip" in result
        assert result["ai_chip"] == ["NVDA"]
        assert "memory" in result
        assert result["memory"] == ["MU"]
        assert "fintech" not in result  # no overlap

    def test_no_overlap(self):
        """No tickers match any theme."""
        seed = {
            "ai_chip": {"keywords": ["GPU"], "tickers": ["NVDA"]},
        }
        result = match_themes(["AAPL", "GOOG"], seed=seed)
        assert result == {}

    def test_empty_input(self):
        """Empty ticker list returns empty themes."""
        result = match_themes([])
        assert result == {}

    def test_uses_default_seed(self):
        """Uses THEME_KEYWORDS_SEED by default."""
        result = match_themes(["NVDA", "AMD"])
        # Should find at least ai_chip
        assert "ai_chip" in result
        assert "NVDA" in result["ai_chip"]


# ---------------------------------------------------------------------------
# Tests: format_theme_report
# ---------------------------------------------------------------------------

class TestFormatThemeReport:
    """Tests for format_theme_report()."""

    def test_produces_valid_report(self):
        """Report contains all 7 sections."""
        report = format_theme_report(
            expand_result={"added": [{"symbol": "IONQ"}], "failed": [], "dry_run": False},
            merged={"converged": ["NVDA"], "momentum_only": ["TSLA"], "narrative_only": ["IONQ"]},
            theme_map={"ai_chip": ["NVDA"]},
            cluster_result={"clusters": {"0": ["NVDA", "AMD"]}},
            attention_ranking=[{"ticker": "NVDA", "composite_score": 3.0}],
            pool_stats={"total": 50, "screener": 45, "analysis": 3, "attention": 2},
            elapsed=42.0,
        )

        assert "A. 池子扩展" in report
        assert "B. 主线共振" in report
        assert "C. 动量先行" in report
        assert "D. 叙事先行" in report
        assert "E. 主题热力图" in report
        assert "F. 聚类周报" in report
        assert "G. 建议深度分析" in report
        assert "IONQ" in report
        assert "NVDA" in report
        assert "42s" in report

    def test_empty_report(self):
        """Report works with empty data."""
        report = format_theme_report(
            expand_result={},
            merged={"converged": [], "momentum_only": [], "narrative_only": []},
            theme_map={},
            cluster_result={},
            attention_ranking=[],
            pool_stats={"total": 0, "screener": 0, "analysis": 0, "attention": 0},
            elapsed=1.0,
        )
        assert "无共振信号" in report
        assert "无主题信号" in report

    def test_no_expand_report(self):
        """Report shows skip message when expand is None."""
        report = format_theme_report(
            expand_result={},
            merged={"converged": [], "momentum_only": [], "narrative_only": []},
            theme_map={},
            cluster_result={},
            attention_ranking=[],
            pool_stats={"total": 50, "screener": 50, "analysis": 0, "attention": 0},
            elapsed=1.0,
        )
        # Empty expand_result → "跳过池扩展"
        # (since there are no "added" keys in empty dict when checked)
        assert "A. 池子扩展" in report


# ---------------------------------------------------------------------------
# Tests: helpers
# ---------------------------------------------------------------------------

class TestHelpers:
    """Tests for helper functions."""

    def test_get_latest_week_start(self):
        """Returns a Monday date string."""
        result = get_latest_week_start()
        dt = datetime.strptime(result, "%Y-%m-%d")
        assert dt.weekday() == 0  # Monday

    def test_find_attention_score(self):
        """Finds composite_score for a ticker."""
        ranking = [
            {"ticker": "NVDA", "composite_score": 3.5},
            {"ticker": "AMD", "composite_score": 2.1},
        ]
        assert _find_attention_score("NVDA", ranking) == 3.5
        assert _find_attention_score("AAPL", ranking) == 0.0

    def test_fetch_attention_ranking_no_data(self):
        """fetch_attention_ranking returns [] when no weeks."""
        with mock.patch("scripts.scan_themes.get_attention_store") as mock_store:
            mock_store.return_value.get_all_weeks.return_value = []
            result = fetch_attention_ranking()
        assert result == []

    def test_fetch_attention_ranking_with_data(self):
        """fetch_attention_ranking reads latest week."""
        mock_ranking = [
            {"ticker": "NVDA", "composite_score": 3.0, "rank": 1},
        ]
        with mock.patch("scripts.scan_themes.get_attention_store") as mock_store:
            store_instance = mock_store.return_value
            store_instance.get_all_weeks.return_value = ["2026-02-09", "2026-02-02"]
            store_instance.get_weekly_ranking.return_value = mock_ranking

            result = fetch_attention_ranking(top_n=10)

        assert len(result) == 1
        assert result[0]["ticker"] == "NVDA"
        store_instance.get_weekly_ranking.assert_called_once_with("2026-02-09", top_n=10)
