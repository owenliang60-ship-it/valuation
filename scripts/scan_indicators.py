"""
技术指标扫描脚本
用法:
    python scripts/scan_indicators.py              # 扫描全部股票
    python scripts/scan_indicators.py --top 20     # 只显示前 20
    python scripts/scan_indicators.py --signals    # 只显示有信号的
    python scripts/scan_indicators.py --save       # 保存结果到文件
"""
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.indicators.engine import run_all_indicators, get_indicator_summary


def main():
    parser = argparse.ArgumentParser(description="技术指标扫描")
    parser.add_argument("--top", type=int, default=10, help="显示前 N 名 (默认 10)")
    parser.add_argument("--signals", action="store_true", help="只显示有信号的股票")
    parser.add_argument("--save", action="store_true", help="保存结果到文件")
    parser.add_argument("--symbols", type=str, help="指定股票代码，逗号分隔")

    args = parser.parse_args()

    print(f"\n{'=' * 70}")
    print(f"技术指标扫描")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 70}\n")

    # 解析股票列表
    symbols = None
    if args.symbols:
        symbols = [s.strip().upper() for s in args.symbols.split(",")]

    # 运行分析
    results = run_all_indicators(symbols, parallel=True)
    summary = get_indicator_summary(results)

    # 打印结果
    print(f"总股票数: {summary['total']}")
    print(f"有信号: {summary['with_signals']}")
    print(f"分析失败: {summary['errors']}")

    # 信号汇总
    if summary["signals"]:
        print("\n" + "=" * 70)
        print("信号汇总")
        print("=" * 70)

        # 按信号类型分组显示
        signal_types = {
            "pmarp:bullish_breakout": "PMARP 上穿 98% (强势追涨)",
            "pmarp:overbought": "PMARP > 95% (高位)",
            "pmarp:oversold_bounce": "PMARP 下穿 2% (超卖反弹)",
            "pmarp:oversold": "PMARP < 5% (超卖)",
            "rvol:extreme_volume": "RVOL >= 4σ (异常放量)",
            "rvol:high_volume": "RVOL >= 2σ (放量)",
            "rvol:low_volume": "RVOL <= -2σ (缩量)",
        }

        for sig_key, sig_desc in signal_types.items():
            if sig_key in summary["signals"]:
                stocks = summary["signals"][sig_key]
                print(f"\n{sig_desc}:")
                print(f"  {', '.join(stocks)}")

    # PMARP 排名
    print("\n" + "=" * 70)
    print(f"PMARP 排名 (Top {args.top})")
    print("=" * 70)

    print(f"\n最强 (追涨候选):")
    print(f"{'代码':<8} {'PMARP':<10} {'信号':<20}")
    print("-" * 40)
    for item in summary["top_pmarp"][:args.top]:
        print(f"{item['symbol']:<8} {item['value']:>6.1f}%    {item['signal']}")

    print(f"\n最弱 (超卖候选):")
    print(f"{'代码':<8} {'PMARP':<10} {'信号':<20}")
    print("-" * 40)
    # 反转显示最弱的
    low_list = sorted(summary["top_pmarp"], key=lambda x: x["value"])[:args.top]
    for item in low_list:
        print(f"{item['symbol']:<8} {item['value']:>6.1f}%    {item['signal']}")

    # RVOL 排名
    print("\n" + "=" * 70)
    print(f"RVOL 排名 (Top {args.top})")
    print("=" * 70)

    print(f"\n放量 (关注候选):")
    print(f"{'代码':<8} {'RVOL':<10} {'信号':<20}")
    print("-" * 40)
    for item in summary["top_rvol"][:args.top]:
        print(f"{item['symbol']:<8} {item['value']:>6.1f}σ    {item['signal']}")

    # 有信号的股票详情
    if args.signals:
        print("\n" + "=" * 70)
        print("有信号的股票详情")
        print("=" * 70)

        for symbol, data in results.items():
            if data.get("signals"):
                print(f"\n{symbol}:")
                pmarp = data.get("pmarp", {})
                rvol = data.get("rvol", {})
                if pmarp.get("current"):
                    print(f"  PMARP: {pmarp['current']:.1f}% - {pmarp.get('description', '')}")
                if rvol.get("current"):
                    print(f"  RVOL: {rvol['current']:.1f}σ - {rvol.get('description', '')}")

    # 保存结果
    if args.save:
        output_dir = PROJECT_ROOT / "data" / "scans"
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"scan_{timestamp}.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": timestamp,
                "summary": summary,
                "results": results
            }, f, ensure_ascii=False, indent=2, default=str)

        print(f"\n结果已保存到: {output_file}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
