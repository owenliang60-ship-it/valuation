"""Tests for data freshness gate + realtime price validation."""
import sys
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_price_df(days_ago: int = 0, close: float = 100.0) -> pd.DataFrame:
    """Create a minimal price DataFrame with a date `days_ago` days in the past."""
    date = datetime.now() - timedelta(days=days_ago)
    return pd.DataFrame({
        "date": [date],
        "open": [close - 1],
        "high": [close + 1],
        "low": [close - 2],
        "close": [close],
        "volume": [1_000_000],
    })


# ---------------------------------------------------------------------------
# 1. get_price_df() freshness gate
# ---------------------------------------------------------------------------

class TestGetPriceDfFreshness:
    """Test max_age_days parameter in get_price_df()."""

    @patch("src.data.price_fetcher.fetch_and_update_price")
    @patch("src.data.price_fetcher.load_price_cache")
    def test_fresh_cache_not_refreshed(self, mock_load, mock_fetch):
        """Cache within max_age_days should NOT trigger refresh."""
        mock_load.return_value = _make_price_df(days_ago=1, close=150.0)
        mock_fetch.return_value = _make_price_df(days_ago=0, close=151.0)

        from src.data.price_fetcher import get_price_df
        df = get_price_df("AAPL", max_age_days=3)

        assert df is not None
        mock_fetch.assert_not_called()  # Should use cache
        assert float(df["close"].iloc[0]) == 150.0

    @patch("src.data.price_fetcher.fetch_and_update_price")
    @patch("src.data.price_fetcher.load_price_cache")
    def test_stale_cache_triggers_refresh(self, mock_load, mock_fetch):
        """Cache older than max_age_days should trigger auto-refresh."""
        mock_load.return_value = _make_price_df(days_ago=5, close=140.0)
        mock_fetch.return_value = _make_price_df(days_ago=0, close=150.0)

        from src.data.price_fetcher import get_price_df
        df = get_price_df("AAPL", max_age_days=3)

        assert df is not None
        mock_fetch.assert_called_once_with("AAPL")
        assert float(df["close"].iloc[0]) == 150.0

    @patch("src.data.price_fetcher.fetch_and_update_price")
    @patch("src.data.price_fetcher.load_price_cache")
    def test_exactly_at_threshold_not_refreshed(self, mock_load, mock_fetch):
        """Cache exactly at max_age_days boundary should NOT refresh."""
        mock_load.return_value = _make_price_df(days_ago=3, close=140.0)

        from src.data.price_fetcher import get_price_df
        df = get_price_df("AAPL", max_age_days=3)

        mock_fetch.assert_not_called()

    @patch("src.data.price_fetcher.fetch_and_update_price")
    @patch("src.data.price_fetcher.load_price_cache")
    def test_no_cache_fetches_fresh(self, mock_load, mock_fetch):
        """No cache at all should trigger fresh fetch."""
        mock_load.return_value = None
        mock_fetch.return_value = _make_price_df(days_ago=0, close=200.0)

        from src.data.price_fetcher import get_price_df
        df = get_price_df("AAPL", max_age_days=3)

        mock_fetch.assert_called_once_with("AAPL")
        assert float(df["close"].iloc[0]) == 200.0

    @patch("src.data.price_fetcher.fetch_and_update_price")
    @patch("src.data.price_fetcher.load_price_cache")
    def test_max_age_zero_skips_check(self, mock_load, mock_fetch):
        """max_age_days=0 should skip freshness check and use cache as-is."""
        mock_load.return_value = _make_price_df(days_ago=30, close=100.0)

        from src.data.price_fetcher import get_price_df
        df = get_price_df("AAPL", max_age_days=0)

        mock_fetch.assert_not_called()
        assert float(df["close"].iloc[0]) == 100.0

    @patch("src.data.price_fetcher.fetch_and_update_price")
    @patch("src.data.price_fetcher.load_price_cache")
    def test_days_parameter_respected(self, mock_load, mock_fetch):
        """days parameter should limit returned rows."""
        dates = [datetime.now() - timedelta(days=i) for i in range(10)]
        df = pd.DataFrame({
            "date": dates,
            "open": range(10),
            "high": range(10),
            "low": range(10),
            "close": range(10),
            "volume": range(10),
        })
        mock_load.return_value = df

        from src.data.price_fetcher import get_price_df
        result = get_price_df("AAPL", days=3, max_age_days=3)

        assert len(result) == 3


