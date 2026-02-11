# 002: Binance 限流级联导致 EMA120 扫描失败

**日期**: 2026-02-11
**严重性**: P1 — 单个扫描器失败
**影响**: EMA120 趋势扫描每天必挂，Telegram 报 "API请求失败"

## 现象

```
[4/5] 运行 EMA120 扫描器...
[API] 第1次请求失败: 429 Client Error: Too Many Requests
[API] 第2次请求失败: 429 ...
[API] 第3次请求失败: 429 ...
[错误] API请求失败，无法获取交易对列表
```

EMA120 之前的 PMARP 扫描 540 个合约，已经把 Binance IP 限流打满。

## 根因

`daily_scan_all.py` 5 个扫描器串行执行，间隔仅 **2 秒**。Binance futures API 的限流窗口是 1 分钟，PMARP 扫 540 个合约已消耗大量配额，2 秒根本不够恢复。

## 修复

```python
# daily_scan_all.py
time.sleep(30)  # 从 2s 改为 30s，等待限流窗口恢复
```

总耗时增加 ~2 分钟（4×30s vs 4×2s），可接受。

## 防范

- 串行任务共用 API 时，间隔要按限流窗口设计，不能只隔 2 秒
- 如果后续扫描器增多，考虑加限流 budget 跟踪
