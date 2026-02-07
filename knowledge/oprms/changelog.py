"""
OPRMS 评级变更日志 — 带证据追踪

每次评级变更追加到 JSONL 文件，支持按 symbol 查询历史。
"""
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


@dataclass
class RatingChange:
    """单次评级变更记录"""
    symbol: str
    field_changed: str  # "dna" | "timing" | "timing_coeff" | "investment_bucket"
    old_value: str
    new_value: str
    evidence: List[str]  # 支持变更的证据
    rationale: str       # 变更理由
    changed_at: str = field(default_factory=lambda: datetime.now().isoformat())
    changed_by: str = "user"  # "user" | "system" | "ai_review"

    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "field_changed": self.field_changed,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "evidence": self.evidence,
            "rationale": self.rationale,
            "changed_at": self.changed_at,
            "changed_by": self.changed_by,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "RatingChange":
        return cls(
            symbol=d["symbol"],
            field_changed=d["field_changed"],
            old_value=d["old_value"],
            new_value=d["new_value"],
            evidence=d.get("evidence", []),
            rationale=d.get("rationale", ""),
            changed_at=d.get("changed_at", ""),
            changed_by=d.get("changed_by", "user"),
        )


def log_rating_change(change: RatingChange, log_path: Path) -> None:
    """
    追加变更记录到 JSONL 文件

    Args:
        change: 变更记录
        log_path: JSONL 文件路径
    """
    log_path.parent.mkdir(parents=True, exist_ok=True)

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(change.to_dict(), ensure_ascii=False) + "\n")

    logger.info(
        f"评级变更: {change.symbol} {change.field_changed} "
        f"{change.old_value} → {change.new_value}"
    )


def get_rating_history(
    symbol: str,
    log_path: Path,
    field_changed: Optional[str] = None,
) -> List[RatingChange]:
    """
    查询指定 symbol 的评级变更历史

    Args:
        symbol: 股票代码
        log_path: JSONL 文件路径
        field_changed: 可选，只看特定字段的变更

    Returns:
        按时间正序排列的变更记录列表
    """
    if not log_path.exists():
        return []

    changes = []
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
                if d["symbol"] == symbol:
                    if field_changed is None or d["field_changed"] == field_changed:
                        changes.append(RatingChange.from_dict(d))
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"解析变更记录失败: {e}")

    return sorted(changes, key=lambda c: c.changed_at)


def get_all_changes(log_path: Path, limit: int = 50) -> List[RatingChange]:
    """
    获取最近的所有变更记录

    Args:
        log_path: JSONL 文件路径
        limit: 最多返回条数

    Returns:
        按时间倒序排列的变更记录
    """
    if not log_path.exists():
        return []

    changes = []
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                changes.append(RatingChange.from_dict(json.loads(line)))
            except (json.JSONDecodeError, KeyError):
                continue

    changes.sort(key=lambda c: c.changed_at, reverse=True)
    return changes[:limit]
