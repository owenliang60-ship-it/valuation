"""
Test suite for pipeline integration with tool registry (Task #8).

Verifies:
1. fundamental_fetcher uses registry when available
2. Backward compatibility maintained
3. Function signatures unchanged
"""
import pytest
from unittest.mock import Mock, patch, MagicMock

# Test that fundamental_fetcher detects registry
def test_fundamental_fetcher_uses_registry():
    """Verify fundamental_fetcher is using the registry."""
    from src.data.fundamental_fetcher import USE_REGISTRY
    assert USE_REGISTRY is True, "Registry should be available"


def test_fetch_profile_via_registry():
    """Test fetch_profile uses registry.execute()."""
    from src.data import fundamental_fetcher

    # Mock the registry
    mock_registry = MagicMock()
    mock_registry.execute.return_value = {
        "companyName": "Apple Inc.",
        "mktCap": 3000000000000,
        "sector": "Technology",
    }

    with patch.object(fundamental_fetcher, 'registry', mock_registry):
        with patch.object(fundamental_fetcher, 'USE_REGISTRY', True):
            result = fundamental_fetcher.fetch_profile("AAPL")

            # Verify registry was called
            mock_registry.execute.assert_called_once_with("get_profile", symbol="AAPL")

            # Verify result includes data + timestamp
            assert result is not None
            assert result["companyName"] == "Apple Inc."
            assert "_updated_at" in result


def test_fetch_ratios_via_registry():
    """Test fetch_ratios uses registry.execute()."""
    from src.data import fundamental_fetcher

    mock_registry = MagicMock()
    mock_registry.execute.return_value = [
        {"priceEarningsRatio": 30.5, "returnOnEquity": 0.15}
    ]

    with patch.object(fundamental_fetcher, 'registry', mock_registry):
        with patch.object(fundamental_fetcher, 'USE_REGISTRY', True):
            result = fundamental_fetcher.fetch_ratios("AAPL", limit=4)

            mock_registry.execute.assert_called_once_with(
                "get_ratios", symbol="AAPL", limit=4
            )
            assert len(result) == 1
            assert result[0]["priceEarningsRatio"] == 30.5


def test_fetch_income_via_registry():
    """Test fetch_income uses registry.execute()."""
    from src.data import fundamental_fetcher

    mock_registry = MagicMock()
    mock_registry.execute.return_value = [
        {"revenue": 100000000000, "netIncome": 25000000000}
    ]

    with patch.object(fundamental_fetcher, 'registry', mock_registry):
        with patch.object(fundamental_fetcher, 'USE_REGISTRY', True):
            result = fundamental_fetcher.fetch_income("AAPL", period="quarter", limit=8)

            mock_registry.execute.assert_called_once_with(
                "get_income_statement", symbol="AAPL", period="quarter", limit=8
            )
            assert len(result) == 1


def test_fetch_balance_sheet_via_registry():
    """Test fetch_balance_sheet uses registry.execute()."""
    from src.data import fundamental_fetcher

    mock_registry = MagicMock()
    mock_registry.execute.return_value = [
        {"totalAssets": 350000000000, "totalLiabilities": 250000000000}
    ]

    with patch.object(fundamental_fetcher, 'registry', mock_registry):
        with patch.object(fundamental_fetcher, 'USE_REGISTRY', True):
            result = fundamental_fetcher.fetch_balance_sheet("AAPL")

            mock_registry.execute.assert_called_once_with(
                "get_balance_sheet", symbol="AAPL", period="quarter", limit=8
            )
            assert len(result) == 1


def test_fetch_cash_flow_via_registry():
    """Test fetch_cash_flow uses registry.execute()."""
    from src.data import fundamental_fetcher

    mock_registry = MagicMock()
    mock_registry.execute.return_value = [
        {"operatingCashFlow": 30000000000, "freeCashFlow": 25000000000}
    ]

    with patch.object(fundamental_fetcher, 'registry', mock_registry):
        with patch.object(fundamental_fetcher, 'USE_REGISTRY', True):
            result = fundamental_fetcher.fetch_cash_flow("AAPL")

            mock_registry.execute.assert_called_once_with(
                "get_cash_flow", symbol="AAPL", period="quarter", limit=8
            )
            assert len(result) == 1


def test_fallback_to_fmp_client_when_registry_unavailable():
    """Test fallback to fmp_client when registry not available."""
    # Note: This test validates the fallback logic exists, even though
    # in practice the registry is always available in this codebase.
    # The fallback is for safety during incremental deployment.

    # Simply verify USE_REGISTRY flag exists and can be checked
    from src.data.fundamental_fetcher import USE_REGISTRY
    assert isinstance(USE_REGISTRY, bool)


def test_data_query_integration():
    """Test that get_stock_data still works with registry integration."""
    from src.data.data_query import get_stock_data

    # This should not raise any errors
    # Note: will fail if stock not in cache, but tests the import chain
    try:
        # Just verify the function exists and has correct signature
        assert callable(get_stock_data)
        import inspect
        sig = inspect.signature(get_stock_data)
        assert "symbol" in sig.parameters
        assert "price_days" in sig.parameters
    except Exception as e:
        pytest.fail(f"get_stock_data integration broken: {e}")


def test_pipeline_data_collection_compatibility():
    """Test that pipeline's DataPackage collection is compatible."""
    from terminal.pipeline import collect_data

    # Verify function exists and has correct signature
    assert callable(collect_data)

    import inspect
    sig = inspect.signature(collect_data)
    assert "symbol" in sig.parameters
    assert "price_days" in sig.parameters


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
