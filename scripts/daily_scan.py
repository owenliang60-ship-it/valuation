#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
美股每日扫描 - 云端定时任务入口

功能：
1. 更新量价数据
2. 运行指标扫描
3. 发送 Telegram 通知

Author: Claude Code
Date: 2026-02-04
"""

import os
import sys
import time
import json
import requests
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# ============================================================
# 配置 (从环境变量读取)
# ============================================================
CONFIG = {
    "telegram_bot_token": os.environ.get("TELEGRAM_BOT_TOKEN", ""),
    "telegram_chat_id": os.environ.get("TELEGRAM_CHAT_ID", ""),
}


def log(msg: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def send_telegram(message: str, max_retries: int = 3) -> bool:
    """发送 Telegram 消息"""
    token = CONFIG["telegram_bot_token"]
    chat_id = CONFIG["telegram_chat_id"]

    if not token or not chat_id:
        log("[Telegram] 未配置，跳过发送")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.post(url, json=payload, timeout=15)
            response.raise_for_status()
            log("[Telegram] 消息已发送")
            return True
        except Exception as e:
            log(f"[Telegram] 第{attempt}次发送失败: {e}")
            if attempt < max_retries:
                time.sleep(attempt * 2)

    return False


def format_scan_message(summary: dict) -> str:
    """格式化扫描结果消息"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    msg = f"*🇺🇸 美股指标扫描*\n"
    msg += f"时间: {now}\n\n"

    # 信号汇总
    signals = summary.get("signals", {})
    if signals:
        msg += "*📊 信号汇总:*\n"

        signal_names = {
            "pmarp:bullish_breakout": "📈 PMARP突破98%",
            "pmarp:overbought": "⚠️ PMARP高位(>95%)",
            "pmarp:oversold_bounce": "📉 PMARP跌破2%",
            "pmarp:oversold": "💰 PMARP超卖(<5%)",
            "rvol:extreme_volume": "🔥 极端放量(4σ)",
            "rvol:high_volume": "📊 放量(2σ)",
        }

        for key, name in signal_names.items():
            if key in signals:
                msg += f"  {name}: {', '.join(signals[key])}\n"
    else:
        msg += "今日无信号触发\n"

    msg += f"\n扫描范围: {summary.get('total', 0)} 只股票"

    return msg


def run_scan():
    """运行指标扫描"""
    from src.indicators.engine import run_all_indicators, get_indicator_summary

    log("开始扫描指标...")
    results = run_all_indicators(parallel=True)
    summary = get_indicator_summary(results)

    log(f"扫描完成: {summary['total']} 只股票, {summary['with_signals']} 个信号")

    # 保存结果
    output_dir = PROJECT_ROOT / "data" / "scans"
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"scan_{timestamp}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": timestamp,
            "summary": summary,
        }, f, ensure_ascii=False, indent=2, default=str)

    log(f"结果已保存: {output_file}")

    return summary


def format_dollar_volume_message(result: dict) -> str:
    """格式化 Dollar Volume 消息"""
    date = result.get("date", "")
    rankings = result.get("rankings", [])
    new_faces = result.get("new_faces", [])

    msg = f"*💰 交易额 Top 50*\n"
    msg += f"日期: {date}\n\n"

    if not rankings:
        msg += "无数据\n"
        return msg

    # Top 10 详细
    msg += "*Top 10:*\n"
    msg += "```\n"
    msg += f" {'#':>2} {'Symbol':<7} {'$Vol':>8} {'Price':>8}\n"
    for r in rankings[:10]:
        dv = r["dollar_volume"]
        if dv >= 1e9:
            dv_str = f"${dv/1e9:.1f}B"
        else:
            dv_str = f"${dv/1e6:.0f}M"
        msg += f" {r['rank']:>2} {r['symbol']:<7} {dv_str:>8}  ${r['price']:>7.0f}\n"
    msg += "```\n"

    # #11-50 简略
    if len(rankings) > 10:
        rest = [r["symbol"] for r in rankings[10:]]
        # 每行8个
        lines = []
        for i in range(0, len(rest), 8):
            lines.append(", ".join(rest[i:i+8]))
        msg += f"\n*#11-50:*\n"
        msg += "\n".join(lines) + "\n"

    # 新面孔
    if new_faces:
        msg += f"\n*🆕 新面孔 ({len(new_faces)}):*\n"
        for nf in new_faces:
            dv = nf["dollar_volume"]
            if dv >= 1e9:
                dv_str = f"${dv/1e9:.1f}B"
            else:
                dv_str = f"${dv/1e6:.0f}M"
            sector = f" ({nf['sector']})" if nf.get("sector") else ""
            msg += f"  #{nf['rank']} {nf['symbol']}{sector} {dv_str}\n"
    else:
        msg += "\n无新面孔\n"

    return msg


def run_dollar_volume():
    """运行 Dollar Volume 采集"""
    try:
        # collect_dollar_volume.py 在同目录 scripts/ 下
        scripts_dir = str(Path(__file__).parent)
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
        from collect_dollar_volume import collect_daily

        log("开始采集 Dollar Volume...")
        result = collect_daily()
        log(f"Dollar Volume 采集完成: {result['status']}")
        return result
    except Exception as e:
        log(f"[Dollar Volume 错误] {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    log("=" * 60)
    log("美股每日扫描开始")
    log("=" * 60)

    start_time = time.time()

    try:
        # 1. 运行指标扫描
        summary = run_scan()
        scan_msg = format_scan_message(summary)

        # 2. Dollar Volume 采集
        dv_result = run_dollar_volume()
        dv_msg = format_dollar_volume_message(dv_result) if dv_result else ""

        # 3. 发送（超长则分两条）
        if dv_msg:
            full_msg = scan_msg + "\n" + dv_msg
            if len(full_msg) > 4000:
                send_telegram(scan_msg)
                send_telegram(dv_msg)
            else:
                send_telegram(full_msg)
        else:
            send_telegram(scan_msg)

    except Exception as e:
        log(f"[错误] {e}")
        import traceback
        traceback.print_exc()

        # 发送错误通知
        error_msg = f"*🇺🇸 美股扫描异常*\n\n错误: {str(e)[:200]}"
        send_telegram(error_msg)

    elapsed = time.time() - start_time
    log(f"\n扫描完成，耗时 {elapsed:.1f} 秒")
    log("=" * 60)


if __name__ == "__main__":
    main()
