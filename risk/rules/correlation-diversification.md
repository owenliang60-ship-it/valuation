# Correlation-Based Diversification Rules

> "You think you're diversified, but you're actually making one big bet."
>
> This document defines rules for measuring and enforcing true diversification
> beyond simple position count.

---

## Data Dependency

- **Required**: Rolling correlation matrix from `data/price/*.csv` (Phase 2b-1 in roadmap)
- **Current status**: Not yet implemented. 77 stocks with 5-year daily price data available.
- **Interim**: Apply qualitative sector/thesis overlap assessment for new positions

---

## Core Rules

### Rule 1: Correlation Threshold

**If the 60-day rolling Pearson correlation between any two portfolio positions exceeds 0.80, treat them as a single concentrated bet for sizing purposes.**

What this means in practice:
- Combined weight of two positions with correlation > 0.80 must not exceed the higher DNA cap of the pair
- Example: MSFT (S-tier, 25% cap) and AAPL (A-tier, 15% cap) with correlation 0.85 → combined weight capped at 25%, not 40%

### Rule 2: Effective Position Count

**Portfolio must maintain >= 5 effective positions at all times.**

Effective position count is calculated using the Herfindahl-Hirschman Index (HHI):

```
Effective Positions = 1 / sum(w_i^2)

where w_i = weight of position i (as a decimal)
```

Examples:
- 5 equal positions (20% each): 1 / (5 * 0.04) = 5.0
- 1 position at 40% + 4 at 15%: 1 / (0.16 + 4*0.0225) = 1 / 0.25 = 4.0 (VIOLATION)
- 1 position at 25% + 3 at 15% + 4 at 5%: 1 / (0.0625 + 3*0.0225 + 4*0.0025) = 1 / 0.14 = 7.1

Action on violation: No new positions until either (a) existing positions are trimmed to restore effective count >= 5, or (b) new position itself restores the count.

### Rule 3: Sector Correlation Awareness

Known high-correlation clusters in the large-cap universe (to be validated with data):

| Cluster | Typical Correlation | Members (examples) |
|---------|--------------------|--------------------|
| Mega-cap Tech | 0.70-0.85 | AAPL, MSFT, GOOGL, AMZN, META |
| Semiconductors | 0.75-0.90 | NVDA, AMD, AVGO, TSM |
| Financials | 0.65-0.80 | JPM, GS, MS, BAC |
| Streaming/Entertainment | 0.60-0.75 | NFLX, DIS, SPOT |
| Healthcare/Pharma | 0.50-0.65 | LLY, UNH, JNJ, ABBV |

**Rule**: Within a known high-correlation cluster, total portfolio weight must not exceed 1.5x the highest individual DNA cap.
- Example: Semiconductor cluster → if best name is S-tier (25%), total semi exposure capped at 37.5%

### Rule 4: Thesis Overlap

Even if statistical correlation is low, positions with overlapping thesis drivers should be flagged:

| Overlap Type | Example | Risk |
|-------------|---------|------|
| Same macro driver | Multiple AI plays (NVDA + MSFT + GOOGL) all depend on AI capex cycle | AI spending slowdown hits all simultaneously |
| Same customer concentration | Multiple companies with Apple as top customer | Apple supply chain shift hits all |
| Same regulatory risk | Multiple Big Tech names facing antitrust | Regulatory action is correlated |
| Same interest rate sensitivity | Growth stocks with similar duration profile | Rate shock hits all |

**Action**: Document thesis overlap for every new position. If 3+ positions share the same primary thesis driver, treat the cluster as a single bet and apply cluster sizing limits.

---

## Stress Correlation Rules

### Crisis Correlation Convergence

In market stress (VIX > 30, or portfolio drawdown > -10%), assume:
- All equity correlations converge toward 0.90
- Effective diversification benefit drops to near zero
- Portfolio behaves as a single leveraged position in "equities"

### Stress-Adjusted Exposure

When in defensive posture (per IPS drawdown protocols):

```
Stress-Adjusted Equity Exposure = Sum of all equity weights * Average Stress Correlation

If Stress Correlation = 0.90 and total equity = 80%:
  Effective exposure = 80% * 0.90 = 72% (of a single-factor bet)
```

This is why the IPS requires reducing equity exposure in drawdowns -- the diversification you think you have disappears.

---

## Measurement and Monitoring

### Metrics to Track (Future Automation)

| Metric | Frequency | Threshold | Action |
|--------|-----------|-----------|--------|
| Pairwise 60-day correlation | Weekly | > 0.80 for any held pair | Review combined sizing |
| Effective position count (HHI) | Weekly | < 5.0 | Trim or diversify |
| Sector cluster weight | Weekly | > 1.5x highest DNA cap | Review cluster exposure |
| Average portfolio correlation | Monthly | > 0.60 | Portfolio is too concentrated in one theme |

### Implementation Plan

1. **Phase 2b-1**: Python script to compute 60/120-day rolling correlation matrix from `data/price/*.csv`
2. **Output**: `risk/correlation/` directory with correlation matrix CSV, updated weekly
3. **Alerts**: Flag pairs exceeding 0.80, compute effective position count, identify clusters
4. **Dashboard**: Future integration with Portfolio Desk weekly snapshot

---

## Interim Manual Process

Until automated correlation monitoring is built:

1. Before adding a new position, qualitatively assess correlation with existing holdings
2. Check: Is the new name in the same sector? Same macro driver? Same customer base?
3. If 2+ overlap factors exist, explicitly document why the position adds true diversification
4. Use free tools (e.g., portfolio visualizer) for spot-check correlation analysis on existing holdings quarterly
