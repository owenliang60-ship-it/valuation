# Strategy: Compounder Accumulation

> Category: Equity
> Investment Bucket: Long-term Compounder
> Typical Horizon: 3+ years
> Last Updated: 2026-02-07

---

## Overview

Systematic accumulation of the highest-quality businesses at attractive prices. These are "forever" holdings -- companies with durable competitive advantages, high ROIC, and long reinvestment runways. The edge is patience and conviction: building large positions in extraordinary businesses when the market offers temporary discounts.

This strategy maps directly to the Quality Compounder lens from the six investment philosophies.

## Entry Criteria

### Required Conditions
- [ ] DNA rating of S or A (proven compounder with durable moat)
- [ ] ROIC > 15% sustained over 5+ years
- [ ] Revenue and earnings growth trajectory intact
- [ ] Business model with high switching costs, network effects, or scale advantages
- [ ] Price at or below action price from investment memo
- [ ] Full investment memo completed with score >= 7.0/10

### OPRMS Requirements
- **Minimum DNA Rating**: A (preferably S)
- **Minimum Timing Rating**: B (will accumulate on normal pullbacks)
- **Preferred Conditions**: DNA S + Timing A or better for full-speed accumulation

### Pre-Entry Checklist
- [ ] Thesis documented in trade journal
- [ ] Kill conditions defined (fundamental only, not price-based)
- [ ] Not within 5 trading days of earnings
- [ ] Position size calculated per OPRMS
- [ ] Checked correlation with existing compounder positions

## Sizing Rules

- **Initial Position**: 30-40% of target position (first tranche)
- **Scaling Plan**: 3-5 tranches over weeks to months. Add on:
  - Price pullbacks to lower action price tiers (if thesis intact)
  - Timing rating upgrade (e.g., B -> A after breakout confirmation)
  - Positive fundamental catalysts (earnings beat, guidance raise)
- **Max Position**: DNA_cap x Timing_coeff (S=25%, A=15%)
- **Sizing Formula**: `Position = Total Capital x DNA_cap x Timing_coeff`
  - Example: $5M portfolio, DNA S (25%), Timing B (0.5x) = $625K max = 12.5%
  - As Timing improves to A (0.9x): $1.125M = 22.5%

## Exit Protocol

### Profit Taking
- **No profit-taking on price alone.** Compounders are held as long as the thesis is intact.
- Trim only if: position exceeds DNA_cap at Timing S (25% x 1.5 = 37.5%), or if rebalancing needed for new opportunity of equal/higher conviction.

### Stop Loss
- **No price-based stop losses.** Compounders are not managed by price -- they are managed by thesis.
- A 30% drawdown on a DNA S stock is a buying opportunity, not a sell signal, unless kill conditions are triggered.

### Thesis Invalidation
- Exit when kill conditions are triggered. Examples of compounder kill conditions:
  - ROIC drops below cost of capital for 2+ consecutive years
  - Competitive moat permanently breached (new technology, regulation)
  - Management makes capital allocation decisions that destroy value (overpriced acquisitions, excessive dilution)
  - Revenue growth turns negative for 3+ consecutive quarters without cyclical explanation

## Risk Controls

- **Max loss per trade**: No hard stop. Risk is managed through conviction level (DNA rating) and position sizing.
- **Earnings protocol**: Maintain position through earnings. No pre-earnings trimming for compounders -- the edge IS holding through volatility. Exception: if position is >20% and earnings are binary (regulatory decision, etc.), reduce to 15%.
- **Correlation check**: No more than 40% of portfolio in compounders with >0.7 correlation to each other.
- **Max concurrent positions**: No hard limit, but practically 3-5 compounder positions (at 10-25% each, they fill the portfolio).
- **Review cadence**: Quarterly thesis review. Annual deep-dive with updated investment memo.

## Examples

| Trade ID | Symbol | Result | Key Lesson |
|----------|--------|--------|------------|
| [Example: 2026-01-15-AAPL-LONG] | AAPL | +9.3% (exited early) | Pre-earnings exit violated compounder discipline |

## Lessons Log

| Date | Lesson | Source Trade |
|------|--------|-------------|
| 2026-02-07 | Pre-earnings exits on compounders convert long-term thesis into short-term swing trades. Define earnings-bridge protocol upfront. | AAPL-long-example |
