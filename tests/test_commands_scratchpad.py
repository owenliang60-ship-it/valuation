"""Tests for scratchpad viewer commands."""
import pytest
from pathlib import Path

from terminal.commands import (
    list_analysis_scratchpads,
    replay_analysis_scratchpad,
    _summarize_event,
)
from terminal.scratchpad import AnalysisScratchpad


def test_list_analysis_scratchpads_empty(tmp_path, monkeypatch):
    """Test listing scratchpads when none exist."""
    monkeypatch.setattr("terminal.scratchpad._COMPANIES_DIR", tmp_path)

    result = list_analysis_scratchpads("AAPL")

    assert result["symbol"] == "AAPL"
    assert result["count"] == 0
    assert "No analysis scratchpads found" in result["message"]


def test_list_analysis_scratchpads(tmp_path, monkeypatch):
    """Test listing multiple scratchpads."""
    monkeypatch.setattr("terminal.scratchpad._COMPANIES_DIR", tmp_path)

    # Create scratchpads
    s1 = AnalysisScratchpad("TSLA", "quick", "Quick check")
    s2 = AnalysisScratchpad("TSLA", "full", "Full analysis")
    s3 = AnalysisScratchpad("TSLA", "standard", "Standard analysis")

    result = list_analysis_scratchpads("TSLA", limit=10)

    assert result["symbol"] == "TSLA"
    assert result["count"] == 3
    assert result["total_available"] == 3
    assert result["limit"] == 10

    # Check scratchpad metadata
    scratchpads = result["scratchpads"]
    assert len(scratchpads) == 3

    # All should have required fields
    for sp in scratchpads:
        assert "path" in sp
        assert "filename" in sp
        assert "timestamp" in sp
        assert sp["depth"] in ["quick", "full", "standard"]
        assert sp["query"] is not None
        assert sp["events_count"] >= 1  # At least query event


def test_list_analysis_scratchpads_limit(tmp_path, monkeypatch):
    """Test scratchpad listing with limit."""
    monkeypatch.setattr("terminal.scratchpad._COMPANIES_DIR", tmp_path)

    # Create 5 scratchpads
    for i in range(5):
        AnalysisScratchpad("NVDA", "quick", f"Analysis {i}")

    result = list_analysis_scratchpads("NVDA", limit=3)

    assert result["count"] == 3
    assert result["total_available"] == 5
    assert len(result["scratchpads"]) == 3


def test_replay_analysis_scratchpad_not_found():
    """Test replay with non-existent path."""
    result = replay_analysis_scratchpad("/nonexistent/path.jsonl")

    assert "error" in result
    assert "not found" in result["error"]


def test_replay_analysis_scratchpad(tmp_path, monkeypatch):
    """Test replaying a complete analysis scratchpad."""
    monkeypatch.setattr("terminal.scratchpad._COMPANIES_DIR", tmp_path)

    # Create scratchpad with various events
    scratchpad = AnalysisScratchpad("MSFT", "full", "Complete analysis")

    scratchpad.log_tool_call(
        "FMPPriceTool",
        {"symbol": "MSFT", "days": 60},
        {"price": 420.5, "volume": 2000000}
    )

    scratchpad.log_reasoning(
        "valuation_check",
        "PE 35x vs sector 28x, justified by cloud growth"
    )

    scratchpad.log_lens_complete("growth_story", "data/companies/MSFT/memos/growth.md")

    scratchpad.log_final_rating({
        "dna": "A",
        "timing": "B",
        "timing_coeff": 0.6,
        "position_pct": 9.0,
    })

    # Replay
    result = replay_analysis_scratchpad(str(scratchpad.log_path))

    assert "error" not in result
    assert result["log_path"] == str(scratchpad.log_path)

    # Check query info
    assert result["query"]["symbol"] == "MSFT"
    assert result["query"]["depth"] == "full"
    assert result["query"]["query"] == "Complete analysis"

    # Check stats
    stats = result["stats"]
    assert stats["total_events"] == 5  # query + tool + reasoning + lens + rating
    assert stats["tool_calls"] == 1
    assert stats["reasoning_steps"] == 1
    assert stats["lens_completed"] == 1
    assert stats["has_final_rating"] is True

    # Check timeline
    timeline = result["timeline"]
    assert len(timeline) == 5

    # Verify timeline order and types
    assert timeline[0]["type"] == "query"
    assert timeline[1]["type"] == "tool_call"
    assert timeline[2]["type"] == "reasoning"
    assert timeline[3]["type"] == "lens_complete"
    assert timeline[4]["type"] == "final_rating"

    # Check final rating
    assert result["final_rating"]["dna"] == "A"
    assert result["final_rating"]["timing"] == "B"


def test_replay_analysis_scratchpad_no_rating(tmp_path, monkeypatch):
    """Test replay of incomplete analysis (no final rating)."""
    monkeypatch.setattr("terminal.scratchpad._COMPANIES_DIR", tmp_path)

    scratchpad = AnalysisScratchpad("GOOGL", "quick")
    scratchpad.log_tool_call("FMPPriceTool", {"symbol": "GOOGL"}, {"price": 150.0})

    result = replay_analysis_scratchpad(str(scratchpad.log_path))

    assert result["stats"]["has_final_rating"] is False
    assert result["final_rating"] is None


def test_summarize_event_query():
    """Test query event summarization."""
    event = {
        "type": "query",
        "query": "Analyze AAPL",
        "depth": "full",
    }

    summary = _summarize_event(event)

    assert "Query:" in summary
    assert "Analyze AAPL" in summary
    assert "full" in summary


def test_summarize_event_tool_call():
    """Test tool call event summarization."""
    event = {
        "type": "tool_call",
        "tool": "FMPPriceTool",
        "args": {"symbol": "TSLA", "days": 90},
        "result_size": 12345,
    }

    summary = _summarize_event(event)

    assert "Tool:" in summary
    assert "FMPPriceTool" in summary
    assert "12345 bytes" in summary


def test_summarize_event_reasoning():
    """Test reasoning event summarization."""
    event = {
        "type": "reasoning",
        "step": "valuation_analysis",
        "content": "This is a long reasoning text that should be truncated in the preview",
    }

    summary = _summarize_event(event)

    assert "Reasoning:" in summary
    assert "valuation_analysis" in summary
    # Content should be truncated to 80 chars
    assert len(summary) <= 120  # "Reasoning: step — " + 80 chars


def test_summarize_event_lens_complete():
    """Test lens completion event summarization."""
    event = {
        "type": "lens_complete",
        "lens": "risk_assessment",
        "output_path": "/path/to/output.md",
    }

    summary = _summarize_event(event)

    assert "Lens complete:" in summary
    assert "risk_assessment" in summary
    assert "/path/to/output.md" in summary


def test_summarize_event_final_rating():
    """Test final rating event summarization."""
    event = {
        "type": "final_rating",
        "oprms": {
            "dna": "S",
            "timing": "A",
            "timing_coeff": 1.2,
        }
    }

    summary = _summarize_event(event)

    assert "Final rating:" in summary
    assert "DNA=S" in summary
    assert "Timing=A" in summary


def test_summarize_event_unknown():
    """Test unknown event type handling."""
    event = {
        "type": "unknown_type",
        "data": "something",
    }

    summary = _summarize_event(event)

    assert "Unknown event type:" in summary
    assert "unknown_type" in summary
