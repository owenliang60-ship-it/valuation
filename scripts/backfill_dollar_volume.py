#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dollar Volume 历史回填脚本

三阶段设计（均可断点续传）：
  Phase 1: 识别股票 (~6 API calls, ~12秒)
  Phase 2: 下载历史 (~1000 API calls, ~35分钟)
  Phase 3: 计算排名 (0 API calls, ~30秒)

用法:
    python scripts/backfill_dollar_volume.py                    # 跑全部
    python scripts/backfill_dollar_volume.py --phase discover   # 只识别股票
    python scripts/backfill_dollar_volume.py --phase download   # 只下载历史
    python scripts/backfill_dollar_volume.py --phase process    # 只计算排名
    python scripts/backfill_dollar_volume.py --status           # 查看进度
    python scripts/backfill_dollar_volume.py --days 90          # 只回填90天
"""

import sys
import time
import json
import argparse
import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import (
    DOLLAR_VOLUME_DB, DOLLAR_VOLUME_TOP_N, DATA_DIR,
)
from src.data.fmp_client import FMPClient
from src.data.dollar_volume import (
    init_db, get_connection, store_daily_rankings,
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CACHE_DIR = DATA_DIR / "dollar_volume_cache"


# ============================================================
# Phase 1: 识别需要回填的股票
# ============================================================

def phase_discover(client: FMPClient, min_dollar_volume: float = 1_000_000):
    """
    分页拉取全市场，过滤出 dollar_volume > min 的候选股票
    写入 backfill_progress 表 (status='pending')
    """
    logger.info("=== Phase 1: Discover stocks ===")

    all_stocks = {}
    offset = 0
    api_calls = 0

    while True:
        page = client.get_screener_page(offset=offset, limit=1000)
        api_calls += 1
        logger.info(f"  offset={offset}: got {len(page)} stocks")

        if not page:
            break
        for s in page:
            sym = s.get("symbol")
            if sym:
                all_stocks[sym] = s
        if len(page) < 1000:
            break
        offset += 1000

    # 过滤：只要当前 dollar volume > threshold 的
    candidates = []
    for sym, s in all_stocks.items():
        price = s.get("price", 0) or 0
        volume = s.get("volume", 0) or 0
        dv = price * volume
        if dv >= min_dollar_volume:
            candidates.append(sym)

    logger.info(f"Total stocks: {len(all_stocks)}, candidates (dv>$1M): {len(candidates)}")

    # 写入 backfill_progress（只添加新的，不覆盖已有的）
    conn = get_connection()
    try:
        existing = {r["symbol"] for r in conn.execute(
            "SELECT symbol FROM backfill_progress"
        ).fetchall()}

        new_count = 0
        for sym in candidates:
            if sym not in existing:
                conn.execute(
                    "INSERT INTO backfill_progress (symbol, status, updated_at) VALUES (?, 'pending', ?)",
                    (sym, datetime.now().isoformat())
                )
                new_count += 1
        conn.commit()
        logger.info(f"Added {new_count} new symbols to backfill queue (total: {len(existing) + new_count})")
    finally:
        conn.close()

    return len(candidates), api_calls


# ============================================================
# Phase 2: 下载历史数据
# ============================================================

def phase_download(client: FMPClient):
    """
    对每个 pending 股票下载历史价格，保存到缓存文件
    支持断点续传：只处理 status='pending' 的
    """
    logger.info("=== Phase 2: Download historical data ===")
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    conn = get_connection()
    try:
        pending = conn.execute(
            "SELECT symbol FROM backfill_progress WHERE status = 'pending' ORDER BY symbol"
        ).fetchall()
    finally:
        conn.close()

    total = len(pending)
    logger.info(f"Pending downloads: {total}")

    if total == 0:
        logger.info("Nothing to download")
        return 0

    downloaded = 0
    errors = 0

    for i, row in enumerate(pending, 1):
        symbol = row["symbol"]
        cache_file = CACHE_DIR / f"{symbol}.json"

        # 如果缓存文件已存在（之前下载过但状态未更新），直接标记
        if cache_file.exists():
            _update_backfill_status(symbol, "downloaded")
            downloaded += 1
            continue

        try:
            data = client.get_historical_price(symbol)

            if data:
                with open(cache_file, "w") as f:
                    json.dump(data, f)
                _update_backfill_status(symbol, "downloaded")
                downloaded += 1
            else:
                _update_backfill_status(symbol, "error", "empty response")
                errors += 1

        except Exception as e:
            _update_backfill_status(symbol, "error", str(e)[:200])
            errors += 1

        if i % 50 == 0:
            logger.info(f"  Progress: {i}/{total} (downloaded={downloaded}, errors={errors})")

    logger.info(f"Download complete: {downloaded} ok, {errors} errors")
    return downloaded


def _update_backfill_status(symbol: str, status: str, error_msg: str = None):
    """更新 backfill_progress 状态"""
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE backfill_progress SET status=?, error_message=?, updated_at=? WHERE symbol=?",
            (status, error_msg, datetime.now().isoformat(), symbol)
        )
        conn.commit()
    finally:
        conn.close()


# ============================================================
# Phase 3: 计算历史排名
# ============================================================

def phase_process(days: int = 180):
    """
    加载所有已下载的历史数据，对每个交易日计算排名
    """
    logger.info(f"=== Phase 3: Process rankings (last {days} days) ===")

    # 获取已下载的股票列表
    conn = get_connection()
    try:
        symbols = [r["symbol"] for r in conn.execute(
            "SELECT symbol FROM backfill_progress WHERE status = 'downloaded'"
        ).fetchall()]
    finally:
        conn.close()

    logger.info(f"Loading history for {len(symbols)} symbols...")

    # 加载所有历史数据，按日期分组
    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    daily_data = defaultdict(list)  # date -> [{symbol, price, volume, dv, ...}]

    loaded = 0
    for symbol in symbols:
        cache_file = CACHE_DIR / f"{symbol}.json"
        if not cache_file.exists():
            continue

        try:
            with open(cache_file) as f:
                history = json.load(f)
        except (json.JSONDecodeError, IOError):
            continue

        for day in history:
            date = day.get("date", "")
            if date < cutoff:
                continue

            price = day.get("close") or day.get("adjClose") or 0
            volume = day.get("volume", 0) or 0

            if price > 0 and volume > 0:
                daily_data[date].append({
                    "symbol": symbol,
                    "price": round(price, 2),
                    "volume": int(volume),
                    "dollar_volume": round(price * volume, 2),
                    "company_name": "",
                    "market_cap": None,
                    "sector": "",
                })

        loaded += 1
        if loaded % 200 == 0:
            logger.info(f"  Loaded {loaded}/{len(symbols)} symbols")

    logger.info(f"Loaded {loaded} symbols, {len(daily_data)} trading days")

    # 对每个交易日计算排名并存储
    dates_processed = 0
    for date in sorted(daily_data.keys()):
        stocks = daily_data[date]
        stocks.sort(key=lambda x: x["dollar_volume"], reverse=True)

        rankings = []
        for i, item in enumerate(stocks[:DOLLAR_VOLUME_TOP_N], 1):
            item["rank"] = i
            rankings.append(item)

        store_daily_rankings(date, rankings)
        dates_processed += 1

    logger.info(f"Processed {dates_processed} trading days")
    return dates_processed


# ============================================================
# 进度查看
# ============================================================

def show_status():
    """显示回填进度"""
    init_db()
    conn = get_connection()
    try:
        stats = conn.execute("""
            SELECT status, COUNT(*) as cnt
            FROM backfill_progress
            GROUP BY status
        """).fetchall()

        print("\n=== Backfill Progress ===")
        total = 0
        for row in stats:
            print(f"  {row['status']:<12}: {row['cnt']:>6}")
            total += row["cnt"]
        print(f"  {'total':<12}: {total:>6}")

        # 数据库中的日期范围
        date_range = conn.execute("""
            SELECT MIN(date) as min_date, MAX(date) as max_date,
                   COUNT(DISTINCT date) as days
            FROM daily_rankings
        """).fetchone()

        if date_range["min_date"]:
            print(f"\n=== DB Date Range ===")
            print(f"  From: {date_range['min_date']}")
            print(f"  To:   {date_range['max_date']}")
            print(f"  Days: {date_range['days']}")

        # 缓存文件数
        if CACHE_DIR.exists():
            cache_count = len(list(CACHE_DIR.glob("*.json")))
            cache_size = sum(f.stat().st_size for f in CACHE_DIR.glob("*.json"))
            print(f"\n=== Cache ===")
            print(f"  Files: {cache_count}")
            print(f"  Size:  {cache_size / 1024 / 1024:.1f} MB")

        # 错误列表（最多10个）
        errors = conn.execute("""
            SELECT symbol, error_message FROM backfill_progress
            WHERE status = 'error' LIMIT 10
        """).fetchall()
        if errors:
            print(f"\n=== Recent Errors (up to 10) ===")
            for e in errors:
                print(f"  {e['symbol']}: {e['error_message']}")

    finally:
        conn.close()


# ============================================================
# Main
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Backfill Dollar Volume history")
    parser.add_argument("--phase", choices=["discover", "download", "process"],
                        help="Run specific phase only")
    parser.add_argument("--status", action="store_true", help="Show progress")
    parser.add_argument("--days", type=int, default=180, help="Days to backfill (default: 180)")
    parser.add_argument("--clean-cache", action="store_true",
                        help="Delete cache after processing")
    args = parser.parse_args()

    init_db()

    if args.status:
        show_status()
        return

    client = FMPClient()
    start = time.time()

    if args.phase == "discover" or args.phase is None:
        phase_discover(client)

    if args.phase == "download" or args.phase is None:
        phase_download(client)

    if args.phase == "process" or args.phase is None:
        phase_process(days=args.days)

    elapsed = time.time() - start
    logger.info(f"\nBackfill completed in {elapsed:.1f}s")

    if args.clean_cache and CACHE_DIR.exists():
        import shutil
        shutil.rmtree(CACHE_DIR)
        logger.info(f"Cache cleaned: {CACHE_DIR}")

    show_status()


if __name__ == "__main__":
    main()
