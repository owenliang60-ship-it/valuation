"""
Position history — audit trail for all position changes.

Every mutation to holdings is logged here with timestamp, action type, and details.
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)

_HISTORY_FILE = Path(__file__).parent / "history.json"


# Action types
ACTIONS = ("OPEN", "ADD", "TRIM", "CLOSE", "RATING_CHANGE", "REVIEW")


def log_position_change(symbol: str, action: str, details: dict) -> None:
    """
    Append a position change to the history log.

    Args:
        symbol: Ticker symbol
        action: One of OPEN, ADD, TRIM, CLOSE, RATING_CHANGE, REVIEW
        details: Dict with action-specific details
    """
    if action not in ACTIONS:
        logger.warning(f"Unknown action '{action}' for {symbol}, logging anyway")

    history = _load_history()
    entry = {
        "timestamp": datetime.now().isoformat(),
        "symbol": symbol.upper(),
        "action": action,
        "details": details,
    }
    history.append(entry)
    _save_history(history)
    logger.info(f"History: {symbol} {action}")


def get_position_history(symbol: Optional[str] = None) -> List[dict]:
    """
    Get history entries, optionally filtered by symbol.

    Args:
        symbol: If provided, filter to this symbol only. None = all entries.
    """
    history = _load_history()
    if symbol:
        symbol = symbol.upper()
        history = [h for h in history if h.get("symbol") == symbol]
    return history


def get_recent_history(days: int = 30) -> List[dict]:
    """Get history entries from the last N days."""
    history = _load_history()
    cutoff = datetime.now().timestamp() - (days * 86400)
    result = []
    for h in history:
        try:
            ts = datetime.fromisoformat(h["timestamp"]).timestamp()
            if ts >= cutoff:
                result.append(h)
        except (KeyError, ValueError):
            continue
    return result


# ---------------------------------------------------------------------------
# Internal
# ---------------------------------------------------------------------------

def _load_history() -> List[dict]:
    """Load history from JSON file."""
    if not _HISTORY_FILE.exists():
        return []
    try:
        with open(_HISTORY_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        logger.error(f"Failed to load history: {e}")
        return []


def _save_history(history: List[dict]) -> None:
    """Persist history to JSON file."""
    _HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(_HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
