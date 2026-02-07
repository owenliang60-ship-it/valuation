"""
OPRMS 评级引擎 — 核心仓位计算

核心公式: 最终仓位 = 总资产 x DNA上限 x Timing系数
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from knowledge.oprms.models import (
    DNARating,
    TimingRating,
    OPRMSRating,
    PositionSize,
)

logger = logging.getLogger(__name__)


def calculate_position_size(
    total_capital: float,
    dna: DNARating,
    timing: TimingRating,
    timing_coeff: Optional[float] = None,
) -> PositionSize:
    """
    计算目标仓位

    Args:
        total_capital: 总资产 (USD)
        dna: 资产基因评级
        timing: 时机评级
        timing_coeff: 精确时机系数，默认使用评级中点

    Returns:
        PositionSize 计算结果

    Raises:
        ValueError: timing_coeff 超出评级允许范围
    """
    if timing_coeff is None:
        timing_coeff = timing.midpoint
    else:
        lo, hi = timing.coefficient_range
        if not (lo <= timing_coeff <= hi):
            raise ValueError(
                f"timing_coeff {timing_coeff} 超出 {timing.value} 级允许范围 [{lo}, {hi}]"
            )

    dna_cap = dna.max_position_pct
    target_pct = dna_cap * timing_coeff
    target_usd = total_capital * target_pct

    return PositionSize(
        symbol="",
        total_capital=total_capital,
        dna=dna,
        dna_cap_pct=dna_cap,
        timing=timing,
        timing_coeff=timing_coeff,
        target_position_pct=target_pct,
        target_position_usd=target_usd,
    )


def calculate_from_rating(
    total_capital: float,
    rating: OPRMSRating,
) -> PositionSize:
    """从 OPRMSRating 对象直接计算仓位"""
    result = calculate_position_size(
        total_capital=total_capital,
        dna=rating.dna,
        timing=rating.timing,
        timing_coeff=rating.timing_coeff,
    )
    result.symbol = rating.symbol
    return result


def generate_sensitivity_table(total_capital: float) -> Dict[str, Dict[str, dict]]:
    """
    生成 DNA x Timing 全组合灵敏度表

    Returns:
        {
            "S": {
                "S": {"pct": 25.0, "usd": 250000, "coeff": 1.25},
                "A": {"pct": 22.5, "usd": 225000, "coeff": 0.9},
                ...
            },
            ...
        }
    """
    table = {}
    for dna in DNARating:
        table[dna.value] = {}
        for timing in TimingRating:
            coeff = timing.midpoint
            pct = dna.max_position_pct * coeff
            table[dna.value][timing.value] = {
                "dna_label": dna.label,
                "timing_label": timing.label,
                "dna_cap_pct": round(dna.max_position_pct * 100, 1),
                "timing_coeff": coeff,
                "target_pct": round(pct * 100, 2),
                "target_usd": round(total_capital * pct, 2),
            }
    return table


def print_sensitivity_table(total_capital: float) -> None:
    """打印灵敏度表"""
    table = generate_sensitivity_table(total_capital)
    cap_str = f"${total_capital:,.0f}"

    print(f"\nOPRMS 灵敏度表 (总资产: {cap_str})")
    print("=" * 75)
    print(f"{'DNA \\\\ Timing':<15} {'S (千载难逢)':<16} {'A (趋势确立)':<16} {'B (正常波动)':<16} {'C (垃圾时间)':<16}")
    print("-" * 75)

    for dna in DNARating:
        row = f"{dna.value} {dna.label:<10}"
        for timing in TimingRating:
            cell = table[dna.value][timing.value]
            pct = cell["target_pct"]
            usd = cell["target_usd"]
            row += f" {pct:>5.1f}% ${usd:>10,.0f}"
        print(row)

    print("=" * 75)


def load_ratings(path: Path) -> Dict[str, OPRMSRating]:
    """
    从 JSON 文件加载评级数据

    Args:
        path: JSON 文件路径

    Returns:
        {symbol: OPRMSRating}
    """
    if not path.exists():
        logger.warning(f"评级文件不存在: {path}")
        return {}

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    ratings = {}
    for item in data.get("ratings", []):
        try:
            rating = OPRMSRating.from_dict(item)
            ratings[rating.symbol] = rating
        except (KeyError, ValueError) as e:
            logger.error(f"解析评级失败 {item.get('symbol', '?')}: {e}")

    logger.info(f"加载 {len(ratings)} 个评级 from {path}")
    return ratings


def save_ratings(ratings: Dict[str, OPRMSRating], path: Path) -> None:
    """
    保存评级数据到 JSON 文件

    Args:
        ratings: {symbol: OPRMSRating}
        path: 输出路径
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "version": "1.0",
        "count": len(ratings),
        "ratings": [r.to_dict() for r in ratings.values()],
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    logger.info(f"保存 {len(ratings)} 个评级 to {path}")
