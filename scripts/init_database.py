"""
初始化估值数据库
- 从 JSON 文件导入基本面数据到 SQLite
- 同时存储季度数据和年度数据
- 只包含股票池内的股票
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime

# 路径配置
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "valuation.db"


def load_json(filename: str) -> dict:
    """加载 JSON 文件"""
    with open(DATA_DIR / filename, encoding="utf-8") as f:
        return json.load(f)


def get_pool_symbols() -> set:
    """获取股票池中的股票代码"""
    universe = load_json("pool/universe.json")
    return {s["symbol"] for s in universe}


def create_tables(conn: sqlite3.Connection):
    """创建数据表"""
    cursor = conn.cursor()

    # 公司基本信息表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            symbol TEXT PRIMARY KEY,
            company_name TEXT,
            sector TEXT,
            industry TEXT,
            market_cap REAL,
            price REAL,
            beta REAL,
            dividend_yield REAL,
            pe_ratio REAL,
            exchange TEXT,
            country TEXT,
            employees INTEGER,
            ipo_date TEXT,
            description TEXT,
            updated_at TEXT
        )
    """)

    # 财务数据表 (季度 + 年度)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS financials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            date TEXT,
            fiscal_year INTEGER,
            period TEXT,              -- Q1, Q2, Q3, Q4, FY
            period_type TEXT,         -- 'quarterly' or 'annual'

            -- 利润表数据
            revenue REAL,
            gross_profit REAL,
            operating_income REAL,
            ebitda REAL,
            net_income REAL,
            r_and_d REAL,             -- 研发费用

            -- 现金流量表数据
            operating_cash_flow REAL,
            capital_expenditure REAL,
            free_cash_flow REAL,      -- 自由现金流 (真实值)
            dividends_paid REAL,
            stock_repurchased REAL,   -- 回购金额

            -- 资产负债表数据
            total_assets REAL,
            total_liabilities REAL,
            total_equity REAL,
            total_debt REAL,
            net_debt REAL,
            cash_and_equivalents REAL,
            retained_earnings REAL,

            -- 估值指标 (仅年度数据有)
            pe_ratio REAL,
            peg_ratio REAL,
            forward_peg REAL,
            pb_ratio REAL,
            ps_ratio REAL,
            price_to_fcf REAL,
            ev_multiple REAL,

            -- 盈利能力
            gross_margin REAL,
            operating_margin REAL,
            net_margin REAL,
            ebitda_margin REAL,
            roe REAL,                 -- 净资产收益率
            roa REAL,                 -- 总资产收益率

            -- 每股指标
            eps REAL,
            eps_diluted REAL,
            fcf_per_share REAL,
            book_value_per_share REAL,
            dividend_per_share REAL,

            -- 财务健康 (仅年度数据有)
            current_ratio REAL,
            quick_ratio REAL,
            debt_to_equity REAL,
            debt_to_assets REAL,
            interest_coverage REAL,

            -- 股数
            shares_outstanding REAL,

            UNIQUE(symbol, date, period),
            FOREIGN KEY (symbol) REFERENCES companies(symbol)
        )
    """)

    # 创建索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_fin_symbol ON financials(symbol)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_fin_date ON financials(date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_fin_period_type ON financials(period_type)")

    conn.commit()
    print("✓ 数据表创建完成")


def import_companies(conn: sqlite3.Connection, pool_symbols: set):
    """导入公司基本信息"""
    profiles = load_json("fundamental/profiles.json")
    ratios = load_json("fundamental/ratios.json")

    cursor = conn.cursor()
    count = 0

    for symbol in pool_symbols:
        if symbol not in profiles:
            print(f"  ⚠ {symbol} 无 profile 数据")
            continue

        p = profiles[symbol]

        # 获取最新的 PE ratio
        pe = None
        if symbol in ratios and ratios[symbol]:
            latest = ratios[symbol][0]
            pe = latest.get("priceToEarningsRatio")

        cursor.execute("""
            INSERT OR REPLACE INTO companies
            (symbol, company_name, sector, industry, market_cap, price, beta,
             dividend_yield, pe_ratio, exchange, country, employees, ipo_date,
             description, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            symbol,
            p.get("companyName"),
            p.get("sector"),
            p.get("industry"),
            p.get("marketCap"),
            p.get("price"),
            p.get("beta"),
            p.get("lastDividend"),
            pe,
            p.get("exchange"),
            p.get("country"),
            p.get("fullTimeEmployees"),
            p.get("ipoDate"),
            p.get("description"),
            p.get("_updated_at", datetime.now().isoformat())
        ))
        count += 1

    conn.commit()
    print(f"✓ 导入 {count} 家公司信息")


