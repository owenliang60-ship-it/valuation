"""
RVOL Sustained 指标单元测试
"""
import sys
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.indicators.rvol_sustained import check_rvol_sustained, scan_rvol_sustained


# ---------------------------------------------------------------------------
# Helper: 构造已知 RVOL 值的 Series
# ---------------------------------------------------------------------------

def _make_rvol_series(values: list[float]) -> pd.Series:
    """用给定值直接构造 RVOL Series（模拟 calculate_rvol_series 的输出）"""
    return pd.Series(values, dtype=float)


# ===========================================================================
# TestCheckRvolSustained
# ===========================================================================

class TestCheckRvolSustained:
    """check_rvol_sustained 核心逻辑测试"""

    def test_sustained_5d(self):
        """最后 5+ 天 > 阈值 → sustained_5d"""
        # 前面一些正常值，最后 6 天全部 > 2.0
        series = _make_rvol_series([0.5, 1.0, 0.8, 2.5, 3.0, 2.1, 4.0, 2.3, 2.8])
        result = check_rvol_sustained(series, threshold=2.0)
        assert result["level"] == "sustained_5d"
        assert result["days"] == 6

    def test_sustained_3d(self):
        """最后 3-4 天 > 阈值 → sustained_3d"""
        series = _make_rvol_series([0.5, 1.0, 0.8, 1.5, 2.5, 3.0, 2.1])
        result = check_rvol_sustained(series, threshold=2.0)
        assert result["level"] == "sustained_3d"
        assert result["days"] == 3

    def test_single(self):
        """最后 1-2 天 > 阈值 → single"""
        # 只有最后 2 天 > 2.0
        series = _make_rvol_series([0.5, 1.0, 0.8, 1.5, 1.0, 2.5, 3.0])
        result = check_rvol_sustained(series, threshold=2.0)
        assert result["level"] == "single"
        assert result["days"] == 2

    def test_single_one_day(self):
        """只有最后 1 天 > 阈值 → single"""
        series = _make_rvol_series([0.5, 1.0, 0.8, 1.5, 1.0, 1.5, 3.0])
        result = check_rvol_sustained(series, threshold=2.0)
        assert result["level"] == "single"
        assert result["days"] == 1

    def test_none(self):
        """最后一天不超过阈值 → none"""
        series = _make_rvol_series([0.5, 1.0, 3.0, 2.5, 1.0])
        result = check_rvol_sustained(series, threshold=2.0)
        assert result["level"] == "none"
        assert result["days"] == 0
        assert result["values"] == []

    def test_values_are_most_recent_first(self):
        """values 列表应该最近的在前面"""
        # 最后 3 天: 2.1, 3.5, 4.2 (时间正序)
        series = _make_rvol_series([0.5, 1.0, 2.1, 3.5, 4.2])
        result = check_rvol_sustained(series, threshold=2.0)
        assert result["level"] == "sustained_3d"
        assert result["days"] == 3
        # 最近的排前面: 4.2, 3.5, 2.1
        assert result["values"] == [4.2, 3.5, 2.1]

    def test_custom_threshold(self):
        """自定义阈值应生效"""
        series = _make_rvol_series([0.5, 1.0, 3.5, 4.0, 3.8, 4.5, 5.0])
        # 阈值 4.0: 最后 3 天中 3.8 不超过 → 只有最后 2 天
        result = check_rvol_sustained(series, threshold=4.0)
        assert result["level"] == "single"
        assert result["days"] == 2
        assert result["values"] == [5.0, 4.5]

    def test_empty_series(self):
        """空序列 → none"""
        series = pd.Series([], dtype=float)
        result = check_rvol_sustained(series, threshold=2.0)
        assert result["level"] == "none"
        assert result["days"] == 0
        assert result["latest_rvol"] == 0.0

    def test_all_nan_series(self):
        """全 NaN 序列 → none"""
        series = pd.Series([float('nan'), float('nan'), float('nan')])
        result = check_rvol_sustained(series, threshold=2.0)
        assert result["level"] == "none"


