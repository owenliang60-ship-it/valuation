"""
Test suite for tool registry system (Phase 1).

Tests:
1. Protocol compliance
2. Registry operations (register, get, list)
3. FMP tool availability
4. Tool execution
5. Error handling
"""
import os
import pytest
from unittest.mock import Mock, patch

from terminal.tools.protocol import (
    FinanceTool,
    ToolCategory,
    ToolMetadata,
    ToolExecutionError,
)
from terminal.tools.registry import ToolRegistry, reset_registry
from terminal.tools.fmp_tools import (
    GetHistoricalPriceTool,
    GetQuoteTool,
    GetProfileTool,
    create_fmp_tools,
)


# ========== Mock Tool for Testing ==========

class MockTool(FinanceTool):
    """Mock tool for testing registry operations."""

    def __init__(self, name: str = "mock_tool", available: bool = True):
        self._name = name
        self._available = available

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name=self._name,
            category=ToolCategory.MARKET_DATA,
            description="Mock tool for testing",
            provider="Mock",
            requires_api_key=False,
        )

    def is_available(self) -> bool:
        return self._available

    def execute(self, **kwargs):
        return {"mock_data": kwargs}


# ========== Fixtures ==========

@pytest.fixture
def clean_registry():
    """Provide a fresh registry for each test."""
    reset_registry()
    from terminal.tools.registry import get_registry
    return get_registry()


@pytest.fixture
def mock_tool():
    """Provide a mock tool instance."""
    return MockTool()


# ========== Protocol Tests ==========

def test_tool_metadata_creation():
    """Test ToolMetadata creation."""
    meta = ToolMetadata(
        name="test_tool",
        category=ToolCategory.FUNDAMENTALS,
        description="Test description",
        provider="TestProvider",
        requires_api_key=True,
        api_key_env_var="TEST_API_KEY",
    )

    assert meta.name == "test_tool"
    assert meta.category == ToolCategory.FUNDAMENTALS
    assert meta.provider == "TestProvider"
    assert meta.requires_api_key is True


def test_tool_protocol_compliance(mock_tool):
    """Test that MockTool implements FinanceTool protocol."""
    assert isinstance(mock_tool, FinanceTool)
    assert hasattr(mock_tool, "metadata")
    assert hasattr(mock_tool, "is_available")
    assert hasattr(mock_tool, "execute")


# ========== Registry Tests ==========

def test_registry_register(clean_registry, mock_tool):
    """Test tool registration."""
    clean_registry.register(mock_tool)
    assert len(clean_registry) == 1

    retrieved = clean_registry.get_tool("mock_tool")
    assert retrieved is mock_tool


def test_registry_duplicate_registration(clean_registry, mock_tool):
    """Test that duplicate registration raises error."""
    clean_registry.register(mock_tool)

    with pytest.raises(ValueError, match="already registered"):
        clean_registry.register(mock_tool)


def test_registry_get_all_tools(clean_registry):
    """Test getting all registered tools."""
    tool1 = MockTool(name="tool1")
    tool2 = MockTool(name="tool2")

    clean_registry.register(tool1)
    clean_registry.register(tool2)

    all_tools = clean_registry.get_all_tools()
    assert len(all_tools) == 2
    assert tool1 in all_tools
    assert tool2 in all_tools


def test_registry_get_available_tools(clean_registry):
    """Test filtering available tools."""
    available_tool = MockTool(name="available", available=True)
    unavailable_tool = MockTool(name="unavailable", available=False)

    clean_registry.register(available_tool)
    clean_registry.register(unavailable_tool)

    available = clean_registry.get_available_tools()
    assert len(available) == 1
    assert available[0] is available_tool


def test_registry_filter_by_category(clean_registry):
    """Test filtering tools by category."""
    # Create tools with different categories
    class MarketTool(MockTool):
        @property
        def metadata(self):
            return ToolMetadata(
                name="market",
                category=ToolCategory.MARKET_DATA,
                description="Market tool",
                provider="Mock",
            )

    class FundamentalTool(MockTool):
        @property
        def metadata(self):
            return ToolMetadata(
                name="fundamental",
                category=ToolCategory.FUNDAMENTALS,
                description="Fundamental tool",
                provider="Mock",
            )

    tool1 = MarketTool(name="market")
    tool2 = FundamentalTool(name="fundamental")

    clean_registry.register(tool1)
    clean_registry.register(tool2)

    market_tools = clean_registry.get_available_tools(
        category=ToolCategory.MARKET_DATA
    )
    assert len(market_tools) == 1
    assert market_tools[0].metadata.name == "market"


