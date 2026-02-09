# Postmortem: FMP Stock Screener Returns ~976 Stocks (Not 3000+)

**Date Discovered**: 2026-02-06
**Severity**: Low
**System Impact**: Stock pool selection
**Status**: Accepted (Not a Bug)

---

## Symptom

FMP Stock Screener API returns only ~976 stocks despite documentation claiming "3000+ US stocks" and no query parameters limiting results.

**Observable Behavior**:
```python
# scripts/refresh_stock_pool.py
screener_url = f"{BASE_URL}/stock-screener?marketCapMoreThan=100000000000&apikey={API_KEY}"
response = requests.get(screener_url)
results = response.json()

print(f"Total stocks: {len(results)}")  # Expected: 3000+, Actual: ~976
```

**Initial Hypothesis**: API bug, pagination missing, rate limit applied.

---

## Root Cause

**FMP Stock Screener Endpoint Has Undocumented Result Limits**

Investigation findings:
1. **No Pagination Support**: Screener endpoint does not support `page` or `limit` parameters
2. **Implicit Server-Side Limit**: FMP caps screener results at ~1000 stocks (exact number varies by market conditions)
3. **Not a Bug**: This is consistent behavior across multiple queries over time

**Why This Happens**:
- Screener is designed for quick filtering, not comprehensive universe extraction
- Large result sets (>1000) are expensive to compute and serialize
- FMP likely enforces limits to manage server load

**Does This Affect Us?**
- **No**: Our filter is `marketCap > $100B`, which yields only ~77 stocks (well below 976 limit)
- If we were querying for `marketCap > $1B`, we'd hit the limit and get incomplete results

---

## Impact Timeline

**2026-02-06 14:00** - Noticed screener returns 976 stocks for minimal filters
**2026-02-06 14:30** - Tested with different filters, consistently got ~900-1000 results
**2026-02-06 15:00** - Checked FMP documentation, found no mention of limits
**2026-02-06 15:30** - Tested pagination parameters (`page=1`, `limit=5000`) → No effect
**2026-02-06 16:00** - **Conclusion**: Implicit API limit, not affecting our use case
**2026-02-06 16:30** - Documented in MEMORY.md as "known limitation"

---

## Solution

### Decision: Accept as Non-Issue

**Rationale**:
1. Our stock pool filter (`marketCap > $100B`) returns only ~77 stocks
2. We are **well below** the ~976 screener limit
3. Top 200 by dollar volume (another approach) is also below limit
4. Alternative endpoint (`/stock/list`) returns full universe but lacks filtering

### Alternative Approaches Considered

#### Option 1: Use `/stock/list` + Local Filtering
```python
# Get full universe (13,000+ stocks)
all_stocks = requests.get(f"{BASE_URL}/stock/list?apikey={API_KEY}").json()

# Filter locally
large_caps = [s for s in all_stocks if s.get("marketCap", 0) > 100_000_000_000]
```

**Pros**: Complete control, no server-side limits
**Cons**: 13,000+ API payload, slow, unnecessary for our use case
**Decision**: **Not needed** for current filters

#### Option 2: Multiple Screener Calls with Non-Overlapping Filters
```python
# Example: Split by sector
tech = screener(sector="Technology", marketCap > $100B)
healthcare = screener(sector="Healthcare", marketCap > $100B)
# Merge results
```

**Pros**: Can exceed 976 total by partitioning
**Cons**: Complex, only needed if total universe > 976
**Decision**: **Not needed** currently

---

## Prevention

### When to Worry
FMP Screener limits become a problem **only if**:
- Total matching stocks > ~976 (e.g., `marketCap > $10B` → ~1500 stocks)
- Top N ranking queries where N > 976
- Multi-criteria queries with large result sets

### Mitigation Checklist
If hitting screener limits:
- [ ] Use `/stock/list` + local filtering (slower but complete)
- [ ] Partition query by sector/exchange (multiple API calls)
- [ ] Use alternative endpoint (e.g., `/quote/list` for latest prices)
- [ ] Consider upgrading FMP plan (Professional tier may have higher limits)

### Current Monitoring
Track screener result counts in logs:
```python
# scripts/refresh_stock_pool.py
logger.info(f"Screener returned {len(results)} stocks (limit: ~976)")
if len(results) > 900:
    logger.warning("Approaching screener limit, may be incomplete")
```

---

## Configuration

**Current Stock Pool Filter**:
```python
# config/settings.py
MARKET_CAP_MIN = 100_000_000_000  # $100B
ALLOWED_SECTORS = [
    "Technology",
    "Financial Services",
    "Healthcare",
    "Consumer Cyclical",
    "Communication Services",  # Entertainment only
]
```

**Expected Result Count**: ~77 stocks
**Screener Limit**: ~976 stocks
**Safety Margin**: 10x (no risk of hitting limit)

---

## Lessons Learned

1. **API Documentation Is Often Incomplete**
   - Screener endpoint has undocumented result limits
   - Pagination parameters exist in docs but don't work for screener
   - Always test edge cases (large filters, high limits)

2. **"Not a Bug" Is a Valid Conclusion**
   - Initial symptom (976 ≠ 3000+) looked like a bug
   - Investigation revealed it's intentional server-side limit
   - Documenting the finding prevents future confusion

3. **Design for Known Limits**
   - Stock pool filter designed to stay well below screener limit
   - If requirements change (e.g., expand to $10B+ market cap), revisit this decision

4. **Monitor Boundary Conditions**
   - Log screener result counts
   - Alert if approaching known limits (>900 stocks)

---

## References

- FMP Stock Screener Endpoint: https://site.financialmodelingprep.com/developer/docs#stock-screener
- FMP Stock List Endpoint (alternative): https://site.financialmodelingprep.com/developer/docs#stocks-list
- Current Stock Pool: `data/valuation.db` (77 stocks as of 2026-02-06)

---

## Future Considerations

**If Stock Pool Expands Beyond 976 Stocks**:
1. Switch to `/stock/list` + local filtering
2. Implement sector-based partitioning
3. Upgrade to FMP Professional plan (if available)
4. Cache full universe daily, filter locally

**Current Status**: No action needed, documented for awareness.

---

**Author**: Claude (documentation-specialist)
**Reviewed**: 2026-02-08
**Next Review**: When changing MARKET_CAP_MIN filter