# ===========================================================================
# TestScanRvolSustained
# ===========================================================================

def _make_price_df(volumes: list[float]) -> pd.DataFrame:
    """构造简易 price DataFrame，只含 volume 列"""
    return pd.DataFrame({
        "date": pd.date_range("2025-01-01", periods=len(volumes)),
        "close": [100.0] * len(volumes),
        "volume": volumes,
    })


class TestScanRvolSustained:
    """scan_rvol_sustained 批量扫描测试"""

    @patch("src.indicators.rvol_sustained.calculate_rvol_series")
    def test_filters_none_level(self, mock_calc):
        """level=none 的股票不出现在结果中"""
        # AAPL 有信号，MSFT 无信号
        def side_effect(volumes, lookback=120):
            if volumes.iloc[-1] == 999:  # AAPL
                return _make_rvol_series([0.5] * 120 + [2.5, 3.0, 2.8])
            else:  # MSFT
                return _make_rvol_series([0.5] * 123)

        mock_calc.side_effect = side_effect

        price_dict = {
            "AAPL": _make_price_df([100] * 120 + [999, 999, 999]),
            "MSFT": _make_price_df([100] * 123),
        }

        results = scan_rvol_sustained(price_dict, threshold=2.0, lookback=120)
        symbols = [r["symbol"] for r in results]
        assert "AAPL" in symbols
        assert "MSFT" not in symbols

    @patch("src.indicators.rvol_sustained.calculate_rvol_series")
    def test_sorting_order(self, mock_calc):
        """排序: sustained_5d > sustained_3d > single，同级按 latest_rvol 降序"""
        def side_effect(volumes, lookback=120):
            marker = volumes.iloc[-1]
            if marker == 1:  # single, latest_rvol=2.5
                return _make_rvol_series([0.5] * 122 + [2.5])
            elif marker == 2:  # sustained_3d, latest_rvol=3.0
                return _make_rvol_series([0.5] * 120 + [2.5, 2.8, 3.0])
            elif marker == 3:  # sustained_5d, latest_rvol=4.0
                return _make_rvol_series([0.5] * 118 + [2.1, 2.3, 2.5, 2.8, 4.0])
            elif marker == 4:  # sustained_5d, latest_rvol=5.0 (should be first)
                return _make_rvol_series([0.5] * 118 + [3.0, 2.5, 2.8, 3.5, 5.0])

        mock_calc.side_effect = side_effect

        price_dict = {
            "A_single": _make_price_df([100] * 122 + [1]),
            "B_3d": _make_price_df([100] * 120 + [100, 100, 2]),
            "C_5d": _make_price_df([100] * 118 + [100, 100, 100, 100, 3]),
            "D_5d_high": _make_price_df([100] * 118 + [100, 100, 100, 100, 4]),
        }

        results = scan_rvol_sustained(price_dict, threshold=2.0, lookback=120)
        levels = [(r["symbol"], r["level"]) for r in results]

        # sustained_5d 应该排在前面
        assert results[0]["level"] == "sustained_5d"
        assert results[1]["level"] == "sustained_5d"
        # 其中 latest_rvol 更高的排前面
        assert results[0]["latest_rvol"] > results[1]["latest_rvol"]
        # 然后 sustained_3d
        assert results[2]["level"] == "sustained_3d"
        # 最后 single
        assert results[3]["level"] == "single"

    def test_empty_input(self):
        """空输入 → 空结果"""
        results = scan_rvol_sustained({}, threshold=2.0)
        assert results == []

    @patch("src.indicators.rvol_sustained.calculate_rvol_series")
    def test_insufficient_data_stocks_skipped(self, mock_calc):
        """数据不足的股票被跳过（不调用 calculate_rvol_series）"""
        mock_calc.return_value = _make_rvol_series([2.5] * 5)

        price_dict = {
            "SHORT": _make_price_df([100] * 50),  # 只有 50 条，不够 121
        }

        results = scan_rvol_sustained(price_dict, threshold=2.0, lookback=120)
        assert results == []
        mock_calc.assert_not_called()
