# Strategy: Mean Reversion

> Category: Equity
> Investment Bucket: Long-term Compounder (opportunistic entry)
> Typical Horizon: Weeks to months
> Last Updated: 2026-02-07

---

## Overview

Counter-trend strategy for building positions in high-conviction names when they are deeply oversold. Targets situations where the market has overreacted to short-term news, pushing excellent businesses to statistically extreme low valuations. The edge is conviction in the fundamental thesis combined with statistical mean reversion of price momentum indicators.

This is a "buy the dip" strategy with discipline -- only for stocks you would hold at higher prices, only at extreme readings, and only when fundamentals remain intact.

## Entry Criteria

### Required Conditions
- [ ] PMARP < 20th percentile (statistically oversold relative to recent history)
- [ ] DNA rating S or A (only buy dips on highest-quality names)
- [ ] No fundamental deterioration explaining the decline (kill conditions NOT triggered)
- [ ] Decline driven by: market-wide selloff, sector rotation, sentiment, or short-term earnings miss with intact long-term thesis
- [ ] Forward P/E at or below 5-year average (valuation support)

### Disqualifying Conditions
- Fundamental kill condition triggered (competitive moat breached, accounting issues)
- Decline driven by structural change in the business
- PMARP < 5th percentile on company-specific negative news (may be justified decline)
- DNA rating B or C (insufficient conviction for counter-trend entry)

### OPRMS Requirements
- **Minimum DNA Rating**: A (S preferred; mean reversion requires high conviction)
- **Timing Rating**: C or B (this is the definition of poor timing -- the strategy is about upgrading Timing as reversion occurs)
- **Preferred Conditions**: DNA S with Timing C (maximum conviction at maximum pessimism)

### Pre-Entry Checklist
- [ ] Confirmed that decline is NOT fundamentally justified
- [ ] Checked last earnings report for any thesis-breaking changes
- [ ] Verified no pending negative catalysts (regulatory, legal, competitive)
- [ ] Position size reflects low Timing coefficient (small initial)
- [ ] Defined add levels and conditions for scaling in

## Sizing Rules

- **Initial Position**: 0.5x Timing_coeff applied to DNA_cap (very small start)
  - Example: DNA S (25%), Timing C (0.2x) = 5% max, start at 2.5%
- **Scaling Plan**: Add as mean reversion confirms
  - Add at PMARP 30%: bring to 1.0x Timing_coeff
  - Add at PMARP 50%: upgrade Timing to B, recalculate position
  - Full position when PMARP > 70% (reversion confirmed, Timing upgraded to A)
- **Max Position**: DNA_cap x upgraded Timing_coeff (position grows as timing improves)
- **Key principle**: Never go to full position size on a mean reversion entry. Let the reversion prove itself.

## Exit Protocol

### Profit Taking
- **Primary target**: PMARP reversion to 50-70% range. Take initial profits (30-50% of position).
- **Secondary target**: PMARP > 80%. Evaluate whether to convert to compounder hold or take remaining profits.
- **Conversion**: If thesis remains strong at PMARP 70%+, convert to Compounder Accumulation strategy and update trade journal.

### Stop Loss
- **Max loss**: 10% from average entry price. Mean reversion can fail if the decline is fundamentally justified.
- **Time stop**: If PMARP remains below 20% for 30+ trading days, reduce position by 50% and reassess.
- **Escalating stop**: If PMARP drops below 5% after entry, exit immediately. This suggests the decline is not mean-reverting.

### Thesis Invalidation
- Any kill condition triggered during the dip
- New information reveals the decline is fundamentally justified
- Company issues earnings warning or guidance cut
- Management change that undermines the quality thesis

## Risk Controls

- **Max loss per trade**: 10% from entry
- **Max exposure to mean reversion trades**: 15% of total portfolio. These are inherently high-risk entries.
- **Earnings protocol**: Do not initiate mean reversion entries within 10 trading days of earnings. A stock at PMARP < 20% heading into earnings is especially dangerous.
- **Correlation check**: No more than 2 mean reversion trades in the same sector (sector-wide selloffs mean reversion is correlated).
- **Max concurrent positions**: 2-3. These require monitoring and conviction.
- **Dollar-cost averaging floor**: Define a maximum number of add levels (3). If the stock keeps falling past your third add, stop adding and wait.

## Examples

| Trade ID | Symbol | PMARP at Entry | Result | Key Lesson |
|----------|--------|---------------|--------|------------|
| [To be filled with actual trades] | | | | |

## Lessons Log

| Date | Lesson | Source Trade |
|------|--------|-------------|
| | | |