# ---------------------------------------------------------------------------
# 2. get_realtime_price()
# ---------------------------------------------------------------------------

class TestGetRealtimePrice:
    """Test FMP client get_realtime_price()."""

    @patch("src.data.fmp_client.FMPClient._request")
    def test_returns_price_from_profile(self, mock_req):
        """Should extract price from profile API response."""
        mock_req.return_value = [{"price": 394.69, "companyName": "Micron"}]

        from src.data.fmp_client import FMPClient
        client = FMPClient(api_key="test")
        price = client.get_realtime_price("MU")

        assert price == 394.69
        mock_req.assert_called_once_with("profile", {"symbol": "MU"})

    @patch("src.data.fmp_client.FMPClient._request")
    def test_returns_none_on_empty_response(self, mock_req):
        """Should return None if API returns empty list."""
        mock_req.return_value = []

        from src.data.fmp_client import FMPClient
        client = FMPClient(api_key="test")
        price = client.get_realtime_price("FAKE")

        assert price is None

    @patch("src.data.fmp_client.FMPClient._request")
    def test_returns_none_on_api_failure(self, mock_req):
        """Should return None if API returns None."""
        mock_req.return_value = None

        from src.data.fmp_client import FMPClient
        client = FMPClient(api_key="test")
        price = client.get_realtime_price("MU")

        assert price is None

    @patch("src.data.fmp_client.FMPClient._request")
    def test_returns_none_when_price_missing(self, mock_req):
        """Should return None if profile has no price key."""
        mock_req.return_value = [{"companyName": "Micron"}]

        from src.data.fmp_client import FMPClient
        client = FMPClient(api_key="test")
        price = client.get_realtime_price("MU")

        assert price is None


# ---------------------------------------------------------------------------
# 3. collect_data() realtime price validation
# ---------------------------------------------------------------------------