def load_json_safe(filename: str) -> dict:
    """安全加载 JSON 文件（文件不存在返回空字典）"""
    filepath = DATA_DIR / filename
    if filepath.exists():
        with open(filepath, encoding="utf-8") as f:
            return json.load(f)
    return {}


def import_quarterly_data(conn: sqlite3.Connection, pool_symbols: set):
    """导入季度数据 (整合 income + cash_flow + balance_sheet)"""
    income = load_json("fundamental/income.json")
    cash_flow = load_json_safe("fundamental/cash_flow.json")
    balance_sheet = load_json_safe("fundamental/balance_sheet.json")

    cursor = conn.cursor()
    count = 0

    for symbol in pool_symbols:
        if symbol not in income:
            continue

        # 建立 cash_flow 和 balance_sheet 的查找表 (按 date)
        cf_by_date = {c.get("date"): c for c in cash_flow.get(symbol, [])}
        bs_by_date = {b.get("date"): b for b in balance_sheet.get(symbol, [])}

        for i in income[symbol]:
            date = i.get("date")
            cf = cf_by_date.get(date, {})
            bs = bs_by_date.get(date, {})

            # 计算利润率
            revenue = i.get("revenue") or 0
            gross_margin = (i.get("grossProfit") or 0) / revenue if revenue else None
            operating_margin = (i.get("operatingIncome") or 0) / revenue if revenue else None
            net_margin = (i.get("netIncome") or 0) / revenue if revenue else None
            ebitda_margin = (i.get("ebitda") or 0) / revenue if revenue else None

            # 计算 ROE 和 ROA
            net_income = i.get("netIncome") or 0
            total_equity = bs.get("totalStockholdersEquity") or bs.get("totalEquity")
            total_assets = bs.get("totalAssets")
            roe = net_income / total_equity if total_equity and total_equity != 0 else None
            roa = net_income / total_assets if total_assets and total_assets != 0 else None

            # 计算净负债
            total_debt = bs.get("totalDebt")
            cash = bs.get("cashAndCashEquivalents")
            net_debt = (total_debt or 0) - (cash or 0) if total_debt is not None else None

            cursor.execute("""
                INSERT OR REPLACE INTO financials
                (symbol, date, fiscal_year, period, period_type,
                 revenue, gross_profit, operating_income, ebitda, net_income, r_and_d,
                 operating_cash_flow, capital_expenditure, free_cash_flow, dividends_paid, stock_repurchased,
                 total_assets, total_liabilities, total_equity, total_debt, net_debt, cash_and_equivalents, retained_earnings,
                 gross_margin, operating_margin, net_margin, ebitda_margin, roe, roa,
                 eps, eps_diluted, shares_outstanding)
                VALUES (?, ?, ?, ?, 'quarterly', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                symbol,
                date,
                i.get("fiscalYear"),
                i.get("period"),
                # 利润表
                i.get("revenue"),
                i.get("grossProfit"),
                i.get("operatingIncome"),
                i.get("ebitda"),
                i.get("netIncome"),
                i.get("researchAndDevelopmentExpenses"),
                # 现金流量表
                cf.get("operatingCashFlow"),
                cf.get("capitalExpenditure"),
                cf.get("freeCashFlow"),
                cf.get("dividendsPaid") or cf.get("commonDividendsPaid"),
                cf.get("commonStockRepurchased"),
                # 资产负债表
                bs.get("totalAssets"),
                bs.get("totalLiabilities"),
                total_equity,
                total_debt,
                net_debt,
                cash,
                bs.get("retainedEarnings"),
                # 利润率
                gross_margin,
                operating_margin,
                net_margin,
                ebitda_margin,
                roe,
                roa,
                # 每股指标
                i.get("eps"),
                i.get("epsdiluted"),
                i.get("weightedAverageShsOut"),
            ))
            count += 1

    conn.commit()
    print(f"✓ 导入 {count} 条季度数据")


def import_annual_data(conn: sqlite3.Connection, pool_symbols: set):
    """导入年度数据 (整合 ratios + income + cash_flow + balance_sheet)"""
    ratios = load_json("fundamental/ratios.json")
    income = load_json("fundamental/income.json")
    cash_flow = load_json_safe("fundamental/cash_flow.json")
    balance_sheet = load_json_safe("fundamental/balance_sheet.json")

    cursor = conn.cursor()
    count = 0

    for symbol in pool_symbols:
        if symbol not in ratios:
            continue

        # 建立数据查找表 (按 date)
        income_by_date = {i.get("date"): i for i in income.get(symbol, [])}
        cf_by_date = {c.get("date"): c for c in cash_flow.get(symbol, [])}
        bs_by_date = {b.get("date"): b for b in balance_sheet.get(symbol, [])}

        for r in ratios[symbol]:
            date = r.get("date")
            inc = income_by_date.get(date, {})
            cf = cf_by_date.get(date, {})
            bs = bs_by_date.get(date, {})

            # 从现金流量表获取真实 FCF
            fcf = cf.get("freeCashFlow")
            fcf_per_share = r.get("freeCashFlowPerShare")
            shares = inc.get("weightedAverageShsOut")

            # 如果没有真实 FCF，用 fcf_per_share 计算
            if fcf is None and fcf_per_share and shares:
                fcf = fcf_per_share * shares

            # 从各数据源获取值
            revenue = inc.get("revenue")
            gross_profit = inc.get("grossProfit")
            operating_income = inc.get("operatingIncome")
            ebitda = inc.get("ebitda")
            net_income = inc.get("netIncome")
            r_and_d = inc.get("researchAndDevelopmentExpenses")

            # 资产负债表数据
            total_equity = bs.get("totalStockholdersEquity") or bs.get("totalEquity")
            total_assets = bs.get("totalAssets")
            total_debt = bs.get("totalDebt")
            cash = bs.get("cashAndCashEquivalents")
            net_debt = (total_debt or 0) - (cash or 0) if total_debt is not None else None

            # 计算 ROE 和 ROA
            roe = net_income / total_equity if net_income and total_equity and total_equity != 0 else None
            roa = net_income / total_assets if net_income and total_assets and total_assets != 0 else None

            cursor.execute("""
                INSERT OR REPLACE INTO financials
                (symbol, date, fiscal_year, period, period_type,
                 revenue, gross_profit, operating_income, ebitda, net_income, r_and_d,
                 operating_cash_flow, capital_expenditure, free_cash_flow, dividends_paid, stock_repurchased,
                 total_assets, total_liabilities, total_equity, total_debt, net_debt, cash_and_equivalents, retained_earnings,
                 pe_ratio, peg_ratio, forward_peg, pb_ratio, ps_ratio, price_to_fcf, ev_multiple,
                 gross_margin, operating_margin, net_margin, ebitda_margin, roe, roa,
                 eps, fcf_per_share, book_value_per_share, dividend_per_share,
                 current_ratio, quick_ratio, debt_to_equity, debt_to_assets, interest_coverage,
                 shares_outstanding)
                VALUES (?, ?, ?, ?, 'annual', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                symbol,
                date,
                r.get("fiscalYear"),
                r.get("period"),
                # 利润表
                revenue,
                gross_profit,
                operating_income,
                ebitda,
                net_income,
                r_and_d,
                # 现金流量表
                cf.get("operatingCashFlow"),
                cf.get("capitalExpenditure"),
                fcf,
                cf.get("dividendsPaid") or cf.get("commonDividendsPaid"),
                cf.get("commonStockRepurchased"),
                # 资产负债表
                total_assets,
                bs.get("totalLiabilities"),
                total_equity,
                total_debt,
                net_debt,
                cash,
                bs.get("retainedEarnings"),
                # 估值指标
                r.get("priceToEarningsRatio"),
                r.get("priceToEarningsGrowthRatio"),
                r.get("forwardPriceToEarningsGrowthRatio"),
                r.get("priceToBookRatio"),
                r.get("priceToSalesRatio"),
                r.get("priceToFreeCashFlowRatio"),
                r.get("enterpriseValueMultiple"),
                # 盈利能力
                r.get("grossProfitMargin"),
                r.get("operatingProfitMargin"),
                r.get("netProfitMargin"),
                r.get("ebitdaMargin"),
                roe,
                roa,
                # 每股指标
                r.get("netIncomePerShare"),
                fcf_per_share,
                r.get("bookValuePerShare"),
                r.get("dividendPerShare"),
                # 财务健康
                r.get("currentRatio"),
                r.get("quickRatio"),
                r.get("debtToEquityRatio"),
                r.get("debtToAssetsRatio"),
                r.get("interestCoverageRatio"),
                shares,
            ))
            count += 1

    conn.commit()
    print(f"✓ 导入 {count} 条年度数据")


