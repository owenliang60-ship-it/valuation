# 003: PMARP sort_index() 导致计算结果完全反转

**日期**: 2026-02-11
**严重性**: P0 — 核心指标全部算反，从上线起就是错的
**影响**: 所有 PMARP 信号方向相反（超卖显示为突破，突破显示为超卖）

## 现象

| Ticker | 修复前 PMARP | 修复后 PMARP | 实际走势 |
|--------|-------------|-------------|---------|
| JPM | 0.67% (超卖) | 60.00% (中性) | 稳步上行 |
| QCOM | 100.00% (突破) | 2.67% (超卖) | 暴跌 11% |
| V | 3.33% (超卖) | 42.00% (中性) | 横盘微涨 |

**V 的 PMARP 一天从 52% 跳到 3%（价格还涨了）** 是发现此 bug 的线索。

## 根因

FMP API 返回价格数据按 **倒序**（最新在前），CSV 原样存储：

```
index 0    → 2026-02-10 (最新)
index 1260 → 2021-02-03 (最老)
```

`analyze_pmarp()` 先 `sort_values('date')` 正确排序为时间正序，但保留原始 index：

```
index 1260 → 2021-02-03
...
index 0    → 2026-02-10
```

然后 `calculate_pmarp()` 内部调用 `prices.sort_index()` 按 index 0,1,2... 重新排序，**把数据翻回倒序**：

```
index 0    → 2026-02-10 (最新，变成第一条)
...
index 1260 → 2021-02-03 (最老，变成最后一条)
```

后果：
1. **EMA 在反向数据上计算** — 完全错误
2. **`iloc[-1]` 取到 5 年前的值** — 报告的"当前"PMARP 其实是最老数据点的

## 修复

```python
# src/indicators/pmarp.py calculate_pmarp()
# 修复前
prices = prices.sort_index()
# 修复后
prices = prices.reset_index(drop=True)
```

`reset_index(drop=True)` 重建 0,1,2...N 索引，与传入顺序一致（调用方已按日期正序排列）。

## 教训

1. **`sort_index()` 不等于 "按时间排序"** — 当 DataFrame 经过 `sort_values()` 后 index 已被打乱，`sort_index()` 会把它恢复到原始（可能错误的）顺序
2. **倒序存储的 CSV + sort_index() = 定时炸弹** — 只要数据源的存储顺序和 index 顺序一致（都是倒序），`sort_values` 之后再 `sort_index` 就会撤销排序
3. **函数应信任调用方的排序承诺** — 文档说 "prices must be sorted chronologically"，函数内部不应自作主张 re-sort
4. **指标验证必须用已知数据** — 如果上线时用真实数据做过 sanity check（"JPM 在涨，PMARP 应该偏高"），这个 bug 当场就能发现
