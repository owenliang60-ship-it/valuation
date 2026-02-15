"""Tests for terminal/theme_pool.py — pool expansion from attention engine.

Tests:
1. expand_pool_from_attention: adds new tickers
2. expand_pool_from_attention: skips existing tickers
3. expand_pool_from_attention: respects max_new limit
4. expand_pool_from_attention: dry_run mode
5. expand_pool_from_attention: handles FMP failure
6. expand_pool_from_attention: records history
7. get_attention_pool: returns only attention-source stocks
8. remove_from_attention_pool: removes attention stock
9. remove_from_attention_pool: rejects non-attention stock
10. get_pool_expansion_stats: correct counts
"""
import json
import pytest
from datetime import datetime
from pathlib import Path
from unittest import mock

from terminal.theme_pool import (
    expand_pool_from_attention,
    get_attention_pool,
    remove_from_attention_pool,
    get_pool_expansion_stats,
)
from src.data.pool_manager import (
    load_universe,
    save_universe,
    load_history,
    UNIVERSE_FILE,
    HISTORY_FILE,
)


EXISTING_POOL = [
    {
        "symbol": "AAPL",
        "companyName": "Apple Inc",
        "marketCap": 3_500_000_000_000,
        "sector": "Technology",
        "industry": "Consumer Electronics",
        "exchange": "NASDAQ",
    },
    {
        "symbol": "NVDA",
        "companyName": "NVIDIA Corporation",
        "marketCap": 3_200_000_000_000,
        "sector": "Technology",
        "industry": "Semiconductors",
        "exchange": "NASDAQ",
    },
]

SAMPLE_PROFILE = {
    "symbol": "IONQ",
    "companyName": "IonQ Inc",
    "mktCap": 8_000_000_000,
    "sector": "Technology",
    "industry": "Computer Hardware",
    "exchangeShortName": "NYSE",
    "country": "US",
}

SAMPLE_PROFILE_2 = {
    "symbol": "RKLB",
    "companyName": "Rocket Lab USA Inc",
    "mktCap": 12_000_000_000,
    "sector": "Industrials",
    "industry": "Aerospace & Defense",
    "exchangeShortName": "NASDAQ",
    "country": "US",
}


@pytest.fixture(autouse=True)
def _isolate_pool(tmp_path, monkeypatch):
    """Redirect pool files to tmp_path."""
    pool_dir = tmp_path / "pool"
    pool_dir.mkdir()
    price_dir = tmp_path / "price"
    price_dir.mkdir()

    universe = pool_dir / "universe.json"
    history = pool_dir / "pool_history.json"
    universe.write_text(json.dumps(EXISTING_POOL))
    history.write_text("[]")

    monkeypatch.setattr("src.data.pool_manager.UNIVERSE_FILE", universe)
    monkeypatch.setattr("src.data.pool_manager.HISTORY_FILE", history)
    monkeypatch.setattr("src.data.pool_manager.POOL_DIR", pool_dir)
    monkeypatch.setattr("terminal.theme_pool.load_universe", lambda: json.loads(universe.read_text()))
    monkeypatch.setattr("terminal.theme_pool.save_universe", lambda stocks: universe.write_text(json.dumps(stocks, ensure_ascii=False, indent=2)))
    monkeypatch.setattr("terminal.theme_pool.load_history", lambda: json.loads(history.read_text()))
    monkeypatch.setattr("terminal.theme_pool.save_history", lambda h: history.write_text(json.dumps(h, ensure_ascii=False, indent=2)))
    monkeypatch.setattr("terminal.theme_pool.get_symbols", lambda: [s["symbol"] for s in json.loads(universe.read_text())])


