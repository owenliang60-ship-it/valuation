"""
清洗大市值股票列表
1. 过滤掉 ETF 和基金
2. 只保留美国公司
3. 处理重复（同一公司不同股票类别）
4. 按市值排序
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


def clean_stock_list():
    # 读取原始数据
    with open(DATA_DIR / "large_cap_stocks.json", "r") as f:
        stocks = json.load(f)

    print(f"原始数据: {len(stocks)} 家")

    # Step 1: 过滤 ETF 和基金
    stocks = [s for s in stocks if not s.get("isEtf") and not s.get("isFund")]
    print(f"过滤 ETF/基金后: {len(stocks)} 家")

    # Step 2: 只保留美国公司
    stocks = [s for s in stocks if s.get("country") == "US"]
    print(f"只保留美国公司后: {len(stocks)} 家")

    # Step 3: 只保留活跃交易的
    stocks = [s for s in stocks if s.get("isActivelyTrading")]
    print(f"只保留活跃交易后: {len(stocks)} 家")

    # Step 4: 处理同一公司多个股票类别
    # 已知的重复: GOOG/GOOGL, BRK-A/BRK-B, 等
    # 策略: 保留市值较大的那个
    seen_companies = {}
    for s in stocks:
        name = s.get("companyName", "").lower()
        # 标准化公司名
        name_key = name.replace(" inc.", "").replace(" inc", "").replace(" corp.", "").replace(" corp", "").strip()

        if name_key not in seen_companies:
            seen_companies[name_key] = s
        else:
            # 保留市值较大的
            if s.get("marketCap", 0) > seen_companies[name_key].get("marketCap", 0):
                seen_companies[name_key] = s

    stocks = list(seen_companies.values())
    print(f"去重后: {len(stocks)} 家")

    # Step 5: 按市值排序
    stocks = sorted(stocks, key=lambda x: x.get("marketCap", 0), reverse=True)

    # 打印结果
    print("\n" + "=" * 70)
    print(f"最终股票池: {len(stocks)} 家公司 (市值 > $1000 亿)")
    print("=" * 70)

    print(f"\n{'排名':<4} {'代码':<8} {'公司名称':<35} {'行业':<25} {'市值($B)':<10}")
    print("-" * 85)

    for i, s in enumerate(stocks[:30], 1):
        symbol = s.get("symbol", "N/A")
        name = s.get("companyName", "N/A")[:33]
        industry = s.get("industry", "N/A")[:23]
        market_cap = s.get("marketCap", 0) / 1e9
        print(f"{i:<4} {symbol:<8} {name:<35} {industry:<25} ${market_cap:,.0f}B")

    if len(stocks) > 30:
        print(f"... 还有 {len(stocks) - 30} 家公司")

    # 行业分布
    print("\n" + "=" * 70)
    print("行业分布:")
    print("=" * 70)

    sector_count = {}
    for s in stocks:
        sector = s.get("sector", "Unknown") or "Unknown"
        sector_count[sector] = sector_count.get(sector, 0) + 1

    for sector, count in sorted(sector_count.items(), key=lambda x: -x[1]):
        print(f"  {sector}: {count} 家")

    # 保存清洗后的数据
    output_path = DATA_DIR / "us_large_cap_stocks.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(stocks, f, ensure_ascii=False, indent=2)
    print(f"\n📁 清洗后数据已保存到: {output_path}")

    # 同时保存一个简化版本（只有 symbol 列表）
    symbols = [s.get("symbol") for s in stocks]
    symbols_path = DATA_DIR / "us_large_cap_symbols.json"
    with open(symbols_path, "w") as f:
        json.dump(symbols, f, indent=2)
    print(f"📁 股票代码列表已保存到: {symbols_path}")

    return stocks


if __name__ == "__main__":
    clean_stock_list()
