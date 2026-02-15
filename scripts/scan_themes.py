#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
未来资本 主线扫描 — Theme Engine P2

合并 Engine A (量价动量) + Engine B (注意力量化) 的信号，
输出"市场主线在哪"的统一报告 + 自动扩展股票池。

用法:
    python scripts/scan_themes.py                    # 完整周扫描
    python scripts/scan_themes.py --no-expand        # 跳过池扩展
    python scripts/scan_themes.py --dry-run          # 只看不做
    python scripts/scan_themes.py --top-n 20         # Engine B Top N
"""

import sys
import time
import json
import argparse
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Set, Any

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import (
    DATA_DIR, SCANS_DIR,
    THEME_TOP_N, THEME_MAX_NEW_TICKERS, THEME_RS_THRESHOLD,
    THEME_KEYWORDS_SEED,
)
from src.data import get_symbols
from src.indicators.engine import run_all_indicators, get_indicator_summary, run_momentum_scan
from terminal.attention_store import get_attention_store
from terminal.theme_pool import (
    expand_pool_from_attention,
    get_pool_expansion_stats,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# ============================================================
# Step 1: Engine B — 注意力周排名
# ============================================================

def get_latest_week_start() -> str:
    """计算最近一个周一的日期字符串 (YYYY-MM-DD)."""
    today = datetime.now().date()
    days_since_monday = today.weekday()
    monday = today - timedelta(days=days_since_monday)
    return monday.strftime("%Y-%m-%d")


def fetch_attention_ranking(top_n: int = THEME_TOP_N) -> List[Dict]:
    """
    读取 Engine B 最近一周的注意力排名。

    Returns:
        [{"ticker": "NVDA", "composite_score": 2.5, "rank": 1, ...}, ...]
    """
    store = get_attention_store()
    weeks = store.get_all_weeks()

    if not weeks:
        logger.warning("Engine B 无数据，跳过注意力排名")
        return []

    latest_week = weeks[0]
    ranking = store.get_weekly_ranking(latest_week, top_n=top_n)
    logger.info(
        "Engine B 排名: week=%s, top_n=%d, found=%d",
        latest_week, top_n, len(ranking),
    )
    return ranking


# ============================================================
# Step 4: 合并 A + B 信号
# ============================================================

def has_momentum_signal(
    symbol: str,
    momentum_results: Dict,
    indicator_summary: Dict,
    rs_threshold: int = THEME_RS_THRESHOLD,
) -> bool:
    """
    判断 symbol 是否有动量信号（任一触发即算）:
    - RS Rating B 或 C >= P{rs_threshold}
    - DV 加速 signal=True
    - RVOL sustained（任意级别）
    - PMARP breakout_98 或 recovery_2
    """
    # RS Rating
    rs_b = momentum_results.get("rs_rating_b")
    if rs_b is not None and len(rs_b) > 0:
        match = rs_b[rs_b["symbol"] == symbol]
        if len(match) > 0 and match.iloc[0]["rs_rank"] >= rs_threshold:
            return True

    rs_c = momentum_results.get("rs_rating_c")
    if rs_c is not None and len(rs_c) > 0:
        match = rs_c[rs_c["symbol"] == symbol]
        if len(match) > 0 and match.iloc[0]["rs_rank"] >= rs_threshold:
            return True

    # DV Acceleration
    dv = momentum_results.get("dv_acceleration")
    if dv is not None and len(dv) > 0:
        match = dv[dv["symbol"] == symbol]
        if len(match) > 0 and match.iloc[0].get("signal", False):
            return True

    # RVOL Sustained
    rvol_list = momentum_results.get("rvol_sustained", [])
    for item in rvol_list:
        if item.get("symbol") == symbol:
            return True

    # PMARP crossovers
    crossovers = indicator_summary.get("pmarp_crossovers", {})
    breakout = crossovers.get("breakout_98", [])
    recovery = crossovers.get("recovery_2", [])
    for entry in breakout:
        if entry.get("symbol") == symbol:
            return True
    for entry in recovery:
        if entry.get("symbol") == symbol:
            return True

    return False


def merge_signals(
    attention_ranking: List[Dict],
    momentum_results: Dict,
    indicator_summary: Dict,
    all_symbols: List[str],
    rs_threshold: int = THEME_RS_THRESHOLD,
) -> Dict[str, List[str]]:
    """
    合并 Engine A + Engine B 信号。

    Returns:
        {
            "converged": ["NVDA", ...],    # 双引擎共振
            "momentum_only": ["TSLA", ...], # 动量先行
            "narrative_only": ["IONQ", ...], # 叙事先行
        }
    """
    attention_tickers = set()
    for item in attention_ranking:
        t = item.get("ticker", "")
        if t:
            attention_tickers.add(t.upper())

    # 找出所有有动量信号的 ticker
    momentum_tickers = set()
    for sym in all_symbols:
        if has_momentum_signal(sym, momentum_results, indicator_summary, rs_threshold):
            momentum_tickers.add(sym)

    converged = sorted(attention_tickers & momentum_tickers)
    momentum_only = sorted(momentum_tickers - attention_tickers)
    narrative_only = sorted(attention_tickers - momentum_tickers)

    return {
        "converged": converged,
        "momentum_only": momentum_only,
        "narrative_only": narrative_only,
    }


# ============================================================
# Step 5: 主题匹配
# ============================================================

def match_themes(
    tickers: List[str],
    seed: Dict = None,
) -> Dict[str, List[str]]:
    """
    按 THEME_KEYWORDS_SEED 把 ticker 归类到主题。

    Returns:
        {"ai_chip": ["NVDA", "AMD"], "memory": ["MU"], ...}
    """
    if seed is None:
        seed = THEME_KEYWORDS_SEED

    ticker_set = set(t.upper() for t in tickers)
    theme_map = {}

    for theme_name, info in seed.items():
        theme_tickers = set(info.get("tickers", []))
        overlap = sorted(theme_tickers & ticker_set)
        if overlap:
            theme_map[theme_name] = overlap

    return theme_map


# ============================================================
# Step 6: 报告格式化
# ============================================================

def format_theme_report(
    expand_result: Dict,
    merged: Dict[str, List[str]],
    theme_map: Dict[str, List[str]],
    cluster_result: Dict,
    attention_ranking: List[Dict],
    pool_stats: Dict,
    elapsed: float,
) -> str:
    """
    格式化完整主线报告（终端文本，7 个 Section）。
    """
    now = datetime.now()
    weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][now.weekday()]

    lines = [
        "=" * 60,
        "未来资本 主线扫描 (Theme Engine P2)",
        "{} ({})".format(now.strftime("%Y-%m-%d %H:%M"), weekday),
        "=" * 60,
        "",
    ]

    # A: 池子扩展摘要
    lines.append("[ A. 池子扩展 ]")
    if expand_result:
        added = expand_result.get("added", [])
        skipped = expand_result.get("skipped_in_pool", [])
        failed = expand_result.get("failed", [])
        dry_run = expand_result.get("dry_run", False)
        tag = " [DRY-RUN]" if dry_run else ""

        if added:
            added_str = ", ".join(
                a["symbol"] if isinstance(a, dict) else a for a in added
            )
            lines.append("新增{}: {}".format(tag, added_str))
        else:
            lines.append("无新增{}".format(tag))
        if failed:
            lines.append("失败: {}".format(", ".join(failed)))
        lines.append(
            "池子: {} 只 (screener={}, analysis={}, attention={})".format(
                pool_stats.get("total", 0),
                pool_stats.get("screener", 0),
                pool_stats.get("analysis", 0),
                pool_stats.get("attention", 0),
            )
        )
    else:
        lines.append("跳过池扩展 (--no-expand)")
    lines.append("")

    # B: 主线共振 (converged)
    lines.append("[ B. 主线共振 (A+B 双引擎) ]")
    converged = merged.get("converged", [])
    if converged:
        for sym in converged:
            # 找 attention score
            score = _find_attention_score(sym, attention_ranking)
            score_str = " (attn={:.2f})".format(score) if score else ""
            lines.append("  {} {}".format(sym, score_str))
    else:
        lines.append("  无共振信号")
    lines.append("")

    # C: 动量先行 (momentum_only)
    lines.append("[ C. 动量先行 (Engine A only) ]")
    momentum_only = merged.get("momentum_only", [])
    if momentum_only:
        for i in range(0, len(momentum_only), 8):
            chunk = momentum_only[i:i + 8]
            lines.append("  {}".format("  ".join(chunk)))
    else:
        lines.append("  无")
    lines.append("")

    # D: 叙事先行 (narrative_only)
    lines.append("[ D. 叙事先行 (Engine B only) ]")
    narrative_only = merged.get("narrative_only", [])
    if narrative_only:
        for sym in narrative_only:
            score = _find_attention_score(sym, attention_ranking)
            score_str = " (attn={:.2f})".format(score) if score else ""
            lines.append("  {} {}".format(sym, score_str))
    else:
        lines.append("  无")
    lines.append("")

    # E: 主题热力图
    lines.append("[ E. 主题热力图 ]")
    if theme_map:
        for theme, tickers in sorted(
            theme_map.items(), key=lambda x: -len(x[1])
        ):
            lines.append("  {}: {}".format(theme, " ".join(tickers)))
    else:
        lines.append("  无主题信号")
    lines.append("")

    # F: 聚类周报
    lines.append("[ F. 聚类周报 ]")
    clusters = cluster_result.get("clusters", {})
    if clusters:
        lines.append("  {} 个集群".format(len(clusters)))
        for cid, members in clusters.items():
            members_str = " ".join(members[:10])
            if len(members) > 10:
                members_str += "..."
            lines.append("  C{}: {} ({})".format(cid, members_str, len(members)))
    else:
        lines.append("  无聚类数据")
    lines.append("")

    # G: 建议深度分析
    lines.append("[ G. 建议深度分析 ]")
    if converged:
        lines.append("  共振标的: {}".format(" ".join(converged)))
    else:
        lines.append("  无建议")
    lines.append("")

    # Footer
    lines.append("-" * 60)
    lines.append("耗时: {:.0f}s".format(elapsed))

    return "\n".join(lines)


def _find_attention_score(symbol: str, ranking: List[Dict]) -> float:
    """在注意力排名中查找 composite_score。"""
    for item in ranking:
        if item.get("ticker", "").upper() == symbol.upper():
            return item.get("composite_score", 0.0)
    return 0.0


# ============================================================
# 主流程
# ============================================================

def run_theme_scan(
    no_expand: bool = False,
    dry_run: bool = False,
    top_n: int = THEME_TOP_N,
    force_clustering: bool = False,
) -> Dict[str, Any]:
    """
    执行完整主线扫描。

    Returns:
        {
            "expand_result": {...},
            "merged": {"converged": [...], ...},
            "theme_map": {...},
            "report": str,
        }
    """
    start_time = time.time()

    # Step 1: Engine B 注意力排名
    logger.info("Step 1: 读取 Engine B 注意力排名 (top_n=%d)", top_n)
    attention_ranking = fetch_attention_ranking(top_n=top_n)
    hot_tickers = [r["ticker"] for r in attention_ranking if r.get("ticker")]

    # Step 2: 池子扩展
    expand_result = None
    if not no_expand and hot_tickers:
        logger.info("Step 2: 池子扩展 (%d 个热股候选)", len(hot_tickers))
        expand_result = expand_pool_from_attention(
            hot_tickers,
            max_new=THEME_MAX_NEW_TICKERS,
            dry_run=dry_run,
        )
    else:
        logger.info("Step 2: 跳过池扩展")

    # Step 3: Engine A — 在完整池上跑动量扫描
    symbols = get_symbols()
    logger.info("Step 3: Engine A 动量扫描 (%d 只)", len(symbols))

    indicator_results = run_all_indicators(symbols, parallel=True)
    indicator_summary = get_indicator_summary(indicator_results)
    momentum_results = run_momentum_scan(symbols, max_age_days=0)

    # 聚类 (周六或强制)
    is_saturday = datetime.now().weekday() == 5
    cluster_result = {}
    if is_saturday or force_clustering:
        try:
            from scripts.morning_report import run_clustering
            cluster_result = run_clustering(symbols)
        except Exception as e:
            logger.warning("聚类失败: %s", e)

    # Step 4: 合并 A + B
    logger.info("Step 4: 合并信号")
    merged = merge_signals(
        attention_ranking,
        momentum_results,
        indicator_summary,
        symbols,
    )
    logger.info(
        "合并结果: converged=%d, momentum_only=%d, narrative_only=%d",
        len(merged["converged"]),
        len(merged["momentum_only"]),
        len(merged["narrative_only"]),
    )

    # Step 5: 主题匹配
    logger.info("Step 5: 主题匹配")
    all_signal_tickers = (
        merged["converged"] + merged["momentum_only"] + merged["narrative_only"]
    )
    theme_map = match_themes(all_signal_tickers)

    # Pool stats
    pool_stats = get_pool_expansion_stats()

    elapsed = time.time() - start_time

    # Step 6: 报告
    report = format_theme_report(
        expand_result or {},
        merged,
        theme_map,
        cluster_result,
        attention_ranking,
        pool_stats,
        elapsed,
    )

    # 保存 JSON
    SCANS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_path = SCANS_DIR / "theme_{}.json".format(timestamp)
    save_data = {
        "timestamp": timestamp,
        "attention_ranking": [
            {"ticker": r.get("ticker"), "score": r.get("composite_score")}
            for r in attention_ranking
        ],
        "merged": merged,
        "theme_map": theme_map,
        "pool_stats": pool_stats,
        "expand_result": {
            "added": [
                e["symbol"] if isinstance(e, dict) else e
                for e in (expand_result or {}).get("added", [])
            ],
            "failed": (expand_result or {}).get("failed", []),
        },
        "elapsed": round(elapsed, 1),
    }
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2)
    logger.info("结果已保存: %s", save_path)

    return {
        "expand_result": expand_result,
        "merged": merged,
        "theme_map": theme_map,
        "cluster_result": cluster_result,
        "report": report,
        "save_path": str(save_path),
    }


def main():
    parser = argparse.ArgumentParser(description="未来资本 主线扫描")
    parser.add_argument("--no-expand", action="store_true", help="跳过池扩展")
    parser.add_argument("--dry-run", action="store_true", help="只看不做")
    parser.add_argument("--top-n", type=int, default=THEME_TOP_N, help="Engine B Top N")
    parser.add_argument("--clustering", action="store_true", help="强制运行聚类")
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("未来资本 主线扫描 开始")
    logger.info("=" * 60)

    result = run_theme_scan(
        no_expand=args.no_expand,
        dry_run=args.dry_run,
        top_n=args.top_n,
        force_clustering=args.clustering,
    )

    print(result["report"])

    logger.info("=" * 60)
    logger.info("主线扫描完成")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
