# Strategy: Breakout / Pullback

> Category: Equity
> Investment Bucket: Any long bucket
> Typical Horizon: Weeks to months
> Last Updated: 2026-02-07

---

## Overview

Technical entry strategy that uses the Data Desk's PMARP and RVOL indicators to time entries on momentum breakouts or pullback-to-support setups. This is primarily an entry timing strategy -- it should be paired with a fundamental thesis from another strategy (compounder or catalyst-driven). The edge is precise entry timing using quantitative signals, reducing drawdown on otherwise sound fundamental positions.

## Entry Criteria

### Breakout Entry
- [ ] PMARP crosses above 98th percentile (strong momentum confirmation)
- [ ] RVOL >= 4 sigma (anomalous volume confirming the move)
- [ ] Fundamental thesis already documented (this strategy does not replace fundamental analysis)
- [ ] Price above all major moving averages (20, 50, 120 EMA)

### Pullback Entry
- [ ] Stock previously made PMARP > 98% breakout (momentum established)
- [ ] Currently pulling back to PMARP 50-70% zone (healthy retracement)
- [ ] RVOL normalizing (< 2 sigma, not panic selling)
- [ ] Support at prior resistance or key moving average (EMA 20 or 50)

### OPRMS Requirements
- **Minimum DNA Rating**: B (need fundamental quality for any equity position)
- **Minimum Timing Rating**: A for breakout entry (the breakout itself signals A or S timing)
- **Preferred Conditions**: DNA A+ with Timing S (once-in-a-cycle breakout on a quality name)

### Pre-Entry Checklist
- [ ] Fundamental thesis exists (not a pure technical trade)
- [ ] PMARP and RVOL signals confirmed in Data Desk scan output
- [ ] Kill conditions include both technical and fundamental triggers
- [ ] Not within 5 trading days of earnings

## Sizing Rules

- **Breakout Entry**:
  - Initial: 50% of target position on breakout day
  - Add: remaining 50% on first pullback that holds above breakout level (3-5 day confirmation)
- **Pullback Entry**:
  - Initial: 40% of target position at first support level
  - Add: 30% on confirmation (bounce with rising RVOL)
  - Final: 30% on PMARP re-expansion above 80%
- **Max Position**: DNA_cap x Timing_coeff. Timing is likely A or S for breakouts.
- **Sizing Formula**: `Position = Total Capital x DNA_cap x Timing_coeff`

## Exit Protocol

### Profit Taking
- **Breakout trades**: Trail stop using PMARP. Begin taking profits when PMARP peaks and starts declining from >95th percentile.
  - Take 30% when PMARP drops below 90% from peak
  - Take 30% when PMARP drops below 75%
  - Hold remaining 40% for fundamental thesis (convert to compounder or catalyst position)
- **Pullback trades**: Target PMARP reversion to 90%+ for initial profit (50%), then manage remainder by thesis.

### Stop Loss
- **Breakout**: Stop below breakout level. If price closes below breakout price for 2 consecutive days, exit full position.
- **Pullback**: Stop below the support level targeted for entry. Max loss: 5-7% from entry.
- If fundamental thesis remains intact at stop-loss level, may re-enter on next valid signal.

### Thesis Invalidation
- Price breaks below breakout level on high volume (RVOL > 3 sigma on the breakdown)
- Fundamental kill conditions triggered (always supersede technical signals)
- PMARP collapses below 20% from a breakout entry (momentum completely lost)

## Risk Controls

- **Max loss per trade**: 5-7% from entry (technical stop)
- **Earnings protocol**: No breakout/pullback entries within 5 trading days of earnings. Existing positions should be evaluated -- if unrealized gain > 10%, consider protecting with options.
- **Correlation check**: Avoid entering multiple breakout trades in the same sector simultaneously (sector-wide breakouts often reverse together).
- **Max concurrent positions**: 3-4 active breakout/pullback trades. These require active monitoring.
- **Signal freshness**: Breakout signal valid for 3 trading days. If not acted on within 3 days, wait for next signal.

## Data Desk Integration

This strategy depends on the indicator engine:
- `scripts/scan_indicators.py --save` produces PMARP and RVOL scans
- Cloud cron runs daily scans (see Data Desk schedule)
- Alert threshold: PMARP > 98% AND RVOL >= 4 sigma

## Examples

| Trade ID | Symbol | Signal | Result | Key Lesson |
|----------|--------|--------|--------|------------|
| [To be filled with actual trades] | | | | |

## Lessons Log

| Date | Lesson | Source Trade |
|------|--------|-------------|
| | | |