def calculate_ttm_data(conn: sqlite3.Connection, pool_symbols: set):
    """计算 TTM (Trailing Twelve Months) 数据 - 最近4个季度汇总"""
    ratios = load_json("fundamental/ratios.json")

    cursor = conn.cursor()
    count = 0

    for symbol in pool_symbols:
        # 获取最近 4 个季度的数据（包含新字段）
        cursor.execute("""
            SELECT date, fiscal_year,
                   revenue, gross_profit, operating_income, ebitda, net_income, r_and_d,
                   operating_cash_flow, capital_expenditure, free_cash_flow, dividends_paid, stock_repurchased,
                   total_assets, total_liabilities, total_equity, total_debt, net_debt, cash_and_equivalents,
                   eps, eps_diluted, shares_outstanding
            FROM financials
            WHERE symbol = ? AND period_type = 'quarterly'
            ORDER BY date DESC
            LIMIT 4
        """, (symbol,))

        quarters = cursor.fetchall()
        if len(quarters) < 4:
            continue  # 不足 4 个季度，跳过

        # 汇总计算 (利润表和现金流量表项目需要加总)
        ttm_date = quarters[0][0]  # 最新季度的日期
        ttm_fy = quarters[0][1]    # 最新季度的财年

        # 利润表项目 - 加总
        ttm_revenue = sum(q[2] or 0 for q in quarters)
        ttm_gross_profit = sum(q[3] or 0 for q in quarters)
        ttm_operating_income = sum(q[4] or 0 for q in quarters)
        ttm_ebitda = sum(q[5] or 0 for q in quarters)
        ttm_net_income = sum(q[6] or 0 for q in quarters)
        ttm_r_and_d = sum(q[7] or 0 for q in quarters)

        # 现金流量表项目 - 加总
        ttm_ocf = sum(q[8] or 0 for q in quarters)
        ttm_capex = sum(q[9] or 0 for q in quarters)
        ttm_fcf = sum(q[10] or 0 for q in quarters)
        ttm_dividends = sum(q[11] or 0 for q in quarters)
        ttm_buyback = sum(q[12] or 0 for q in quarters)

        # 资产负债表项目 - 使用最新季度的值 (存量数据，不能加总)
        total_assets = quarters[0][13]
        total_liabilities = quarters[0][14]
        total_equity = quarters[0][15]
        total_debt = quarters[0][16]
        net_debt = quarters[0][17]
        cash = quarters[0][18]

        # 每股指标 - 加总
        ttm_eps = sum(q[19] or 0 for q in quarters)
        ttm_eps_diluted = sum(q[20] or 0 for q in quarters)
        shares = quarters[0][21]  # 用最新季度的股数

        # 计算利润率
        gross_margin = ttm_gross_profit / ttm_revenue if ttm_revenue else None
        operating_margin = ttm_operating_income / ttm_revenue if ttm_revenue else None
        net_margin = ttm_net_income / ttm_revenue if ttm_revenue else None
        ebitda_margin = ttm_ebitda / ttm_revenue if ttm_revenue else None

        # 计算 ROE 和 ROA
        roe = ttm_net_income / total_equity if ttm_net_income and total_equity and total_equity != 0 else None
        roa = ttm_net_income / total_assets if ttm_net_income and total_assets and total_assets != 0 else None

        # 从最新年度数据获取估值指标
        pe_ratio = peg_ratio = pb_ratio = ps_ratio = price_to_fcf = ev_multiple = None
        fcf_per_share = book_value_per_share = dividend_per_share = None
        current_ratio = quick_ratio = debt_to_equity = debt_to_assets = interest_coverage = None

        if symbol in ratios and ratios[symbol]:
            latest_ratio = ratios[symbol][0]  # 最新年度比率数据
            pe_ratio = latest_ratio.get("priceToEarningsRatio")
            peg_ratio = latest_ratio.get("priceToEarningsGrowthRatio")
            pb_ratio = latest_ratio.get("priceToBookRatio")
            ps_ratio = latest_ratio.get("priceToSalesRatio")
            price_to_fcf = latest_ratio.get("priceToFreeCashFlowRatio")
            ev_multiple = latest_ratio.get("enterpriseValueMultiple")
            fcf_per_share = latest_ratio.get("freeCashFlowPerShare")
            book_value_per_share = latest_ratio.get("bookValuePerShare")
            dividend_per_share = latest_ratio.get("dividendPerShare")
            current_ratio = latest_ratio.get("currentRatio")
            quick_ratio = latest_ratio.get("quickRatio")
            debt_to_equity = latest_ratio.get("debtToEquityRatio")
            debt_to_assets = latest_ratio.get("debtToAssetsRatio")
            interest_coverage = latest_ratio.get("interestCoverageRatio")

        cursor.execute("""
            INSERT OR REPLACE INTO financials
            (symbol, date, fiscal_year, period, period_type,
             revenue, gross_profit, operating_income, ebitda, net_income, r_and_d,
             operating_cash_flow, capital_expenditure, free_cash_flow, dividends_paid, stock_repurchased,
             total_assets, total_liabilities, total_equity, total_debt, net_debt, cash_and_equivalents,
             pe_ratio, peg_ratio, forward_peg, pb_ratio, ps_ratio, price_to_fcf, ev_multiple,
             gross_margin, operating_margin, net_margin, ebitda_margin, roe, roa,
             eps, eps_diluted, fcf_per_share, book_value_per_share, dividend_per_share,
             current_ratio, quick_ratio, debt_to_equity, debt_to_assets, interest_coverage,
             shares_outstanding)
            VALUES (?, ?, ?, 'TTM', 'ttm', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            symbol,
            ttm_date,
            ttm_fy,
            # 利润表
            ttm_revenue if ttm_revenue else None,
            ttm_gross_profit if ttm_gross_profit else None,
            ttm_operating_income if ttm_operating_income else None,
            ttm_ebitda if ttm_ebitda else None,
            ttm_net_income if ttm_net_income else None,
            ttm_r_and_d if ttm_r_and_d else None,
            # 现金流量表
            ttm_ocf if ttm_ocf else None,
            ttm_capex if ttm_capex else None,
            ttm_fcf if ttm_fcf else None,
            ttm_dividends if ttm_dividends else None,
            ttm_buyback if ttm_buyback else None,
            # 资产负债表
            total_assets,
            total_liabilities,
            total_equity,
            total_debt,
            net_debt,
            cash,
            # 估值指标
            pe_ratio,
            peg_ratio,
            None,  # forward_peg
            pb_ratio,
            ps_ratio,
            price_to_fcf,
            ev_multiple,
            # 盈利能力
            gross_margin,
            operating_margin,
            net_margin,
            ebitda_margin,
            roe,
            roa,
            # 每股指标
            ttm_eps if ttm_eps else None,
            ttm_eps_diluted if ttm_eps_diluted else None,
            fcf_per_share,
            book_value_per_share,
            dividend_per_share,
            # 财务健康
            current_ratio,
            quick_ratio,
            debt_to_equity,
            debt_to_assets,
            interest_coverage,
            shares,
        ))
        count += 1

    conn.commit()
    print(f"✓ 计算 {count} 条 TTM 数据")


def print_summary(conn: sqlite3.Connection):
    """打印数据库摘要"""
    cursor = conn.cursor()

    print("\n" + "="*60)
    print("数据库创建完成: data/valuation.db")
    print("="*60)

    cursor.execute("SELECT COUNT(*) FROM companies")
    print(f"  companies: {cursor.fetchone()[0]} 家公司")

    cursor.execute("SELECT COUNT(*) FROM financials WHERE period_type = 'quarterly'")
    print(f"  季度数据: {cursor.fetchone()[0]} 条")

    cursor.execute("SELECT COUNT(*) FROM financials WHERE period_type = 'annual'")
    print(f"  年度数据: {cursor.fetchone()[0]} 条")

    cursor.execute("SELECT COUNT(*) FROM financials WHERE period_type = 'ttm'")
    print(f"  TTM数据: {cursor.fetchone()[0]} 条")

    # 示例：AAPL 数据结构
    print("\n" + "-"*60)
    print("示例: AAPL 季度 vs TTM vs 年度对比")
    print("-"*60)
    cursor.execute("""
        SELECT fiscal_year, period, period_type, date,
               revenue/1e9, net_income/1e9, free_cash_flow/1e9, pe_ratio
        FROM financials
        WHERE symbol = 'AAPL'
        ORDER BY
            CASE period_type
                WHEN 'ttm' THEN 0
                WHEN 'annual' THEN 1
                ELSE 2
            END,
            date DESC
        LIMIT 10
    """)
    print(f"{'FY':>4} {'Period':>6} {'Type':<10} {'Date':<12} {'Rev(B)':>8} {'NI(B)':>8} {'FCF(B)':>8} {'PE':>8}")
    for row in cursor.fetchall():
        rev = f"{row[4]:.1f}" if row[4] else "-"
        ni = f"{row[5]:.1f}" if row[5] else "-"
        fcf = f"{row[6]:.1f}" if row[6] else "-"
        pe = f"{row[7]:.1f}" if row[7] else "-"
        print(f"{row[0]:>4} {row[1]:>6} {row[2]:<10} {row[3]:<12} {rev:>8} {ni:>8} {fcf:>8} {pe:>8}")

    # 示例查询：使用 TTM 数据
    print("\n" + "-"*60)
    print("示例: TTM 收入 Top 10 (含年度化财务数据)")
    print("-"*60)
    cursor.execute("""
        SELECT c.symbol, c.company_name, c.sector,
               f.revenue/1e9, f.gross_profit/1e9, f.net_income/1e9,
               f.free_cash_flow/1e9, f.pe_ratio
        FROM companies c
        JOIN financials f ON c.symbol = f.symbol
        WHERE f.period_type = 'ttm'
        ORDER BY f.revenue DESC
        LIMIT 10
    """)
    print(f"{'Symbol':<6} {'Company':<18} {'Sector':<12} {'Rev':>8} {'GP':>8} {'NI':>8} {'FCF':>8} {'PE':>6}")
    for row in cursor.fetchall():
        fcf = f"{row[6]:.1f}" if row[6] else "-"
        pe = f"{row[7]:.1f}" if row[7] else "-"
        print(f"{row[0]:<6} {row[1][:18]:<18} {(row[2] or '')[:12]:<12} {row[3]:>7.0f}B {row[4]:>7.0f}B {row[5]:>7.0f}B {fcf:>7}B {pe:>6}")


def main():
    print("开始创建估值数据库...")
    print(f"数据库路径: {DB_PATH}\n")

    # 删除旧数据库
    if DB_PATH.exists():
        DB_PATH.unlink()
        print("✓ 删除旧数据库")

    # 获取股票池
    pool_symbols = get_pool_symbols()
    print(f"✓ 股票池: {len(pool_symbols)} 只股票\n")

    # 创建数据库
    conn = sqlite3.connect(DB_PATH)

    try:
        create_tables(conn)
        import_companies(conn, pool_symbols)
        import_quarterly_data(conn, pool_symbols)
        import_annual_data(conn, pool_symbols)
        calculate_ttm_data(conn, pool_symbols)
        print_summary(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
