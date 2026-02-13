"""
RVOL Sustained 指标 — 持续放量检测

基于 RVOL (Relative Volume) 的持续性分析：
- 复用 calculate_rvol_series() 计算每日 RVOL
- 检测最近 N 天是否连续 > 阈值（默认 2σ）
- 三个等级: single (1-2天) / sustained_3d (3-4天) / sustained_5d (5+天)

用途:
    持续放量 ≠ 单日异常，通常代表机构持续建仓/出货，
    是趋势强度的关键确认信号。
"""
import logging
from typing import Dict, List, Optional

import pandas as pd

from src.indicators.rvol import calculate_rvol_series

logger = logging.getLogger(__name__)


def check_rvol_sustained(
    rvol_series: pd.Series,
    threshold: float = 2.0
) -> dict:
    """
    检测 RVOL 序列的持续放量等级

    从序列末尾向前检查，统计连续超过阈值的天数。

    Args:
        rvol_series: RVOL 序列（已按时间正序排列，由 calculate_rvol_series 生成）
        threshold: 放量阈值，默认 2.0（即 2σ）

    Returns:
        {
            "level": "sustained_5d" | "sustained_3d" | "single" | "none",
            "days": int,          # 连续超过阈值的天数
            "values": list[float], # 这些天的 RVOL 值（最近的排前面）
            "latest_rvol": float   # 最新一天的 RVOL
        }
    """
    result = {
        "level": "none",
        "days": 0,
        "values": [],
        "latest_rvol": 0.0
    }

    # 去掉 NaN 值
    valid = rvol_series.dropna()
    if len(valid) == 0:
        return result

    result["latest_rvol"] = float(valid.iloc[-1])

    # 从末尾向前数连续超过阈值的天数
    consecutive = 0
    values: List[float] = []
    for i in range(len(valid) - 1, -1, -1):
        val = valid.iloc[i]
        if val > threshold:
            consecutive += 1
            values.append(float(val))
        else:
            break

    result["days"] = consecutive
    result["values"] = values  # 已经是最近的排前面

    # 判定等级
    if consecutive >= 5:
        result["level"] = "sustained_5d"
    elif consecutive >= 3:
        result["level"] = "sustained_3d"
    elif consecutive >= 1:
        result["level"] = "single"
    else:
        result["level"] = "none"

    return result


# 等级排序权重，用于 scan 结果排序
_LEVEL_ORDER = {
    "sustained_5d": 0,
    "sustained_3d": 1,
    "single": 2,
    "none": 3,
}


def scan_rvol_sustained(
    price_dict: Dict[str, pd.DataFrame],
    threshold: float = 2.0,
    lookback: int = 120
) -> List[dict]:
    """
    批量扫描持续放量股票

    Args:
        price_dict: {symbol: price_df} 字典，每个 df 包含 [date, close, volume]，按 date 正序
        threshold: 放量阈值，默认 2.0σ
        lookback: RVOL 计算的回看周期（天），默认 120

    Returns:
        list of dict，每个元素:
        {
            "symbol": str,
            "level": str,
            "days": int,
            "values": list[float],
            "latest_rvol": float
        }
        仅包含 level != "none" 的股票。
        排序: sustained_5d > sustained_3d > single，同等级按 latest_rvol 降序。
    """
    results: List[dict] = []

    for symbol, df in price_dict.items():
        if df is None or df.empty:
            logger.debug(f"{symbol}: 数据为空，跳过")
            continue

        if 'volume' not in df.columns:
            logger.debug(f"{symbol}: 缺少 volume 列，跳过")
            continue

        volumes = df['volume']

        # calculate_rvol_series 需要至少 lookback+1 条数据
        if len(volumes) < lookback + 1:
            logger.debug(f"{symbol}: 数据不足 ({len(volumes)}/{lookback + 1})，跳过")
            continue

        try:
            rvol_series = calculate_rvol_series(volumes, lookback=lookback)
            signal = check_rvol_sustained(rvol_series, threshold=threshold)

            if signal["level"] != "none":
                results.append({
                    "symbol": symbol,
                    "level": signal["level"],
                    "days": signal["days"],
                    "values": signal["values"],
                    "latest_rvol": signal["latest_rvol"],
                })
        except Exception as e:
            logger.warning(f"{symbol}: RVOL 计算异常 — {e}")
            continue

    # 排序: 等级优先（5d > 3d > single），同等级按 latest_rvol 降序
    results.sort(key=lambda x: (_LEVEL_ORDER[x["level"]], -x["latest_rvol"]))

    logger.info(f"RVOL Sustained 扫描完成: {len(results)}/{len(price_dict)} 只触发信号")
    return results
