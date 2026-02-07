"""
OPRMS 集成规范 — Portfolio Desk 消费接口

定义 JSON schema 和导出格式，供 Portfolio Desk 读取评级数据。
"""
import json
import logging
from pathlib import Path
from typing import Dict, List

from knowledge.oprms.models import OPRMSRating, DNARating, TimingRating

logger = logging.getLogger(__name__)

# Portfolio Desk 消费的 JSON Schema
PORTFOLIO_SCHEMA = {
    "version": "1.0",
    "description": "OPRMS ratings export for Portfolio Desk consumption",
    "fields": {
        "symbol": {"type": "string", "description": "Ticker symbol"},
        "dna": {"type": "string", "enum": ["S", "A", "B", "C"], "description": "DNA rating"},
        "dna_max_position_pct": {"type": "number", "description": "Max position % from DNA"},
        "timing": {"type": "string", "enum": ["S", "A", "B", "C"], "description": "Timing rating"},
        "timing_coeff": {"type": "number", "description": "Exact timing coefficient"},
        "target_weight_pct": {"type": "number", "description": "Target portfolio weight %"},
        "investment_bucket": {
            "type": "string",
            "enum": [
                "Long-term Compounder",
                "Catalyst-Driven Long",
                "Short Position",
                "Secular Short",
            ],
            "description": "Investment classification bucket",
        },
        "evidence_count": {"type": "integer", "description": "Number of evidence items"},
        "updated_at": {"type": "string", "description": "ISO timestamp of last update"},
    },
}


def export_for_portfolio(ratings: Dict[str, OPRMSRating]) -> Dict:
    """
    导出评级数据为 Portfolio Desk 格式

    Args:
        ratings: {symbol: OPRMSRating}

    Returns:
        结构化导出数据
    """
    exports = []
    for symbol, rating in sorted(ratings.items()):
        target_weight = rating.dna.max_position_pct * rating.timing_coeff
        exports.append({
            "symbol": symbol,
            "dna": rating.dna.value,
            "dna_max_position_pct": round(rating.dna.max_position_pct * 100, 2),
            "timing": rating.timing.value,
            "timing_coeff": rating.timing_coeff,
            "target_weight_pct": round(target_weight * 100, 2),
            "investment_bucket": rating.investment_bucket,
            "evidence_count": len(rating.evidence),
            "updated_at": rating.updated_at,
        })

    return {
        "schema_version": "1.0",
        "count": len(exports),
        "positions": exports,
    }


def validate_rating_data(data: dict) -> List[str]:
    """
    验证评级数据是否符合 schema

    Args:
        data: 待验证的数据字典

    Returns:
        错误列表 (空列表 = 通过)
    """
    errors = []
    valid_dna = {r.value for r in DNARating}
    valid_timing = {r.value for r in TimingRating}
    valid_buckets = {
        "Long-term Compounder",
        "Catalyst-Driven Long",
        "Short Position",
        "Secular Short",
        "",  # allow empty during initial setup
    }

    if "positions" not in data:
        errors.append("Missing 'positions' key")
        return errors

    for i, pos in enumerate(data["positions"]):
        prefix = f"positions[{i}]"

        if "symbol" not in pos:
            errors.append(f"{prefix}: missing 'symbol'")
            continue

        sym = pos["symbol"]

        if pos.get("dna") not in valid_dna:
            errors.append(f"{sym}: invalid dna '{pos.get('dna')}'")

        if pos.get("timing") not in valid_timing:
            errors.append(f"{sym}: invalid timing '{pos.get('timing')}'")

        coeff = pos.get("timing_coeff")
        if coeff is not None:
            timing = pos.get("timing")
            if timing in valid_timing:
                tr = TimingRating(timing)
                lo, hi = tr.coefficient_range
                if not (lo <= coeff <= hi):
                    errors.append(
                        f"{sym}: timing_coeff {coeff} out of range [{lo}, {hi}] for {timing}"
                    )

        bucket = pos.get("investment_bucket", "")
        if bucket not in valid_buckets:
            errors.append(f"{sym}: invalid investment_bucket '{bucket}'")

    return errors


def save_portfolio_export(ratings: Dict[str, OPRMSRating], path: Path) -> None:
    """导出并保存 Portfolio Desk 格式文件"""
    data = export_for_portfolio(ratings)
    errors = validate_rating_data(data)
    if errors:
        logger.warning(f"导出数据有 {len(errors)} 个验证问题: {errors}")

    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    logger.info(f"Portfolio 导出: {data['count']} positions → {path}")
