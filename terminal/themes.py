"""
Investment theme management — CRUD, membership, relevance detection.

Themes live at data/themes/{slug}/ with:
- theme.json:          Theme definition + thesis
- members.json:        Member tickers + roles
- thesis_history.jsonl: Thesis evolution log
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_PROJECT_ROOT = Path(__file__).parent.parent
_THEMES_DIR = _PROJECT_ROOT / "data" / "themes"
_REGISTRY_FILE = _THEMES_DIR / "registry.json"


# ---------------------------------------------------------------------------
# Theme data models
# ---------------------------------------------------------------------------

def _slugify(name: str) -> str:
    """Convert a theme name to a filesystem-safe slug."""
    return name.lower().replace(" ", "_").replace("-", "_").replace("/", "_")


# ---------------------------------------------------------------------------
# Registry (index of all themes)
# ---------------------------------------------------------------------------

def _load_registry() -> List[dict]:
    if not _REGISTRY_FILE.exists():
        return []
    try:
        with open(_REGISTRY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def _save_registry(entries: List[dict]) -> None:
    _THEMES_DIR.mkdir(parents=True, exist_ok=True)
    with open(_REGISTRY_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

def create_theme(
    name: str,
    thesis: str,
    status: str = "active",
    sub_themes: Optional[List[str]] = None,
    kill_conditions: Optional[List[str]] = None,
) -> dict:
    """
    Create a new investment theme.

    status: active / watchlist / mature / invalidated
    """
    slug = _slugify(name)
    theme_dir = _THEMES_DIR / slug
    theme_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now().isoformat()
    theme = {
        "slug": slug,
        "name": name,
        "status": status,
        "thesis": thesis,
        "sub_themes": sub_themes or [],
        "kill_conditions": kill_conditions or [],
        "created_at": now,
        "updated_at": now,
    }

    # Save theme.json
    with open(theme_dir / "theme.json", "w", encoding="utf-8") as f:
        json.dump(theme, f, ensure_ascii=False, indent=2)

    # Initialize members.json
    with open(theme_dir / "members.json", "w", encoding="utf-8") as f:
        json.dump([], f)

    # Initial thesis history entry
    with open(theme_dir / "thesis_history.jsonl", "a", encoding="utf-8") as f:
        entry = {"thesis": thesis, "status": status, "timestamp": now}
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    # Update registry
    registry = _load_registry()
    registry = [r for r in registry if r.get("slug") != slug]  # dedupe
    registry.append({"slug": slug, "name": name, "status": status, "updated_at": now})
    _save_registry(registry)

    logger.info(f"Created theme: {name} ({slug})")
    return theme


def get_theme(slug: str) -> Optional[dict]:
    """Get a theme by slug, including members."""
    theme_dir = _THEMES_DIR / slug
    theme_file = theme_dir / "theme.json"
    if not theme_file.exists():
        return None

    with open(theme_file, "r", encoding="utf-8") as f:
        theme = json.load(f)

    # Load members
    members_file = theme_dir / "members.json"
    if members_file.exists():
        with open(members_file, "r", encoding="utf-8") as f:
            theme["members"] = json.load(f)
    else:
        theme["members"] = []

    return theme


def update_theme(slug: str, **kwargs) -> Optional[dict]:
    """Update theme fields (thesis, status, sub_themes, kill_conditions)."""
    theme = get_theme(slug)
    if theme is None:
        return None

    theme_dir = _THEMES_DIR / slug
    now = datetime.now().isoformat()

    for key in ["thesis", "status", "sub_themes", "kill_conditions", "name"]:
        if key in kwargs:
            theme[key] = kwargs[key]

    theme["updated_at"] = now

    # Save
    members = theme.pop("members", [])
    with open(theme_dir / "theme.json", "w", encoding="utf-8") as f:
        json.dump(theme, f, ensure_ascii=False, indent=2)
    theme["members"] = members

    # Log thesis change
    if "thesis" in kwargs or "status" in kwargs:
        with open(theme_dir / "thesis_history.jsonl", "a", encoding="utf-8") as f:
            entry = {
                "thesis": theme["thesis"],
                "status": theme["status"],
                "timestamp": now,
            }
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    # Update registry
    registry = _load_registry()
    for r in registry:
        if r.get("slug") == slug:
            r["name"] = theme["name"]
            r["status"] = theme["status"]
            r["updated_at"] = now
    _save_registry(registry)

    return theme


def get_all_themes(status: Optional[str] = None) -> List[dict]:
    """Get all themes, optionally filtered by status."""
    registry = _load_registry()
    if status:
        registry = [r for r in registry if r.get("status") == status]
    return registry


# ---------------------------------------------------------------------------
# Membership
# ---------------------------------------------------------------------------

def add_ticker_to_theme(
    slug: str,
    symbol: str,
    role: str = "primary",
    sub_theme: str = "",
) -> bool:
    """
    Add a ticker to a theme.

    role: primary / secondary / pick_and_shovel / short_hedge
    """
    theme_dir = _THEMES_DIR / slug
    members_file = theme_dir / "members.json"
    if not members_file.exists():
        logger.warning(f"Theme {slug} not found")
        return False

    with open(members_file, "r", encoding="utf-8") as f:
        members = json.load(f)

    symbol = symbol.upper()

    # Dedupe
    members = [m for m in members if m.get("symbol") != symbol]
    members.append({
        "symbol": symbol,
        "role": role,
        "sub_theme": sub_theme,
        "added_at": datetime.now().isoformat(),
    })

    with open(members_file, "w", encoding="utf-8") as f:
        json.dump(members, f, ensure_ascii=False, indent=2)

    # Also update the ticker's meta to reference this theme
    from terminal.company_db import save_meta, get_meta
    meta = get_meta(symbol)
    themes = meta.get("themes", [])
    if slug not in themes:
        themes.append(slug)
    save_meta(symbol, {"themes": themes})

    return True


def remove_ticker_from_theme(slug: str, symbol: str) -> bool:
    """Remove a ticker from a theme."""
    theme_dir = _THEMES_DIR / slug
    members_file = theme_dir / "members.json"
    if not members_file.exists():
        return False

    with open(members_file, "r", encoding="utf-8") as f:
        members = json.load(f)

    symbol = symbol.upper()
    original_count = len(members)
    members = [m for m in members if m.get("symbol") != symbol]

    if len(members) == original_count:
        return False  # Not found

    with open(members_file, "w", encoding="utf-8") as f:
        json.dump(members, f, ensure_ascii=False, indent=2)

    return True


def get_ticker_themes(symbol: str) -> List[str]:
    """Get all themes a ticker belongs to."""
    from terminal.company_db import get_meta
    meta = get_meta(symbol.upper())
    return meta.get("themes", [])


def detect_theme_relevance(symbol: str) -> List[dict]:
    """
    Detect which existing themes a ticker might be relevant to.

    Uses sector/industry/description matching from Data Desk profiles.
    Returns list of {theme_slug, confidence, reason}.
    """
    matches = []

    # Get ticker info
    try:
        from src.data.data_query import get_stock_data
        stock = get_stock_data(symbol, price_days=1)
        sector = (stock.get("info") or {}).get("sector", "").lower()
        industry = (stock.get("info") or {}).get("industry", "").lower()
        description = ((stock.get("profile") or {}).get("description", "")).lower()
    except Exception:
        return matches

    # Check each active theme
    for entry in get_all_themes(status="active"):
        slug = entry["slug"]
        theme = get_theme(slug)
        if theme is None:
            continue

        thesis_lower = theme.get("thesis", "").lower()
        sub_themes = [s.lower() for s in theme.get("sub_themes", [])]

        # Simple keyword matching
        relevance_score = 0
        reasons = []

        # Check theme name / thesis against industry/sector
        for keyword in [slug.replace("_", " ")] + sub_themes:
            if keyword in industry:
                relevance_score += 3
                reasons.append(f"Industry match: {industry}")
            if keyword in sector:
                relevance_score += 2
                reasons.append(f"Sector match: {sector}")
            if keyword in description:
                relevance_score += 1
                reasons.append(f"Description mentions: {keyword}")

        if relevance_score > 0:
            confidence = "high" if relevance_score >= 3 else "medium" if relevance_score >= 2 else "low"
            matches.append({
                "theme_slug": slug,
                "theme_name": theme["name"],
                "confidence": confidence,
                "score": relevance_score,
                "reasons": list(set(reasons)),  # dedupe
            })

    matches.sort(key=lambda x: x["score"], reverse=True)
    return matches
