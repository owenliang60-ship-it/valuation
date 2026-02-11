"""
PMARP 指标 (Price Moving Average Ratio Percentile)
复用自 Quant/scanners/binance_pmarp_scanner.py

公式:
    PMAR = Price / EMA(Price, period)
    PMARP = Percentile(PMAR, lookback)

信号:
    PMARP 上穿 98% → 强势追涨信号
    PMARP 下穿 2% → 极度超卖

参考: quant-development skill
"""
import pandas as pd
import numpy as np
from typing import Optional, Dict, Tuple


def calculate_pmarp(
    prices: pd.Series,
    ema_period: int = 20,
    lookback: int = 150
) -> pd.Series:
    """
    计算 PMARP (Price Moving Average Ratio Percentile)

    PMAR = Price / EMA(Price, period)
    PMARP = 在过去 lookback 根 K 线中，有多少比例的 PMAR <= 当前 PMAR

    结果解读:
    - PMARP = 99% → 当前价格相对 EMA 处于历史最高 1% 区域（极强）
    - PMARP = 1% → 当前价格相对 EMA 处于历史最低 1% 区域（极弱）

    Args:
        prices: 收盘价序列 (必须按时间正序，最早在前)
        ema_period: EMA 周期 (默认 20)
        lookback: 回看周期 (默认 150)

    Returns:
        PMARP 序列 (0-100)
    """
    if len(prices) < lookback + ema_period:
        return pd.Series(index=prices.index, dtype=float)

    # 重置索引，确保 iloc 顺序与传入顺序一致（调用方已按日期正序排列）
    prices = prices.reset_index(drop=True)

    # 计算 EMA
    ema = prices.ewm(span=ema_period, adjust=False).mean()

    # 计算 PMAR
    pmar = prices / ema

    # 计算 PMARP (使用向量化方法提高效率)
    pmarp = pd.Series(index=pmar.index, dtype=float)

    for i in range(lookback, len(pmar)):
        current = pmar.iloc[i]
        historical = pmar.iloc[i - lookback:i]

        # 正确公式: count(values <= current) / total * 100
        # PMARP 高 = 当前处于历史高位
        count_le = (historical <= current).sum()
        pmarp.iloc[i] = count_le / lookback * 100

    return pmarp


def check_pmarp_crossover(
    pmarp: pd.Series,
    threshold: float = 98.0,
    direction: str = "up"
) -> bool:
    """
    检测 PMARP 是否发生穿越

    Args:
        pmarp: PMARP 序列
        threshold: 阈值 (默认 98)
        direction: "up" 上穿 / "down" 下穿

    Returns:
        是否触发信号
    """
    valid_pmarp = pmarp.dropna()
    if len(valid_pmarp) < 2:
        return False

    prev_value = valid_pmarp.iloc[-2]
    curr_value = valid_pmarp.iloc[-1]

    if direction == "up":
        # 上穿: 前一天 < threshold AND 当天 >= threshold
        return prev_value < threshold and curr_value >= threshold
    else:
        # 下穿: 前一天 > threshold AND 当天 <= threshold
        return prev_value > threshold and curr_value <= threshold


def analyze_pmarp(df: pd.DataFrame, ema_period: int = 20, lookback: int = 150) -> Dict:
    """
    分析单只股票的 PMARP

    Args:
        df: 量价数据 DataFrame，必须包含 'close' 列，按时间正序
        ema_period: EMA 周期
        lookback: 回看周期

    Returns:
        {
            "current": 当前 PMARP 值,
            "previous": 前一天 PMARP 值,
            "signal": "bullish_breakout" / "overbought" / "oversold" / "neutral",
            "crossover_98": 是否上穿 98%,
            "crossover_2": 是否下穿 2%,
            "description": 描述文字
        }
    """
    result = {
        "current": None,
        "previous": None,
        "signal": "neutral",
        "crossover_98": False,
        "crossover_2": False,
        "description": ""
    }

    if df is None or df.empty or 'close' not in df.columns:
        result["description"] = "数据不足"
        return result

    # 确保按时间正序（日期小的在前）
    if 'date' in df.columns:
        df = df.sort_values('date')

    prices = df['close']
    pmarp = calculate_pmarp(prices, ema_period, lookback)

    valid_pmarp = pmarp.dropna()
    if len(valid_pmarp) < 2:
        result["description"] = "PMARP 计算数据不足"
        return result

    result["current"] = round(valid_pmarp.iloc[-1], 2)
    result["previous"] = round(valid_pmarp.iloc[-2], 2)

    # 检测信号
    result["crossover_98"] = check_pmarp_crossover(pmarp, 98, "up")
    result["crossover_2"] = check_pmarp_crossover(pmarp, 2, "down")

    current = result["current"]

    if result["crossover_98"]:
        result["signal"] = "bullish_breakout"
        result["description"] = f"PMARP 上穿 98% ({result['previous']:.1f}→{current:.1f})，强势追涨信号"
    elif result["crossover_2"]:
        result["signal"] = "oversold_bounce"
        result["description"] = f"PMARP 下穿 2% ({result['previous']:.1f}→{current:.1f})，极度超卖"
    elif current >= 95:
        result["signal"] = "overbought"
        result["description"] = f"PMARP={current:.1f}%，处于强势区域"
    elif current <= 5:
        result["signal"] = "oversold"
        result["description"] = f"PMARP={current:.1f}%，处于弱势区域"
    else:
        result["signal"] = "neutral"
        result["description"] = f"PMARP={current:.1f}%，中性区域"

    return result


if __name__ == "__main__":
    # 测试
    import sys
    sys.path.insert(0, str(__file__).rsplit("/src", 1)[0])
    from src.data import get_price_df

    print("测试 PMARP 指标 (NVDA):")
    df = get_price_df("NVDA")
    if df is not None:
        # 按日期正序排列
        df = df.sort_values('date')
        result = analyze_pmarp(df)
        print(f"  当前 PMARP: {result['current']}")
        print(f"  信号: {result['signal']}")
        print(f"  描述: {result['description']}")
