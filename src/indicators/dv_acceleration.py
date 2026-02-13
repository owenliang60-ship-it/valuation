"""
Dollar Volume Acceleration 指标 (DV 加速度)

公式:
    DV = close × volume  (每日美元交易量)
    ratio = mean(DV[-5:]) / mean(DV[-20:])   # 5日均值 / 20日均值

信号:
    ratio > 1.5 → 近期 DV 加速（资金涌入）

用途:
    筛选近期美元交易量显著放大的股票，捕捉资金流入拐点。
"""
import logging
from typing import Dict, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def format_dv(value: float) -> str:
    """
    将美元交易量格式化为可读字符串

    >= 1e9 → "$X.XB"
    <  1e9 → "$XXXM"

    Args:
        value: 美元交易量

    Returns:
        格式化后的字符串
    """
    if value >= 1e9:
        return f"${value / 1e9:.1f}B"
    else:
        return f"${value / 1e6:.0f}M"


def compute_dv_acceleration(df: pd.DataFrame) -> Optional[dict]:
    """
    计算单只股票的 Dollar Volume 加速度

    算法:
        DV = close × volume
        ratio = mean(DV[-5:]) / mean(DV[-20:])
        signal = ratio > 1.5

    Args:
        df: 单只股票的量价 DataFrame，必须包含 [date, close, volume] 列，按日期正序排列

    Returns:
        {"symbol": str, "dv_5d": float, "dv_20d": float, "ratio": float, "signal": bool}
        数据不足时返回 None
    """
    if df is None or df.empty:
        logger.warning("输入 DataFrame 为空")
        return None

    required_cols = {"date", "close", "volume"}
    if not required_cols.issubset(df.columns):
        logger.warning(f"缺少必要列，需要 {required_cols}，实际 {set(df.columns)}")
        return None

    if len(df) < 20:
        logger.warning(f"数据不足，需要至少 20 个交易日，实际 {len(df)} 天")
        return None

    # 确保按日期正序
    df = df.sort_values("date").reset_index(drop=True)

    # 计算每日美元交易量
    dv = df["close"] * df["volume"]

    # 最近 5 日均值 / 最近 20 日均值
    dv_5d = dv.iloc[-5:].mean()
    dv_20d = dv.iloc[-20:].mean()

    if dv_20d == 0 or np.isnan(dv_20d):
        logger.warning("20日 DV 均值为 0，无法计算 ratio")
        return None

    ratio = dv_5d / dv_20d

    # 从 DataFrame 推断 symbol（如果有 symbol 列则取，否则为空）
    symbol = ""
    if "symbol" in df.columns:
        symbol = str(df["symbol"].iloc[0])

    return {
        "symbol": symbol,
        "dv_5d": float(dv_5d),
        "dv_20d": float(dv_20d),
        "ratio": float(round(ratio, 4)),
        "signal": bool(ratio > 1.5),
    }


def scan_dv_acceleration(
    price_dict: Dict[str, pd.DataFrame],
    threshold: float = 1.5,
) -> pd.DataFrame:
    """
    批量扫描多只股票的 DV 加速度

    Args:
        price_dict: {symbol: price_df} 字典，每个 df 包含 [date, close, volume]
        threshold: 信号阈值（默认 1.5，即 5 日均 DV 是 20 日均的 1.5 倍以上）

    Returns:
        包含 [symbol, dv_5d, dv_20d, ratio, signal] 的 DataFrame，按 ratio 降序排列
    """
    if not price_dict:
        logger.info("输入为空，返回空 DataFrame")
        return pd.DataFrame(columns=["symbol", "dv_5d", "dv_20d", "ratio", "signal"])

    results = []
    for symbol, df in price_dict.items():
        result = compute_dv_acceleration(df)
        if result is not None:
            result["symbol"] = symbol
            result["signal"] = bool(result["ratio"] > threshold)
            results.append(result)
        else:
            logger.debug(f"{symbol}: 数据不足，跳过")

    if not results:
        return pd.DataFrame(columns=["symbol", "dv_5d", "dv_20d", "ratio", "signal"])

    out = pd.DataFrame(results)[["symbol", "dv_5d", "dv_20d", "ratio", "signal"]]
    out = out.sort_values("ratio", ascending=False).reset_index(drop=True)

    # 日志输出概要
    fired = out[out["signal"]].shape[0]
    logger.info(f"DV 加速扫描完成: {len(out)} 只股票, {fired} 只触发信号 (threshold={threshold})")

    return out


if __name__ == "__main__":
    # 测试
    import sys
    sys.path.insert(0, str(__file__).rsplit("/src", 1)[0])
    from src.data import get_price_df

    print("测试 DV Acceleration 指标 (NVDA):")
    df = get_price_df("NVDA")
    if df is not None:
        df = df.sort_values("date")
        result = compute_dv_acceleration(df)
        if result:
            print(f"  5日均 DV: {format_dv(result['dv_5d'])}")
            print(f"  20日均 DV: {format_dv(result['dv_20d'])}")
            print(f"  Ratio: {result['ratio']:.2f}")
            print(f"  Signal: {result['signal']}")
