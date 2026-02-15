"""
Tests for pool_manager.cleanup_stale_data()
验证：删除过期 CSV、清理基本面 JSON、保留 benchmark
"""
import json
import pytest
from pathlib import Path
from unittest.mock import patch


@pytest.fixture
def setup_dirs(tmp_path):
    """创建模拟的 price/ 和 fundamental/ 目录结构"""
    price_dir = tmp_path / "price"
    price_dir.mkdir()
    fundamental_dir = tmp_path / "fundamental"
    fundamental_dir.mkdir()
    pool_dir = tmp_path / "pool"
    pool_dir.mkdir()
    return tmp_path, price_dir, fundamental_dir, pool_dir


def _create_csv(price_dir, symbol):
    (price_dir / f"{symbol}.csv").write_text("date,open,high,low,close,volume\n")


def _create_fundamental(fundamental_dir, symbols_data):
    """创建基本面 JSON，symbols_data 是 {symbol: data} 的 dict"""
    for fname in ["profiles", "ratios", "income", "balance_sheet", "cash_flow"]:
        with open(fundamental_dir / f"{fname}.json", "w") as f:
            json.dump(symbols_data, f)


class TestCleanupStaleData:

    def test_deletes_stale_csvs(self, setup_dirs):
        """删除不在池中的过期 CSV"""
        tmp_path, price_dir, fundamental_dir, pool_dir = setup_dirs

        # 创建 CSV: AAPL(池内), MSFT(池内), DEAD(已退出), SPY(benchmark)
        for sym in ["AAPL", "MSFT", "DEAD", "SPY"]:
            _create_csv(price_dir, sym)

        with patch("src.data.pool_manager.PRICE_DIR", price_dir), \
             patch("src.data.pool_manager.FUNDAMENTAL_DIR", fundamental_dir), \
             patch("src.data.pool_manager.BENCHMARK_SYMBOLS", ["SPY", "QQQ"]):
            from src.data.pool_manager import cleanup_stale_data
            stats = cleanup_stale_data(["AAPL", "MSFT"])

        assert stats["csv_deleted"] == 1
        assert (price_dir / "AAPL.csv").exists()
        assert (price_dir / "MSFT.csv").exists()
        assert (price_dir / "SPY.csv").exists()  # benchmark 保留
        assert not (price_dir / "DEAD.csv").exists()  # 已退出，已删除

    def test_preserves_benchmark_csvs(self, setup_dirs):
        """即使池中没有 SPY/QQQ，benchmark CSV 也保留"""
        tmp_path, price_dir, fundamental_dir, pool_dir = setup_dirs

        for sym in ["AAPL", "SPY", "QQQ"]:
            _create_csv(price_dir, sym)

        with patch("src.data.pool_manager.PRICE_DIR", price_dir), \
             patch("src.data.pool_manager.FUNDAMENTAL_DIR", fundamental_dir), \
             patch("src.data.pool_manager.BENCHMARK_SYMBOLS", ["SPY", "QQQ"]):
            from src.data.pool_manager import cleanup_stale_data
            stats = cleanup_stale_data(["AAPL"])

        assert stats["csv_deleted"] == 0
        assert (price_dir / "SPY.csv").exists()
        assert (price_dir / "QQQ.csv").exists()

    def test_cleans_fundamental_json(self, setup_dirs):
        """清理基本面 JSON 中已退出股票的条目 (比例 <30% 才不触发熔断)"""
        tmp_path, price_dir, fundamental_dir, pool_dir = setup_dirs

        # 10 个有效 + 2 个过期 → 删除比例 ~17%，低于 30% 阈值
        keep_symbols = [f"SYM{i}" for i in range(10)]
        data = {s: {"name": f"Company {s}"} for s in keep_symbols}
        data["DEAD"] = {"name": "Dead Co"}
        data["GONE"] = {"name": "Gone Inc"}
        _create_fundamental(fundamental_dir, data)

        with patch("src.data.pool_manager.PRICE_DIR", price_dir), \
             patch("src.data.pool_manager.FUNDAMENTAL_DIR", fundamental_dir), \
             patch("src.data.pool_manager.BENCHMARK_SYMBOLS", ["SPY", "QQQ"]), \
             patch("src.data.data_guardian.snapshot", return_value=None):
            from src.data.pool_manager import cleanup_stale_data
            stats = cleanup_stale_data(keep_symbols)

        # 每个 JSON 文件清理 2 条 (DEAD + GONE)，共 5 个文件
        assert stats["fundamental_cleaned"] == 10

        # 验证 JSON 内容
        for fname in ["profiles", "ratios", "income", "balance_sheet", "cash_flow"]:
            with open(fundamental_dir / f"{fname}.json") as f:
                cleaned = json.load(f)
            assert keep_symbols[0] in cleaned
            assert "DEAD" not in cleaned
            assert "GONE" not in cleaned

    def test_no_op_when_clean(self, setup_dirs):
        """池和数据完全一致时，不做任何操作"""
        tmp_path, price_dir, fundamental_dir, pool_dir = setup_dirs

        for sym in ["AAPL", "MSFT", "SPY"]:
            _create_csv(price_dir, sym)
        _create_fundamental(fundamental_dir, {"AAPL": {}, "MSFT": {}})

        with patch("src.data.pool_manager.PRICE_DIR", price_dir), \
             patch("src.data.pool_manager.FUNDAMENTAL_DIR", fundamental_dir), \
             patch("src.data.pool_manager.BENCHMARK_SYMBOLS", ["SPY"]):
            from src.data.pool_manager import cleanup_stale_data
            stats = cleanup_stale_data(["AAPL", "MSFT"])

        assert stats["csv_deleted"] == 0
        assert stats["fundamental_cleaned"] == 0

    def test_handles_missing_dirs(self, setup_dirs):
        """price/ 或 fundamental/ 不存在时不报错"""
        tmp_path, price_dir, fundamental_dir, pool_dir = setup_dirs

        missing_price = tmp_path / "nonexistent_price"
        missing_fund = tmp_path / "nonexistent_fund"

        with patch("src.data.pool_manager.PRICE_DIR", missing_price), \
             patch("src.data.pool_manager.FUNDAMENTAL_DIR", missing_fund), \
             patch("src.data.pool_manager.BENCHMARK_SYMBOLS", ["SPY"]):
            from src.data.pool_manager import cleanup_stale_data
            stats = cleanup_stale_data(["AAPL"])

        assert stats["csv_deleted"] == 0
        assert stats["fundamental_cleaned"] == 0

    def test_handles_corrupt_json(self, setup_dirs):
        """损坏的 JSON 文件跳过不报错"""
        tmp_path, price_dir, fundamental_dir, pool_dir = setup_dirs

        (fundamental_dir / "profiles.json").write_text("not valid json{{{")
        _create_fundamental(fundamental_dir, {"AAPL": {}})  # 覆盖 profiles 以外的

        with patch("src.data.pool_manager.PRICE_DIR", price_dir), \
             patch("src.data.pool_manager.FUNDAMENTAL_DIR", fundamental_dir), \
             patch("src.data.pool_manager.BENCHMARK_SYMBOLS", ["SPY"]):
            from src.data.pool_manager import cleanup_stale_data
            # 不应该抛出异常
            stats = cleanup_stale_data(["AAPL"])

        assert stats["csv_deleted"] == 0

    def test_safety_fuse_aborts_on_high_csv_ratio(self, setup_dirs):
        """删除超过 30% CSV 时触发熔断"""
        tmp_path, price_dir, fundamental_dir, pool_dir = setup_dirs

        # 创建 10 个 CSV
        for i in range(10):
            _create_csv(price_dir, f"SYM{i}")

        # 只保留 2 个 → 要删 8 个 (80%)
        with patch("src.data.pool_manager.PRICE_DIR", price_dir), \
             patch("src.data.pool_manager.FUNDAMENTAL_DIR", fundamental_dir), \
             patch("src.data.pool_manager.BENCHMARK_SYMBOLS", []), \
             patch("src.data.data_guardian.snapshot", return_value=None):
            from src.data.pool_manager import cleanup_stale_data
            stats = cleanup_stale_data(["SYM0", "SYM1"])

        assert stats.get("aborted") is True
        assert stats["csv_deleted"] == 0
        # 所有文件应该还在
        assert len(list(price_dir.glob("*.csv"))) == 10

    def test_safety_fuse_allows_small_cleanup(self, setup_dirs):
        """删除低于 30% CSV 时正常执行"""
        tmp_path, price_dir, fundamental_dir, pool_dir = setup_dirs

        # 创建 10 个 CSV
        for i in range(10):
            _create_csv(price_dir, f"SYM{i}")

        # 保留 8 个 → 要删 2 个 (20%)
        keep = [f"SYM{i}" for i in range(8)]
        with patch("src.data.pool_manager.PRICE_DIR", price_dir), \
             patch("src.data.pool_manager.FUNDAMENTAL_DIR", fundamental_dir), \
             patch("src.data.pool_manager.BENCHMARK_SYMBOLS", []), \
             patch("src.data.data_guardian.snapshot", return_value=None):
            from src.data.pool_manager import cleanup_stale_data
            stats = cleanup_stale_data(keep)

        assert stats.get("aborted") is not True
        assert stats["csv_deleted"] == 2
        assert len(list(price_dir.glob("*.csv"))) == 8

    def test_safety_fuse_fundamental_threshold(self, setup_dirs):
        """基本面条目删除超过 30% 时触发熔断"""
        tmp_path, price_dir, fundamental_dir, pool_dir = setup_dirs

        # 创建有 10 个 symbol 条目的 JSON
        data = {f"SYM{i}": {"name": f"Company {i}"} for i in range(10)}
        data["_meta"] = {"updated_at": "2026-02-14"}
        (fundamental_dir / "profiles.json").write_text(json.dumps(data))

        # 只保留 2 个 → 要删 8 个 (80%)
        with patch("src.data.pool_manager.PRICE_DIR", price_dir), \
             patch("src.data.pool_manager.FUNDAMENTAL_DIR", fundamental_dir), \
             patch("src.data.pool_manager.BENCHMARK_SYMBOLS", []):
            from src.data.pool_manager import cleanup_stale_data
            stats = cleanup_stale_data(["SYM0", "SYM1"])

        assert stats.get("aborted") is True
        assert stats["fundamental_cleaned"] == 0

    def test_default_reads_universe(self, setup_dirs):
        """不传 active_symbols 时从 universe.json 读取"""
        tmp_path, price_dir, fundamental_dir, pool_dir = setup_dirs

        # 创建 universe.json with 10 symbols
        keep = [f"SYM{i}" for i in range(10)]
        universe = [{"symbol": s} for s in keep]
        with open(pool_dir / "universe.json", "w") as f:
            json.dump(universe, f)

        # 创建 10 个有效 + 1 个过期 CSV → 删除比例 ~9%
        for s in keep:
            _create_csv(price_dir, s)
        _create_csv(price_dir, "DEAD")

        with patch("src.data.pool_manager.PRICE_DIR", price_dir), \
             patch("src.data.pool_manager.FUNDAMENTAL_DIR", fundamental_dir), \
             patch("src.data.pool_manager.BENCHMARK_SYMBOLS", ["SPY"]), \
             patch("src.data.pool_manager.UNIVERSE_FILE", pool_dir / "universe.json"), \
             patch("src.data.data_guardian.snapshot", return_value=None):
            from src.data.pool_manager import cleanup_stale_data
            stats = cleanup_stale_data()  # 不传参数

        assert stats["csv_deleted"] == 1
        assert not (price_dir / "DEAD.csv").exists()
