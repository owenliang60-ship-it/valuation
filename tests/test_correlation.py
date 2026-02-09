"""Tests for src/analysis/correlation.py"""
import json
import sys
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

# Ensure project root is on path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def _make_csv(tmp_path, symbol, dates, closes):
    """Helper: write a minimal price CSV for testing."""
    df = pd.DataFrame({
        "date": dates,
        "open": closes,
        "high": closes,
        "low": closes,
        "close": closes,
        "volume": [1000] * len(closes),
        "change": [0.0] * len(closes),
        "changePercent": [0.0] * len(closes),
    })
    df.to_csv(tmp_path / f"{symbol}.csv", index=False)


class TestLoadPriceReturns:
    def test_returns_none_when_no_file(self, tmp_path):
        with patch("src.analysis.correlation.PRICE_DIR", tmp_path):
            from src.analysis.correlation import load_price_returns
            result = load_price_returns("MISSING")
            assert result is None

    def test_loads_returns_from_csv(self, tmp_path):
        dates = pd.date_range("2025-01-01", periods=30, freq="B").strftime("%Y-%m-%d").tolist()
        closes = list(range(100, 130))
        _make_csv(tmp_path, "AAPL", dates, closes)

        with patch("src.analysis.correlation.PRICE_DIR", tmp_path):
            from src.analysis.correlation import load_price_returns
            ret = load_price_returns("AAPL", window=20)
            assert ret is not None
            assert isinstance(ret, pd.Series)
            assert ret.name == "AAPL"
            assert len(ret) <= 20
            # Returns should be positive (prices are monotonically increasing)
            assert (ret > 0).all()


class TestComputeCorrelationMatrix:
    def test_returns_empty_with_insufficient_data(self, tmp_path):
        # Only one symbol → not enough for correlation
        dates = pd.date_range("2025-01-01", periods=30, freq="B").strftime("%Y-%m-%d").tolist()
        _make_csv(tmp_path, "ONLY", dates, list(range(100, 130)))

        with patch("src.analysis.correlation.PRICE_DIR", tmp_path):
            from src.analysis.correlation import compute_correlation_matrix
            result = compute_correlation_matrix(["ONLY"], window=25)
            assert result == {}

    def test_computes_matrix_for_two_symbols(self, tmp_path):
        np.random.seed(42)
        dates = pd.date_range("2025-01-01", periods=130, freq="B").strftime("%Y-%m-%d").tolist()
        base = np.cumsum(np.random.randn(130)) + 100
        _make_csv(tmp_path, "AAA", dates, base.tolist())
        # BBB = correlated with AAA (same base + small noise)
        _make_csv(tmp_path, "BBB", dates, (base + np.random.randn(130) * 0.5).tolist())

        with patch("src.analysis.correlation.PRICE_DIR", tmp_path):
            from src.analysis.correlation import compute_correlation_matrix
            result = compute_correlation_matrix(["AAA", "BBB"], window=120)
            assert "AAA" in result
            assert "BBB" in result
            # Self-correlation should be 1.0
            assert result["AAA"]["AAA"] == 1.0
            assert result["BBB"]["BBB"] == 1.0
            # Cross-correlation should be high (>0.5) since BBB tracks AAA
            assert result["AAA"]["BBB"] > 0.5

    def test_skips_symbols_with_too_few_points(self, tmp_path):
        np.random.seed(42)
        dates_long = pd.date_range("2025-01-01", periods=130, freq="B").strftime("%Y-%m-%d").tolist()
        dates_short = pd.date_range("2025-01-01", periods=10, freq="B").strftime("%Y-%m-%d").tolist()
        _make_csv(tmp_path, "LONG1", dates_long, np.cumsum(np.random.randn(130) + 100).tolist())
        _make_csv(tmp_path, "LONG2", dates_long, np.cumsum(np.random.randn(130) + 100).tolist())
        _make_csv(tmp_path, "SHORT", dates_short, list(range(100, 110)))

        with patch("src.analysis.correlation.PRICE_DIR", tmp_path):
            from src.analysis.correlation import compute_correlation_matrix
            result = compute_correlation_matrix(["LONG1", "LONG2", "SHORT"], window=120)
            # SHORT should be excluded (< 20 data points after pct_change)
            assert "SHORT" not in result
            assert "LONG1" in result
            assert "LONG2" in result


class TestCacheRoundTrip:
    def test_save_and_load(self, tmp_path):
        cache_dir = tmp_path / "correlation"
        cache_file = cache_dir / "matrix.json"

        with patch("src.analysis.correlation.CORRELATION_CACHE_DIR", cache_dir), \
             patch("src.analysis.correlation.CORRELATION_CACHE_FILE", cache_file):
            from src.analysis.correlation import save_correlation_cache, load_correlation_cache

            matrix = {"AAPL": {"AAPL": 1.0, "NVDA": 0.85}, "NVDA": {"AAPL": 0.85, "NVDA": 1.0}}
            save_correlation_cache(matrix)

            assert cache_file.exists()

            loaded = load_correlation_cache()
            assert loaded == matrix

    def test_load_returns_none_when_no_cache(self, tmp_path):
        cache_file = tmp_path / "correlation" / "matrix.json"

        with patch("src.analysis.correlation.CORRELATION_CACHE_FILE", cache_file):
            from src.analysis.correlation import load_correlation_cache
            assert load_correlation_cache() is None


class TestGetCorrelationMatrix:
    def test_uses_cache_when_available(self, tmp_path):
        cached_matrix = {"AAPL": {"AAPL": 1.0, "NVDA": 0.9}, "NVDA": {"AAPL": 0.9, "NVDA": 1.0}}

        with patch("src.analysis.correlation.load_correlation_cache", return_value=cached_matrix), \
             patch("src.analysis.correlation.compute_correlation_matrix") as mock_compute:
            from src.analysis.correlation import get_correlation_matrix
            result = get_correlation_matrix(["AAPL", "NVDA"], use_cache=True)
            assert result == cached_matrix
            mock_compute.assert_not_called()

    def test_recomputes_when_cache_missing_symbols(self, tmp_path):
        cached_matrix = {"AAPL": {"AAPL": 1.0}}
        new_matrix = {"AAPL": {"AAPL": 1.0, "NVDA": 0.9}, "NVDA": {"AAPL": 0.9, "NVDA": 1.0}}

        with patch("src.analysis.correlation.load_correlation_cache", return_value=cached_matrix), \
             patch("src.analysis.correlation.compute_correlation_matrix", return_value=new_matrix), \
             patch("src.analysis.correlation.save_correlation_cache"):
            from src.analysis.correlation import get_correlation_matrix
            result = get_correlation_matrix(["AAPL", "NVDA"], use_cache=True)
            assert result == new_matrix

    def test_skips_cache_when_disabled(self, tmp_path):
        new_matrix = {"AAPL": {"AAPL": 1.0, "NVDA": 0.9}, "NVDA": {"AAPL": 0.9, "NVDA": 1.0}}

        with patch("src.analysis.correlation.load_correlation_cache") as mock_load, \
             patch("src.analysis.correlation.compute_correlation_matrix", return_value=new_matrix), \
             patch("src.analysis.correlation.save_correlation_cache"):
            from src.analysis.correlation import get_correlation_matrix
            result = get_correlation_matrix(["AAPL", "NVDA"], use_cache=False)
            mock_load.assert_not_called()
            assert result == new_matrix