class TestExpandPoolFromAttention:
    """Tests for expand_pool_from_attention()."""

    def test_adds_new_tickers(self, tmp_path, monkeypatch):
        """New tickers get FMP profile + price fetch + added to pool."""
        with mock.patch("terminal.theme_pool.fmp_client") as mock_fmp, \
             mock.patch("src.data.price_fetcher.fetch_and_update_price") as mock_price:
            mock_fmp.get_profile.return_value = SAMPLE_PROFILE
            mock_price.return_value = None  # price fetch ok but empty

            result = expand_pool_from_attention(["IONQ"])

        assert len(result["added"]) == 1
        assert result["added"][0]["symbol"] == "IONQ"
        assert result["added"][0]["source"] == "attention"
        assert not result["failed"]

    def test_skips_existing_tickers(self):
        """Tickers already in pool are skipped."""
        result = expand_pool_from_attention(["AAPL", "NVDA"])

        assert len(result["skipped_in_pool"]) == 2
        assert len(result["added"]) == 0

    def test_mixed_new_and_existing(self, monkeypatch):
        """Mix of new and existing tickers."""
        with mock.patch("terminal.theme_pool.fmp_client") as mock_fmp, \
             mock.patch("src.data.price_fetcher.fetch_and_update_price"):
            mock_fmp.get_profile.return_value = SAMPLE_PROFILE

            result = expand_pool_from_attention(["AAPL", "IONQ", "NVDA"])

        assert result["skipped_in_pool"] == ["AAPL", "NVDA"]
        assert len(result["added"]) == 1
        assert result["added"][0]["symbol"] == "IONQ"

    def test_max_new_limit(self, monkeypatch):
        """Respects max_new safety valve."""
        profiles = {
            "IONQ": SAMPLE_PROFILE,
            "RKLB": SAMPLE_PROFILE_2,
        }

        with mock.patch("terminal.theme_pool.fmp_client") as mock_fmp, \
             mock.patch("src.data.price_fetcher.fetch_and_update_price"):
            mock_fmp.get_profile.side_effect = lambda t: profiles.get(t)

            result = expand_pool_from_attention(
                ["IONQ", "RKLB", "FAKE1"], max_new=1
            )

        assert len(result["added"]) == 1
        assert result["added"][0]["symbol"] == "IONQ"

    def test_dry_run_mode(self):
        """Dry run reports candidates but doesn't modify pool."""
        result = expand_pool_from_attention(["IONQ", "RKLB"], dry_run=True)

        assert result["dry_run"] is True
        assert len(result["added"]) == 2

        # Pool should be unchanged
        pool = load_universe()
        symbols = [s["symbol"] for s in pool]
        assert "IONQ" not in symbols

    def test_fmp_failure(self, monkeypatch):
        """FMP returns None for a ticker -> goes to failed list."""
        with mock.patch("terminal.theme_pool.fmp_client") as mock_fmp, \
             mock.patch("src.data.price_fetcher.fetch_and_update_price"):
            mock_fmp.get_profile.return_value = None

            result = expand_pool_from_attention(["BADTICKER"])

        assert result["failed"] == ["BADTICKER"]
        assert len(result["added"]) == 0

    def test_records_history(self, tmp_path, monkeypatch):
        """Pool expansion records entry in pool history."""
        with mock.patch("terminal.theme_pool.fmp_client") as mock_fmp, \
             mock.patch("src.data.price_fetcher.fetch_and_update_price"):
            mock_fmp.get_profile.return_value = SAMPLE_PROFILE

            expand_pool_from_attention(["IONQ"])

        history = load_history()
        assert len(history) == 1
        assert history[0]["entered"] == ["IONQ"]
        assert history[0]["reason"] == "theme-engine-attention"

    def test_dedup_input(self, monkeypatch):
        """Duplicate tickers in input are deduplicated."""
        with mock.patch("terminal.theme_pool.fmp_client") as mock_fmp, \
             mock.patch("src.data.price_fetcher.fetch_and_update_price"):
            mock_fmp.get_profile.return_value = SAMPLE_PROFILE

            result = expand_pool_from_attention(["IONQ", "ionq", "IONQ"])

        assert len(result["added"]) == 1

    def test_empty_input(self):
        """Empty input returns empty result."""
        result = expand_pool_from_attention([])
        assert result["added"] == []
        assert result["skipped_in_pool"] == []


class TestGetAttentionPool:
    """Tests for get_attention_pool()."""

    def test_returns_only_attention_source(self):
        """Only stocks with source=attention are returned."""
        pool = EXISTING_POOL + [
            {"symbol": "IONQ", "source": "attention"},
            {"symbol": "VRT", "source": "analysis"},
        ]
        save_universe(pool)

        result = get_attention_pool()
        symbols = [s["symbol"] for s in result]
        assert "IONQ" in symbols
        assert "VRT" not in symbols
        assert "AAPL" not in symbols

    def test_empty_when_no_attention(self):
        """Returns empty when no attention stocks exist."""
        result = get_attention_pool()
        assert result == []


class TestRemoveFromAttentionPool:
    """Tests for remove_from_attention_pool()."""

    def test_removes_attention_stock(self, monkeypatch):
        """Can remove an attention-source stock."""
        pool = EXISTING_POOL + [
            {"symbol": "IONQ", "companyName": "IonQ", "source": "attention"},
        ]
        save_universe(pool)

        ok = remove_from_attention_pool("IONQ")
        assert ok is True

        pool = load_universe()
        symbols = [s["symbol"] for s in pool]
        assert "IONQ" not in symbols
        assert len(pool) == 2  # original 2 remain

    def test_rejects_non_attention_stock(self):
        """Cannot remove a non-attention stock."""
        ok = remove_from_attention_pool("AAPL")
        assert ok is False

        pool = load_universe()
        assert len(pool) == 2  # unchanged

    def test_rejects_unknown_symbol(self):
        """Unknown symbol returns False."""
        ok = remove_from_attention_pool("ZZZZZ")
        assert ok is False

    def test_records_removal_history(self, monkeypatch):
        """Removal records exit in pool history."""
        pool = EXISTING_POOL + [
            {"symbol": "IONQ", "source": "attention"},
        ]
        save_universe(pool)

        remove_from_attention_pool("IONQ")

        history = load_history()
        assert len(history) == 1
        assert history[0]["exited"] == ["IONQ"]
        assert history[0]["reason"] == "manual-remove-attention"


class TestGetPoolExpansionStats:
    """Tests for get_pool_expansion_stats()."""

    def test_counts_all_sources(self, monkeypatch):
        """Correct counts for each source type."""
        pool = [
            {"symbol": "AAPL"},  # no source = screener
            {"symbol": "MSFT", "source": "screener"},
            {"symbol": "VRT", "source": "analysis"},
            {"symbol": "IONQ", "source": "attention"},
            {"symbol": "RKLB", "source": "attention"},
        ]
        save_universe(pool)

        stats = get_pool_expansion_stats()
        assert stats["total"] == 5
        assert stats["screener"] == 2
        assert stats["analysis"] == 1
        assert stats["attention"] == 2
        assert stats["unknown"] == 0

    def test_empty_pool(self, monkeypatch):
        """Empty pool returns all zeros."""
        save_universe([])
        stats = get_pool_expansion_stats()
        assert stats["total"] == 0
        assert stats["screener"] == 0
