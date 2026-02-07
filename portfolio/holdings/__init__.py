"""
Holdings — 持仓数据库

Core types: Position, WatchlistEntry, InvestmentBucket
Manager: load/save/add/update/remove positions
History: audit trail for all position changes
"""
from portfolio.holdings.schema import Position, WatchlistEntry, InvestmentBucket
from portfolio.holdings.manager import (
    load_holdings,
    save_holdings,
    add_position,
    update_position,
    remove_position,
    get_position,
    calculate_target_weight,
)

__all__ = [
    "Position",
    "WatchlistEntry",
    "InvestmentBucket",
    "load_holdings",
    "save_holdings",
    "add_position",
    "update_position",
    "remove_position",
    "get_position",
    "calculate_target_weight",
]