class TestCollectDataPriceValidation:
    """Test realtime price check in collect_data()."""

    def _make_stock_data(self, close: float = 437.80):
        """Return a dict matching get_stock_data() output shape."""
        return {
            "symbol": "MU",
            "info": {"companyName": "Micron", "sector": "Technology", "marketCap": 100e9},
            "profile": None,
            "fundamentals": None,
            "ratios": [],
            "income": [],
            "price": {
                "latest_date": "2026-02-02",
                "latest_close": close,
                "records": 60,
            },
        }

    @patch("terminal.pipeline.get_company_record", return_value=None)
    @patch("src.data.fmp_client.FMPClient.get_realtime_price")
    @patch("src.data.data_query.get_stock_data")
    @patch("src.data.pool_manager.ensure_in_pool", return_value=None)
    def test_large_deviation_replaces_price(self, mock_pool, mock_stock, mock_rt, mock_cr):
        """When deviation > 2%, cached price should be replaced with realtime."""
        mock_stock.return_value = self._make_stock_data(close=437.80)
        mock_rt.return_value = 394.69  # ~11% deviation

        from terminal.pipeline import collect_data
        pkg = collect_data("MU")

        assert pkg.price["latest_close"] == 394.69
        assert pkg.price["price_source"] == "realtime"
        assert pkg.price["realtime_price"] == 394.69
        assert pkg.price["price_deviation"] > 2.0

    @patch("terminal.pipeline.get_company_record", return_value=None)
    @patch("src.data.fmp_client.FMPClient.get_realtime_price")
    @patch("src.data.data_query.get_stock_data")
    @patch("src.data.pool_manager.ensure_in_pool", return_value=None)
    def test_small_deviation_keeps_cache(self, mock_pool, mock_stock, mock_rt, mock_cr):
        """When deviation <= 2%, should keep cached price."""
        mock_stock.return_value = self._make_stock_data(close=393.0)
        mock_rt.return_value = 394.69  # ~0.4% deviation

        from terminal.pipeline import collect_data
        pkg = collect_data("MU")

        assert pkg.price["latest_close"] == 393.0
        assert pkg.price["price_source"] == "cache"

    @patch("terminal.pipeline.get_company_record", return_value=None)
    @patch("src.data.fmp_client.FMPClient.get_realtime_price")
    @patch("src.data.data_query.get_stock_data")
    @patch("src.data.pool_manager.ensure_in_pool", return_value=None)
    def test_realtime_failure_graceful(self, mock_pool, mock_stock, mock_rt, mock_cr):
        """When realtime API fails, should keep cached price without error."""
        mock_stock.return_value = self._make_stock_data(close=437.80)
        mock_rt.side_effect = Exception("API down")

        from terminal.pipeline import collect_data
        pkg = collect_data("MU")

        # Should still have the cached price, no crash
        assert pkg.price["latest_close"] == 437.80
        assert pkg.price.get("price_source") is None  # Not set on failure

    @patch("terminal.pipeline.get_company_record", return_value=None)
    @patch("src.data.fmp_client.FMPClient.get_realtime_price")
    @patch("src.data.data_query.get_stock_data")
    @patch("src.data.pool_manager.ensure_in_pool", return_value=None)
    def test_realtime_returns_none_graceful(self, mock_pool, mock_stock, mock_rt, mock_cr):
        """When realtime returns None, should keep cached price."""
        mock_stock.return_value = self._make_stock_data(close=437.80)
        mock_rt.return_value = None

        from terminal.pipeline import collect_data
        pkg = collect_data("MU")

        assert pkg.price["latest_close"] == 437.80
        assert pkg.price.get("price_source") is None

    @patch("terminal.pipeline.get_company_record", return_value=None)
    @patch("src.data.fmp_client.FMPClient.get_realtime_price")
    @patch("src.data.data_query.get_stock_data")
    @patch("src.data.pool_manager.ensure_in_pool", return_value=None)
    def test_no_price_data_skips_check(self, mock_pool, mock_stock, mock_rt, mock_cr):
        """When no price data collected, should skip realtime check entirely."""
        data = self._make_stock_data()
        data["price"] = None
        mock_stock.return_value = data

        from terminal.pipeline import collect_data
        pkg = collect_data("MU")

        mock_rt.assert_not_called()
        assert pkg.price is None


# ---------------------------------------------------------------------------
# 4. format_context() price source display
# ---------------------------------------------------------------------------

class TestFormatContextPriceSource:
    """Test that format_context shows price source info."""

    def test_cache_source_displayed(self):
        from terminal.pipeline import DataPackage
        pkg = DataPackage(symbol="AAPL")
        pkg.price = {
            "latest_close": 185.0,
            "latest_date": "2026-02-07",
            "records": 60,
            "price_source": "cache",
            "realtime_price": 185.5,
            "price_deviation": 0.27,
        }
        ctx = pkg.format_context()
        assert "[source: cache]" in ctx
        assert "stale" not in ctx.lower()

    def test_realtime_source_shows_deviation(self):
        from terminal.pipeline import DataPackage
        pkg = DataPackage(symbol="MU")
        pkg.price = {
            "latest_close": 394.69,
            "latest_date": "2026-02-02",
            "records": 60,
            "price_source": "realtime",
            "realtime_price": 394.69,
            "price_deviation": 9.84,
        }
        ctx = pkg.format_context()
        assert "[source: realtime]" in ctx
        assert "9.84%" in ctx
        assert "stale" in ctx.lower()

    def test_no_source_defaults_to_cache(self):
        from terminal.pipeline import DataPackage
        pkg = DataPackage(symbol="AAPL")
        pkg.price = {
            "latest_close": 185.0,
            "latest_date": "2026-02-07",
            "records": 60,
        }
        ctx = pkg.format_context()
        assert "[source: cache]" in ctx
