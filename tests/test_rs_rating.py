"""
Tests for RS Rating 指标 (横截面动量排名)

Covers:
- Method B: Risk-Adjusted Z-Score 排名
- Method C: Clenow Regression 排名
- _clenow_momentum 辅助函数
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.indicators.rs_rating import (
    compute_rs_rating_b,
    compute_rs_rating_c,
    _clenow_momentum,
    MIN_TRADING_DAYS,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_price_dict(n_stocks=10, n_days=100, seed=42):
    """Create dict of {symbol: DataFrame} with synthetic price data."""
    np.random.seed(seed)
    dates = pd.date_range("2025-01-01", periods=n_days, freq="B")
    result = {}
    for i in range(n_stocks):
        sym = f"STK{i:02d}"
        drift = 0.001 * (i - n_stocks // 2)  # varying drift
        returns = np.random.randn(n_days) * 0.02 + drift
        prices = 100 * np.exp(np.cumsum(returns))
        df = pd.DataFrame({
            "date": dates,
            "close": prices,
            "volume": np.random.randint(1_000_000, 10_000_000, n_days),
        })
        result[sym] = df
    return result


def _make_trending_price(n_days=100, daily_drift=0.003, volatility=0.01, seed=99):
    """Create a single uptrending price DataFrame."""
    np.random.seed(seed)
    dates = pd.date_range("2025-01-01", periods=n_days, freq="B")
    returns = np.random.randn(n_days) * volatility + daily_drift
    prices = 100 * np.exp(np.cumsum(returns))
    return pd.DataFrame({"date": dates, "close": prices})


def _make_downtrending_price(n_days=100, daily_drift=-0.003, volatility=0.01, seed=99):
    """Create a single downtrending price DataFrame."""
    np.random.seed(seed)
    dates = pd.date_range("2025-01-01", periods=n_days, freq="B")
    returns = np.random.randn(n_days) * volatility + daily_drift
    prices = 100 * np.exp(np.cumsum(returns))
    return pd.DataFrame({"date": dates, "close": prices})


def _make_flat_price(n_days=100, volatility=0.001, seed=99):
    """Create a near-flat price DataFrame."""
    np.random.seed(seed)
    dates = pd.date_range("2025-01-01", periods=n_days, freq="B")
    returns = np.random.randn(n_days) * volatility
    prices = 100 * np.exp(np.cumsum(returns))
    return pd.DataFrame({"date": dates, "close": prices})


# ===========================================================================
# TestComputeRsRatingB
# ===========================================================================

class TestComputeRsRatingB:
    """Method B: Risk-Adjusted Z-Score 排名"""

    def test_basic_ranking(self):
        """多只股票应产生 0-99 之间的排名"""
        price_dict = _make_price_dict(n_stocks=10, n_days=100)
        df = compute_rs_rating_b(price_dict)

        assert len(df) == 10
        assert set(df.columns) == {
            "symbol", "ret_3m", "ret_1m", "ret_1w",
            "z_3m", "z_1m", "z_1w", "composite", "rs_rank",
        }
        assert df["rs_rank"].min() >= 0
        assert df["rs_rank"].max() <= 99

    def test_minimum_data_handling(self):
        """数据不足的股票应被跳过"""
        short_df = pd.DataFrame({
            "date": pd.date_range("2025-01-01", periods=30, freq="B"),
            "close": np.linspace(100, 110, 30),
        })
        price_dict = {"SHORT": short_df}
        df = compute_rs_rating_b(price_dict)
        assert len(df) == 0  # 被跳过

    def test_mixed_data_length(self):
        """混合长短数据，只有足够长的股票被纳入"""
        price_dict = _make_price_dict(n_stocks=5, n_days=100)
        # 加入一只数据不足的
        price_dict["TINY"] = pd.DataFrame({
            "date": pd.date_range("2025-01-01", periods=20, freq="B"),
            "close": np.linspace(100, 105, 20),
        })
        df = compute_rs_rating_b(price_dict)
        assert "TINY" not in df["symbol"].values
        assert len(df) == 5

    def test_winsorization(self):
        """Z-Score 应被 winsorize 到 ±3"""
        price_dict = _make_price_dict(n_stocks=20, n_days=100)
        df = compute_rs_rating_b(price_dict)

        assert df["z_3m"].min() >= -3.0
        assert df["z_3m"].max() <= 3.0
        assert df["z_1m"].min() >= -3.0
        assert df["z_1m"].max() <= 3.0
        assert df["z_1w"].min() >= -3.0
        assert df["z_1w"].max() <= 3.0

    def test_single_stock_edge_case(self):
        """单只股票：无法做横截面 Z-Score，应返回默认值"""
        price_dict = _make_price_dict(n_stocks=1, n_days=100, seed=42)
        # 只取第一只
        sym = list(price_dict.keys())[0]
        price_dict = {sym: price_dict[sym]}
        df = compute_rs_rating_b(price_dict)

        assert len(df) == 1
        assert df["z_3m"].iloc[0] == 0.0
        assert df["z_1m"].iloc[0] == 0.0
        assert df["z_1w"].iloc[0] == 0.0
        assert df["rs_rank"].iloc[0] == 50  # 单只居中

    def test_z_scores_reasonable(self):
        """Z-Score 应围绕 0 分布，标准差接近 1（大样本）"""
        price_dict = _make_price_dict(n_stocks=50, n_days=100, seed=123)
        df = compute_rs_rating_b(price_dict)

        # 50 只股票的 Z-Score 均值应接近 0
        assert abs(df["z_3m"].mean()) < 0.5
        assert abs(df["z_1m"].mean()) < 0.5
        assert abs(df["z_1w"].mean()) < 0.5

    def test_percentile_rank_range(self):
        """所有排名应在 [0, 99]"""
        price_dict = _make_price_dict(n_stocks=30, n_days=100)
        df = compute_rs_rating_b(price_dict)

        assert (df["rs_rank"] >= 0).all()
        assert (df["rs_rank"] <= 99).all()
        assert df["rs_rank"].dtype in [np.int64, np.int32, int]

    def test_strong_uptrend_ranks_high(self):
        """强上升趋势的股票应排名靠前"""
        price_dict = _make_price_dict(n_stocks=10, n_days=100, seed=42)
        # 替换一只为强上升趋势
        strong = _make_trending_price(n_days=100, daily_drift=0.008, volatility=0.005, seed=7)
        price_dict["BULL"] = strong

        df = compute_rs_rating_b(price_dict)
        bull_rank = df.loc[df["symbol"] == "BULL", "rs_rank"].iloc[0]
        median_rank = df["rs_rank"].median()
        assert bull_rank > median_rank


# ===========================================================================
# TestComputeRsRatingC
# ===========================================================================

class TestComputeRsRatingC:
    """Method C: Clenow Regression 排名"""

    def test_basic_ranking(self):
        """多只股票应产生 0-99 之间的排名"""
        price_dict = _make_price_dict(n_stocks=10, n_days=100)
        df = compute_rs_rating_c(price_dict)

        assert len(df) == 10
        assert set(df.columns) == {
            "symbol", "clenow_63d", "clenow_21d", "clenow_10d",
            "composite", "rs_rank",
        }
        assert df["rs_rank"].min() >= 0
        assert df["rs_rank"].max() <= 99

    def test_minimum_data(self):
        """数据不足的股票应被跳过"""
        short_df = pd.DataFrame({
            "date": pd.date_range("2025-01-01", periods=30, freq="B"),
            "close": np.linspace(100, 110, 30),
        })
        price_dict = {"SHORT": short_df}
        df = compute_rs_rating_c(price_dict)
        assert len(df) == 0

    def test_clenow_score_positive_for_uptrend(self):
        """上升趋势的 Clenow 分数应为正"""
        price_dict = _make_price_dict(n_stocks=5, n_days=100, seed=42)
        # 替换一只为平稳上升趋势（低噪声）
        strong = _make_trending_price(n_days=100, daily_drift=0.005, volatility=0.003, seed=10)
        price_dict["TREND"] = strong

        df = compute_rs_rating_c(price_dict)
        trend_row = df.loc[df["symbol"] == "TREND"].iloc[0]
        assert trend_row["clenow_63d"] > 0
        assert trend_row["clenow_21d"] > 0
        assert trend_row["clenow_10d"] > 0

    def test_r_squared_effect(self):
        """高 R² 的趋势: R² 接近 1 应放大分数，R² 低则压缩

        直接验证 _clenow_momentum 对同样斜率、不同 R² 的反应。
        构造确定性数据：纯线性 vs 加锯齿噪声。
        """
        n = 80
        # 纯线性上涨: log(price) 完美线性 → R² ≈ 1.0
        smooth_prices = pd.Series(100 * np.exp(np.linspace(0, 0.5, n)))

        # 加大锯齿噪声: 同样终点，但中途大幅震荡 → R² << 1
        base = np.linspace(0, 0.5, n)
        noise = np.zeros(n)
        for i in range(n):
            noise[i] = 0.15 * (1 if i % 2 == 0 else -1)
        noisy_prices = pd.Series(100 * np.exp(base + noise))

        smooth_score = _clenow_momentum(smooth_prices, window=63)
        noisy_score = _clenow_momentum(noisy_prices, window=63)

        # 两者有相同的起点和终点斜率，但 R² 差异巨大
        assert smooth_score > 0
        assert smooth_score > noisy_score

    def test_empty_dict(self):
        """空字典应返回空 DataFrame，列名正确"""
        df = compute_rs_rating_c({})
        assert len(df) == 0
        assert "rs_rank" in df.columns
        assert "composite" in df.columns


# ===========================================================================
# TestClenowMomentum
# ===========================================================================

class TestClenowMomentum:
    """_clenow_momentum 辅助函数"""

    def test_uptrend_positive_score(self):
        """稳定上升趋势应产生正分数"""
        np.random.seed(42)
        prices = pd.Series(100 * np.exp(np.cumsum(
            np.random.randn(80) * 0.005 + 0.003
        )))
        score = _clenow_momentum(prices, window=63)
        assert score > 0

    def test_downtrend_negative_score(self):
        """稳定下降趋势应产生负分数"""
        np.random.seed(42)
        prices = pd.Series(100 * np.exp(np.cumsum(
            np.random.randn(80) * 0.005 - 0.005
        )))
        score = _clenow_momentum(prices, window=63)
        assert score < 0

    def test_flat_near_zero(self):
        """近似平坦应产生接近 0 的分数"""
        np.random.seed(42)
        prices = pd.Series(100 * np.exp(np.cumsum(
            np.random.randn(80) * 0.001
        )))
        score = _clenow_momentum(prices, window=63)
        assert abs(score) < 0.5  # 接近 0

    def test_insufficient_data(self):
        """数据不足应返回 0.0"""
        prices = pd.Series([100, 101, 102])
        score = _clenow_momentum(prices, window=63)
        assert score == 0.0

    def test_zero_prices_returns_zero(self):
        """包含零价格应返回 0.0（log 不可计算）"""
        prices = pd.Series([0.0] * 70)
        score = _clenow_momentum(prices, window=63)
        assert score == 0.0
