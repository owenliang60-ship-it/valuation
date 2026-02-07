# Trade Journal Entry

> Trade ID: 2026-01-15-AAPL-LONG
> Status: closed
> Created: 2026-01-15
> Strategy: equity/compounder-accumulation

---

## Pre-Trade

### Identification

- **Symbol**: AAPL
- **Direction**: Long
- **Instrument**: Equity
- **Investment Bucket**: Long-term Compounder

### Thesis

**Falsifiable thesis statement**:

> Apple Intelligence will drive a Services revenue inflection, pushing Services growth from 14% to 20%+ YoY within the next 3 quarters, as AI features create new monetization channels (premium AI subscriptions, enhanced App Store discovery) and accelerate the iPhone upgrade cycle in the installed base of 2.2B active devices.

**Variant view**:

> Market is pricing AAPL as a mature hardware company with decelerating growth. Consensus underestimates the compounding effect of AI-driven services monetization on the highest-quality installed base in tech. The Services gross margin expansion (now 75%+) is being obscured by flat hardware margins in blended reporting.

**Key forces**:

1. Apple Intelligence adoption driving premium subscription tier ($10-20/mo potential)
2. iPhone upgrade cycle acceleration as AI features require newer silicon (A17 Pro+)
3. Services flywheel: higher engagement -> more App Store revenue -> higher developer investment

### Kill Conditions

| # | Condition | Threshold | Action |
|---|-----------|-----------|--------|
| 1 | Services revenue growth deceleration | Growth drops below 12% YoY for 2 consecutive quarters | Exit full |
| 2 | iPhone unit decline | Units decline >10% YoY for 2 consecutive quarters without Services offset | Review immediately |
| 3 | Gross margin compression | Consolidated gross margin falls below 44% for 2 consecutive quarters | Exit half |

### Pricing and Sizing

- **OPRMS DNA Rating**: S
- **OPRMS Timing Rating**: B
- **Max Position** (25% x 0.5): 12.5%
- **Target Position**: 10%
- **Action Price**: $225
- **Target IRR**: 18%
- **Entry Rules**: Buy first tranche (40%) at $225, second tranche (30%) at $215, final tranche (30%) at $205 if thesis intact

### Evidence

**Primary sources (3+ required):**

| # | Type | Description | Date |
|---|------|-------------|------|
| 1 | Earnings call | Q4 2025 earnings call -- Tim Cook commentary on Apple Intelligence adoption metrics | 2025-10-31 |
| 2 | Conference | Goldman Sachs Communacopia -- SVP Services detailed AI monetization roadmap | 2025-09-10 |
| 3 | Customer feedback | App Annie data showing 25% increase in daily active usage post-Apple Intelligence launch | 2025-12-15 |
| 4 | Insider trading | CFO purchased $2M in open market, largest purchase in 3 years | 2025-11-20 |

**Total source count**: 9 / 8-10+ target

### Pre-Trade Checklist

- [x] Thesis is falsifiable
- [x] Variant view is clearly stated
- [x] Kill conditions are observable and measurable
- [x] Target IRR clears hurdle (18% >= 15%)
- [x] Position size within OPRMS limits (10% <= 12.5% max)
- [x] Not within 5 trading days of earnings (next ER: 2026-01-30, entry: 2026-01-15 = 11 trading days)
- [x] 3+ primary evidence sources documented (4 primary)
- [x] Linked to investment memo: AAPL-2026-Q1-MEMO

---

## Execution

### Entries

| Date | Price | Quantity | Order Type | Notes |
|------|-------|----------|------------|-------|
| 2026-01-15 | $223.50 | 200 | Limit | First tranche, filled below action price |
| 2026-01-22 | $218.30 | 150 | Limit | Second tranche on market pullback |

- **Avg Entry Price**: $221.28
- **Total Quantity**: 350 shares
- **Actual Position %**: 7.2%
- **Slippage (bps)**: -166 bps (filled better than action price)
- **Sizing Rationale**: Scaled into 2 of 3 planned tranches. Third tranche ($205) not triggered. 7.2% is within Timing B range (12.5% max), leaving room to add on Timing upgrade.
- **Broker**: IBKR

---

## Post-Trade

### Exits

| Date | Price | Quantity | Reason |
|------|-------|----------|--------|
| 2026-02-05 | $241.80 | 350 | Pre-earnings risk reduction -- sold ahead of Q1 ER to lock in gains |

- **Avg Exit Price**: $241.80
- **Realized P&L**: $7,182 (+9.3%)
- **Hold Period**: 21 days (15 days from first entry, 14 from second)

### Thesis Assessment

- **Thesis Accuracy**: Partially Validated -- Services growth thesis intact but position was closed before the catalysts fully played out due to earnings risk management
- **Kill Condition Triggered**: N/A
- **What actually happened vs. thesis**: Stock rallied on broader market momentum and pre-earnings anticipation. The core AI thesis remains untested until Q1 2026 ER reveals Apple Intelligence metrics. Decided to take profit and reassess post-earnings.

### Lessons

1. Entry execution was strong (better than action price), but closing before the thesis was tested means this was more of a swing trade than a compounder accumulation
2. Need clearer rules for distinguishing "take profit" from "thesis exit" -- pre-earnings reduction is valid risk management but should be pre-defined in the entry rules
3. Consider building earnings-bridge protocol: reduce to 50% pre-ER, add back post-ER if thesis confirmed

### Review Link

Post-trade review: [review/examples/sample-review.md]
