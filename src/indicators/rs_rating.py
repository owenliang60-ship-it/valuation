"""
RS Rating 指标 (Relative Strength Rating - 横截面动量排名)

两种计算方法:

Method B — Risk-Adjusted Z-Score
    多周期收益率 (3m/1m/1w)，经波动率调整后做横截面 Z-Score，
    加权合成后转换为 0-99 百分位排名。
    跳过最近 5 个交易日以规避短期反转效应。

Method C — Clenow Exponential Regression
    对数价格线性回归，斜率年化后乘以 R²，
    三窗口 (63d/21d/10d) 加权合成后转换为 0-99 百分位排名。

参考:
    - Andreas Clenow, "Stocks on the Move"
    - Jegadeesh & Titman (1993), momentum anomaly
"""
import logging
from typing import Dict

import numpy as np
import pandas as pd
from scipy.stats import rankdata, zscore as scipy_zscore, linregress

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------
MIN_TRADING_DAYS = 70  # 两种方法共用的最小数据要求


# ---------------------------------------------------------------------------
# Method B: Risk-Adjusted Z-Score
# ---------------------------------------------------------------------------

def compute_rs_rating_b(price_dict: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Method B — 风险调整 Z-Score 横截面动量排名

    对每只股票计算三个时间窗口的收益率（跳过最近 5 个交易日），
    3m 和 1m 经年化波动率调整，横截面 Z-Score (winsorize ±3)，
    加权合成后转换为 0-99 百分位排名。

    Args:
        price_dict: {symbol: price_df} 字典
            每个 df 至少包含 [date, close] 列，按日期正序排列

    Returns:
        DataFrame，列: [symbol, ret_3m, ret_1m, ret_1w,
                        z_3m, z_1m, z_1w, composite, rs_rank]
        数据不足的股票不会出现在结果中
    """
    records = []

    for symbol, df in price_dict.items():
        if df is None or len(df) < MIN_TRADING_DAYS:
            logger.debug(f"{symbol}: 数据不足 ({len(df) if df is not None else 0} < {MIN_TRADING_DAYS})")
            continue

        close = df["close"].values
        n = len(close)

        # 跳过最近 5 个交易日 (short-term reversal avoidance)
        # 索引约定: close[n-1] = 最新, close[n-6] = 5 天前
        if n < 65:  # 需要至少到 n-64
            logger.debug(f"{symbol}: 数据不足以计算 3m 收益率")
            continue

        # --- 收益率 ---
        ret_3m = close[n - 6] / close[n - 64] - 1   # [-63, -5]
        ret_1m = close[n - 6] / close[n - 22] - 1   # [-21, -5]
        ret_1w = close[n - 6] / close[n - 11] - 1   # [-10, -5]

        # --- 风险调整 (年化波动率) ---
        daily_returns = np.diff(close) / close[:-1]

        vol_3m = np.std(daily_returns[n - 64:n - 5], ddof=1) * np.sqrt(252)
        vol_1m = np.std(daily_returns[n - 22:n - 5], ddof=1) * np.sqrt(252)

        ra_3m = ret_3m / vol_3m if vol_3m > 1e-10 else 0.0
        ra_1m = ret_1m / vol_1m if vol_1m > 1e-10 else 0.0
        # 1w 太短，不做风险调整
        ra_1w = ret_1w

        records.append({
            "symbol": symbol,
            "ret_3m": ret_3m,
            "ret_1m": ret_1m,
            "ret_1w": ret_1w,
            "_ra_3m": ra_3m,
            "_ra_1m": ra_1m,
            "_ra_1w": ra_1w,
        })

    if not records:
        return pd.DataFrame(columns=[
            "symbol", "ret_3m", "ret_1m", "ret_1w",
            "z_3m", "z_1m", "z_1w", "composite", "rs_rank",
        ])

    result_df = pd.DataFrame(records)

    # --- 横截面 Z-Score ---
    if len(result_df) == 1:
        # 单只股票无法做横截面 Z-Score，默认 Z=0
        result_df["z_3m"] = 0.0
        result_df["z_1m"] = 0.0
        result_df["z_1w"] = 0.0
    else:
        result_df["z_3m"] = np.clip(scipy_zscore(result_df["_ra_3m"], ddof=1), -3, 3)
        result_df["z_1m"] = np.clip(scipy_zscore(result_df["_ra_1m"], ddof=1), -3, 3)
        result_df["z_1w"] = np.clip(scipy_zscore(result_df["_ra_1w"], ddof=1), -3, 3)

    # --- 加权合成 ---
    result_df["composite"] = (
        0.40 * result_df["z_3m"]
        + 0.35 * result_df["z_1m"]
        + 0.25 * result_df["z_1w"]
    )

    # --- 百分位排名 0-99 ---
    if len(result_df) == 1:
        result_df["rs_rank"] = 50  # 单只股票居中
    else:
        pct = rankdata(result_df["composite"], method="average") / len(result_df)
        result_df["rs_rank"] = np.clip(np.floor(pct * 100).astype(int), 0, 99)

    # 清理临时列，整理输出
    result_df = result_df[[
        "symbol", "ret_3m", "ret_1m", "ret_1w",
        "z_3m", "z_1m", "z_1w", "composite", "rs_rank",
    ]].reset_index(drop=True)

    return result_df


# ---------------------------------------------------------------------------
# Method C: Clenow Exponential Regression
# ---------------------------------------------------------------------------

def _clenow_momentum(prices: pd.Series, window: int) -> float:
    """
    计算单个窗口的 Clenow 动量分数

    对最近 window 根 K 线的对数价格做线性回归，
    将斜率年化后乘以 R²，得到质量调整后的年化收益率。

    Args:
        prices: 收盘价序列（至少 window 个数据点）
        window: 回看窗口长度

    Returns:
        Clenow 分数 = annualized_return * R²
        如果数据不足或回归失败，返回 0.0
    """
    if len(prices) < window:
        return 0.0

    tail = prices.iloc[-window:].values
    if np.any(tail <= 0):
        return 0.0

    log_prices = np.log(tail)
    x = np.arange(window)

    try:
        slope, _intercept, r_value, _p_value, _std_err = linregress(x, log_prices)
    except Exception:
        return 0.0

    r_squared = r_value ** 2
    annualized = (np.exp(slope) ** 252) - 1
    return annualized * r_squared


def compute_rs_rating_c(price_dict: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Method C — Clenow 回归动量排名

    对每只股票在三个窗口 (63d/21d/10d) 上计算 Clenow 动量分数，
    加权合成后转换为 0-99 百分位排名。

    Args:
        price_dict: {symbol: price_df} 字典
            每个 df 至少包含 [date, close] 列，按日期正序排列

    Returns:
        DataFrame，列: [symbol, clenow_63d, clenow_21d, clenow_10d,
                        composite, rs_rank]
        数据不足的股票不会出现在结果中
    """
    records = []

    for symbol, df in price_dict.items():
        if df is None or len(df) < MIN_TRADING_DAYS:
            logger.debug(f"{symbol}: 数据不足 ({len(df) if df is not None else 0} < {MIN_TRADING_DAYS})")
            continue

        close = df["close"]

        c63 = _clenow_momentum(close, 63)
        c21 = _clenow_momentum(close, 21)
        c10 = _clenow_momentum(close, 10)

        records.append({
            "symbol": symbol,
            "clenow_63d": c63,
            "clenow_21d": c21,
            "clenow_10d": c10,
        })

    if not records:
        return pd.DataFrame(columns=[
            "symbol", "clenow_63d", "clenow_21d", "clenow_10d",
            "composite", "rs_rank",
        ])

    result_df = pd.DataFrame(records)

    # --- 加权合成 ---
    result_df["composite"] = (
        0.50 * result_df["clenow_63d"]
        + 0.30 * result_df["clenow_21d"]
        + 0.20 * result_df["clenow_10d"]
    )

    # --- 百分位排名 0-99 ---
    if len(result_df) == 1:
        result_df["rs_rank"] = 50  # 单只股票居中
    else:
        pct = rankdata(result_df["composite"], method="average") / len(result_df)
        result_df["rs_rank"] = np.clip(np.floor(pct * 100).astype(int), 0, 99)

    result_df = result_df[[
        "symbol", "clenow_63d", "clenow_21d", "clenow_10d",
        "composite", "rs_rank",
    ]].reset_index(drop=True)

    return result_df


# ---------------------------------------------------------------------------
# Main (手动测试)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(__file__).rsplit("/src", 1)[0])
    from src.data import get_price_df
    from config.settings import STOCK_POOL

    print("测试 RS Rating 指标:")

    # 加载股票池价格数据
    price_dict = {}
    for sym in STOCK_POOL[:20]:  # 测试前 20 只
        df = get_price_df(sym)
        if df is not None:
            df = df.sort_values("date").reset_index(drop=True)
            price_dict[sym] = df

    if price_dict:
        print(f"\n  加载了 {len(price_dict)} 只股票")

        print("\n  === Method B: Risk-Adjusted Z-Score ===")
        df_b = compute_rs_rating_b(price_dict)
        print(df_b.sort_values("rs_rank", ascending=False).head(10).to_string(index=False))

        print("\n  === Method C: Clenow Regression ===")
        df_c = compute_rs_rating_c(price_dict)
        print(df_c.sort_values("rs_rank", ascending=False).head(10).to_string(index=False))
    else:
        print("  没有可用的价格数据")
