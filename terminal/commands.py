"""
Top-level commands — Claude calls these directly in conversation.

Each command returns a structured dict that Claude formats for the user.
"""
import logging
from typing import Any, Dict, Optional

from terminal.company_db import (
    get_company_record,
    list_all_companies,
    get_oprms,
    get_kill_conditions,
    get_all_memos,
    get_analyses,
    get_meta,
)
from terminal.pipeline import (
    collect_data,
    prepare_lens_prompts,
    prepare_memo_skeleton,
    calculate_position,
    DataPackage,
)

logger = logging.getLogger(__name__)


def analyze_ticker(
    symbol: str,
    depth: str = "quick",
    price_days: int = 60,
) -> Dict[str, Any]:
    """
    Entry point for ticker analysis.

    Depth levels:
    - "quick":    Data + indicators snapshot (~5 sec)
    - "standard": + 6 lens prompts for Claude to run
    - "full":     + debate prompts + memo skeleton + scoring rubric

    Returns a dict with data and (for standard/full) prompt sequences.
    """
    symbol = symbol.upper()
    result: Dict[str, Any] = {"symbol": symbol, "depth": depth}

    # Phase 1: Data collection (always)
    data_pkg = collect_data(symbol, price_days=price_days)
    result["data"] = {
        "info": data_pkg.info,
        "profile": data_pkg.profile,
        "fundamentals": data_pkg.fundamentals,
        "latest_price": data_pkg.latest_price,
        "indicators": data_pkg.indicators,
        "has_financials": data_pkg.has_financials,
    }

    # Existing company record
    record = data_pkg.company_record
    if record and record.has_data:
        result["existing_record"] = {
            "oprms": record.oprms,
            "kill_conditions_count": len(record.kill_conditions),
            "memos_count": len(record.memos),
            "analyses_count": len(record.analyses),
        }

    # Phase 2: Lens prompts (standard and full)
    if depth in ("standard", "full"):
        prompts = prepare_lens_prompts(symbol, data_pkg)
        result["lens_prompts"] = prompts
        result["lens_instructions"] = (
            f"Run each of the {len(prompts)} lens analyses below in sequence. "
            f"After all lenses, identify the 3 key tensions across perspectives."
        )

    # Phase 3+: Debate + memo (full only)
    if depth == "full":
        result["debate_instructions"] = (
            "After completing lens analyses and identifying 3 tensions, "
            "use terminal.pipeline.prepare_debate_prompts() with the tensions "
            "to generate 5-round debate prompts."
        )
        result["memo_skeleton"] = prepare_memo_skeleton(symbol)
        result["scoring_rubric"] = (
            "After writing the memo, use terminal.pipeline.score_memo() "
            "to check completeness and writing standards. Target score: > 7.0/10."
        )

    # Context summary for Claude
    result["context_summary"] = data_pkg.format_context()

    return result


def portfolio_status() -> Dict[str, Any]:
    """
    Comprehensive portfolio status check.

    Combines holdings, exposure alerts, and company DB records.
    """
    result: Dict[str, Any] = {}

    # Holdings
    try:
        from portfolio.holdings.manager import (
            load_holdings,
            refresh_prices,
            get_portfolio_summary,
        )
        positions = load_holdings()
        if positions:
            positions = refresh_prices(positions)
            result["summary"] = get_portfolio_summary(positions)

            # Run exposure alerts
            try:
                from portfolio.exposure.alerts import run_all_checks
                alerts = run_all_checks(positions)
                result["alerts"] = [a.to_dict() for a in alerts]
                result["alert_counts"] = {
                    "CRITICAL": sum(1 for a in alerts if a.level.value == "CRITICAL"),
                    "WARNING": sum(1 for a in alerts if a.level.value == "WARNING"),
                    "INFO": sum(1 for a in alerts if a.level.value == "INFO"),
                }
            except Exception as e:
                result["alerts_error"] = str(e)
        else:
            result["summary"] = {"total_positions": 0, "message": "No holdings found."}
    except Exception as e:
        result["error"] = f"Failed to load holdings: {e}"

    # Company DB coverage
    tracked = list_all_companies()
    result["company_db"] = {
        "tracked_tickers": len(tracked),
        "tickers": tracked,
    }

    return result


def position_advisor(
    symbol: str,
    total_capital: float = 1_000_000,
) -> Dict[str, Any]:
    """
    Position sizing advisor for a specific ticker.

    Checks OPRMS rating, IPS constraints, portfolio impact.
    """
    symbol = symbol.upper()
    result: Dict[str, Any] = {"symbol": symbol}

    # Current OPRMS
    oprms = get_oprms(symbol)
    if oprms:
        result["oprms"] = oprms
        sizing = calculate_position(
            symbol=symbol,
            dna=oprms["dna"],
            timing=oprms["timing"],
            timing_coeff=oprms.get("timing_coeff"),
            total_capital=total_capital,
            evidence_count=len(oprms.get("evidence", [])),
        )
        result["sizing"] = sizing
    else:
        result["oprms"] = None
        result["sizing_note"] = (
            f"No OPRMS rating found for {symbol}. "
            f"Run `analyze_ticker('{symbol}', depth='standard')` first."
        )

    # Kill conditions
    kc = get_kill_conditions(symbol)
    result["kill_conditions"] = kc
    if not kc:
        result["kill_warning"] = (
            f"No kill conditions defined for {symbol}. "
            f"Every position must have observable invalidation triggers."
        )

    # Current position (if held)
    try:
        from portfolio.holdings.manager import get_position
        pos = get_position(symbol)
        if pos:
            result["current_position"] = pos.to_dict()
        else:
            result["current_position"] = None
    except Exception:
        result["current_position"] = None

    return result


def company_lookup(symbol: str) -> Dict[str, Any]:
    """
    Everything we know about a company from the company DB.
    """
    symbol = symbol.upper()
    record = get_company_record(symbol)

    result: Dict[str, Any] = {
        "symbol": symbol,
        "has_data": record.has_data,
    }

    if not record.has_data:
        result["message"] = (
            f"No records found for {symbol} in company DB. "
            f"Run `analyze_ticker('{symbol}')` to start building the knowledge base."
        )
        return result

    result["oprms"] = record.oprms
    result["oprms_history_count"] = len(record.oprms_history)
    result["kill_conditions"] = record.kill_conditions
    result["memos"] = record.memos
    result["analyses"] = record.analyses
    result["meta"] = record.meta

    # Theme memberships
    themes = record.meta.get("themes", [])
    result["themes"] = themes

    return result


def run_monitor() -> Dict[str, Any]:
    """
    Run the full portfolio monitoring sweep.

    Delegates to terminal.monitor.run_full_monitor().
    """
    from terminal.monitor import run_full_monitor
    return run_full_monitor()


def theme_status(slug: str) -> Dict[str, Any]:
    """
    Get the status of an investment theme.

    Delegates to terminal.themes.
    """
    from terminal.themes import get_theme
    theme = get_theme(slug)
    if theme is None:
        return {"error": f"Theme '{slug}' not found."}
    return theme
