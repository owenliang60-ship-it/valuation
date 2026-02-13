"""Tests for src/indicators/dv_acceleration.py"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.indicators.dv_acceleration import (
    compute_dv_acceleration,
    format_dv,
    scan_dv_acceleration,
)


def _make_df(n_days: int, close: float = 100.0, volume_pattern: list = None) -> pd.DataFrame:
    """
    构造合成量价 DataFrame

    Args:
        n_days: 天数
        close: 固定收盘价
        volume_pattern: 自定义 volume 列表，长度必须等于 n_days
    """
    dates = pd.bdate_range("2025-01-01", periods=n_days, freq="B").strftime("%Y-%m-%d").tolist()
    if volume_pattern is not None:
        assert len(volume_pattern) == n_days
        volumes = volume_pattern
    else:
        volumes = [1_000_000] * n_days
    return pd.DataFrame({
        "date": dates,
        "close": [close] * n_days,
        "volume": volumes,
    })


class TestComputeDvAcceleration:
    """compute_dv_acceleration 单股计算测试"""

    def test_basic_computation(self):
        """基本计算：固定 close=100, 均匀 volume → ratio=1.0"""
        df = _make_df(30, close=100.0)
        result = compute_dv_acceleration(df)
        assert result is not None
        assert result["ratio"] == 1.0
        assert result["dv_5d"] == 100.0 * 1_000_000
        assert result["dv_20d"] == 100.0 * 1_000_000
        assert result["signal"] is False

    def test_insufficient_data_returns_none(self):
        """数据不足 20 天时返回 None"""
        df = _make_df(19)
        result = compute_dv_acceleration(df)
        assert result is None

    def test_ratio_calculation_accuracy(self):
        """验证 ratio 准确性：最近 5 天 volume 翻倍"""
        # 前 15 天 volume=1M, 后 5 天 volume=2M
        volumes = [1_000_000] * 15 + [2_000_000] * 5
        df = _make_df(20, close=100.0, volume_pattern=volumes)
        result = compute_dv_acceleration(df)
        assert result is not None
        # dv_5d = 100 * 2M = 200M
        assert result["dv_5d"] == 200_000_000.0
        # dv_20d = 100 * mean(15×1M + 5×2M) = 100 * 1.25M = 125M
        expected_dv_20d = 100.0 * ((15 * 1_000_000 + 5 * 2_000_000) / 20)
        assert result["dv_20d"] == expected_dv_20d
        expected_ratio = round(200_000_000.0 / expected_dv_20d, 4)
        assert result["ratio"] == expected_ratio  # 1.6

    def test_signal_threshold_true(self):
        """ratio > 1.5 时 signal=True"""
        # 前 15 天 volume=1M, 后 5 天 volume=3M → ratio = 300M / 150M = 2.0
        volumes = [1_000_000] * 15 + [3_000_000] * 5
        df = _make_df(20, close=100.0, volume_pattern=volumes)
        result = compute_dv_acceleration(df)
        assert result is not None
        assert result["signal"] is True
        assert result["ratio"] > 1.5

    def test_signal_threshold_false(self):
        """ratio < 1.5 时 signal=False"""
        # 均匀 volume → ratio=1.0
        df = _make_df(20, close=100.0)
        result = compute_dv_acceleration(df)
        assert result is not None
        assert result["signal"] is False
        assert result["ratio"] <= 1.5


class TestScanDvAcceleration:
    """scan_dv_acceleration 批量扫描测试"""

    def test_multiple_stocks_sorted_by_ratio(self):
        """多只股票按 ratio 降序排列"""
        # FAST: 后 5 天 volume=4M → ratio=4M/1.75M ≈ 2.29
        fast_volumes = [1_000_000] * 15 + [4_000_000] * 5
        # SLOW: 均匀 → ratio=1.0
        slow_volumes = [1_000_000] * 20
        # MED: 后 5 天 volume=1.5M → ratio=1.5M/1.125M ≈ 1.33
        med_volumes = [1_000_000] * 15 + [1_500_000] * 5

        price_dict = {
            "FAST": _make_df(20, close=100.0, volume_pattern=fast_volumes),
            "SLOW": _make_df(20, close=100.0, volume_pattern=slow_volumes),
            "MED": _make_df(20, close=100.0, volume_pattern=med_volumes),
        }
        result = scan_dv_acceleration(price_dict)
        assert len(result) == 3
        assert result.iloc[0]["symbol"] == "FAST"
        assert result.iloc[1]["symbol"] == "MED"
        assert result.iloc[2]["symbol"] == "SLOW"
        # ratio 递减
        ratios = result["ratio"].tolist()
        assert ratios == sorted(ratios, reverse=True)

    def test_empty_input(self):
        """空输入返回空 DataFrame"""
        result = scan_dv_acceleration({})
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
        assert list(result.columns) == ["symbol", "dv_5d", "dv_20d", "ratio", "signal"]

    def test_all_below_threshold(self):
        """所有股票 ratio < threshold 时 signal 全部为 False"""
        uniform = [1_000_000] * 20
        price_dict = {
            "A": _make_df(20, close=100.0, volume_pattern=uniform),
            "B": _make_df(20, close=100.0, volume_pattern=uniform),
        }
        result = scan_dv_acceleration(price_dict, threshold=1.5)
        assert len(result) == 2
        assert result["signal"].sum() == 0


class TestFormatDv:
    """format_dv 格式化测试"""

    def test_billion_formatting(self):
        """>= 1e9 显示为 $X.XB"""
        assert format_dv(1_500_000_000) == "$1.5B"
        assert format_dv(1_000_000_000) == "$1.0B"
        assert format_dv(23_400_000_000) == "$23.4B"

    def test_million_formatting(self):
        """< 1e9 显示为 $XXXM"""
        assert format_dv(500_000_000) == "$500M"
        assert format_dv(50_000_000) == "$50M"
        assert format_dv(1_234_567) == "$1M"