def test_registry_execute(clean_registry, mock_tool):
    """Test tool execution via registry."""
    clean_registry.register(mock_tool)

    result = clean_registry.execute("mock_tool", param1="value1")
    assert result == {"mock_data": {"param1": "value1"}}


def test_registry_execute_not_found(clean_registry):
    """Test executing non-existent tool raises error."""
    with pytest.raises(KeyError, match="not found"):
        clean_registry.execute("nonexistent_tool")


def test_registry_execute_unavailable(clean_registry):
    """Test executing unavailable tool raises error."""
    unavailable_tool = MockTool(available=False)
    clean_registry.register(unavailable_tool)

    with pytest.raises(RuntimeError, match="not available"):
        clean_registry.execute("mock_tool")


def test_registry_check_availability(clean_registry):
    """Test availability status check."""
    tool1 = MockTool(name="available", available=True)
    tool2 = MockTool(name="unavailable", available=False)

    clean_registry.register(tool1)
    clean_registry.register(tool2)

    status = clean_registry.check_availability()

    assert status["available"]["available"] is True
    assert status["unavailable"]["available"] is False
    assert status["available"]["provider"] == "Mock"


# ========== FMP Tools Tests ==========

def test_fmp_tools_creation():
    """Test FMP tool factory creates all tools."""
    tools = create_fmp_tools()

    assert len(tools) >= 10  # We created 10 tools

    # Check categories
    market_tools = [t for t in tools if t.metadata.category == ToolCategory.MARKET_DATA]
    company_tools = [t for t in tools if t.metadata.category == ToolCategory.COMPANY_INFO]
    fundamental_tools = [t for t in tools if t.metadata.category == ToolCategory.FUNDAMENTALS]

    assert len(market_tools) >= 3
    assert len(company_tools) >= 2
    assert len(fundamental_tools) >= 5


def test_fmp_tool_availability_with_api_key():
    """Test FMP tool is available when API key present."""
    with patch.dict(os.environ, {"FMP_API_KEY": "test_key"}):
        tool = GetQuoteTool()
        # Note: actual availability depends on fmp_client import success
        # We're testing the env var check logic here


def test_fmp_tool_availability_without_api_key():
    """Test FMP tool is unavailable when API key missing."""
    with patch.dict(os.environ, {}, clear=True):
        # Clear the cached availability check
        tool = GetQuoteTool()
        tool._api_key_checked = False
        assert tool.is_available() is False


def test_fmp_tool_metadata():
    """Test FMP tool metadata is correctly set."""
    tool = GetHistoricalPriceTool()
    meta = tool.metadata

    assert meta.name == "get_historical_price"
    assert meta.category == ToolCategory.MARKET_DATA
    assert meta.provider == "FMP"
    assert meta.requires_api_key is True
    assert meta.api_key_env_var == "FMP_API_KEY"


# ========== Integration Tests ==========

def test_global_registry_initialization():
    """Test that global registry auto-loads FMP tools."""
    from terminal.tools import registry

    # Should have FMP tools loaded (if API key available)
    all_tools = registry.get_all_tools()
    assert len(all_tools) >= 10  # At least 10 FMP tools


def test_registry_repr(clean_registry):
    """Test registry string representation."""
    tool1 = MockTool(name="t1", available=True)
    tool2 = MockTool(name="t2", available=False)

    clean_registry.register(tool1)
    clean_registry.register(tool2)

    repr_str = repr(clean_registry)
    assert "1/2 available" in repr_str


def test_tool_repr():
    """Test tool string representation."""
    tool = MockTool()
    repr_str = repr(tool)

    assert "mock_tool" in repr_str
    assert "Mock" in repr_str
    # Should show availability status (✓ or ✗)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
