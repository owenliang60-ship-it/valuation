# Strategy: Earnings Plays

> Category: Options
> Use Case: Defined-risk bets on earnings outcomes
> Max Risk: 1-2% of portfolio per play
> Last Updated: 2026-02-07

---

## Overview

Options-based strategies to profit from earnings announcements. Earnings are binary events with known dates, making them natural options territory. The key constraint: **defined risk only**. No naked options through earnings. Every earnings play must have a known maximum loss before entry.

This strategy acknowledges that earnings are the most dangerous time for any position. Rather than avoiding earnings entirely, it provides a disciplined framework for participating with controlled risk.

## Entry Criteria

### Required Conditions
- [ ] Earnings date confirmed (from Data Desk earnings calendar)
- [ ] Defined-risk structure only (no naked calls/puts)
- [ ] Maximum loss per play <= 2% of total portfolio
- [ ] Directional view or volatility view documented in trade journal
- [ ] Pre-earnings IV assessed relative to historical (IV rank, IV percentile)

### Types of Earnings Plays

#### Directional (you have a view on the outcome)
- **Long call spread**: Bullish, expects beat + raise
- **Long put spread**: Bearish, expects miss or weak guidance
- **Long call or put** (limited to 1% max loss): Strong conviction on direction

#### Volatility (you have a view on the move size, not direction)
- **Long straddle**: Expects a larger-than-implied move in either direction
- **Long strangle**: Same thesis, wider strikes, lower cost
- **Iron condor**: Expects a smaller-than-implied move (sell volatility)
- **Butterfly**: Expects stock to land near a specific price

### OPRMS Requirements
- DNA rating is less relevant for earnings plays (these are short-term trades)
- **Key requirement**: completed investment memo or recent research on the company
- Must understand the business well enough to have a variant view on the quarter

### Pre-Entry Checklist
- [ ] Max loss calculated and documented
- [ ] Max loss <= 2% of portfolio (1% preferred)
- [ ] Entry timing: 5-10 trading days before earnings (capture pre-earnings IV build)
- [ ] Historical earnings move analysis completed (what has the stock done in past 4-8 quarters?)
- [ ] Current implied move vs. historical actual move compared
- [ ] Exit plan defined for all scenarios

## Strike and Expiry Selection

### Expiry
- **Target**: First expiry after earnings date
- **Never**: Use an expiry before earnings (defeats the purpose)
- **Weekly preferred**: Minimizes extrinsic value paid for post-earnings time

### Strikes for Directional Plays
- **Call/put spreads**: Short leg at expected move level, long leg 5-10% further OTM
- **Width**: Wide enough to capture the expected move, narrow enough to manage cost

### Strikes for Volatility Plays
- **Straddle**: ATM strikes
- **Strangle**: 1 standard deviation OTM on each side
- **Iron condor**: Short legs at 1 std dev, long legs at 1.5 std dev
- **Butterfly**: Center at expected price, wings 1 std dev out

## Sizing Rules

- **Hard max**: 2% of portfolio at risk per earnings play
- **Standard**: 1% of portfolio at risk
- **High conviction**: up to 2% (requires >7.0 memo score and variant view)
- **Multiple plays**: No more than 3 earnings plays active in the same week
- **Sizing formula**: `Max loss = Total Capital x 0.01 (or 0.02)`. Size contracts so worst case = this amount.

## Exit Protocol

### Pre-Earnings
- If position is profitable before earnings (>30%), consider taking partial profits
- If IV has expanded more than expected, directional spreads may be profitable to close before earnings

### Post-Earnings (DAY 1)
- **Close the position on the first trading day after earnings.** Do not hold earnings plays beyond the event.
- Morning gap: assess within first 30 minutes. If thesis played out, close for profit.
- IV crush: be aware that even correct directional bets can lose if the move was within implied range (IV crush kills long premium)

### Loss Management
- **Max loss is defined at entry.** The spread/structure defines the worst case.
- If the play is clearly wrong intraday after earnings, close immediately rather than hoping for recovery
- Never add to a losing earnings play

## Risk Controls

- **Hard cap**: 2% of portfolio per play, 5% aggregate across all active earnings plays
- **No naked positions**: Every earnings play must be defined risk
- **No doubling down**: One entry, one exit. No averaging into earnings plays.
- **Diversification**: No more than 2 earnings plays in the same sector in the same week
- **Frequency**: Max 4-6 earnings plays per quarter. Be selective -- only play when you have genuine variant view.
- **Track record**: Maintain win rate tracking. If win rate drops below 40% over 10+ plays, pause and review methodology.

## Historical Move Analysis Template

Before every earnings play, complete this analysis:

| Quarter | Expected Move (implied) | Actual Move | Direction | Beat/Miss |
|---------|------------------------|-------------|-----------|-----------|
| Q-1 | | | | |
| Q-2 | | | | |
| Q-3 | | | | |
| Q-4 | | | | |

**Average actual move**: ____%
**Current implied move**: ____%
**Ratio (actual/implied)**: ____

If ratio > 1.2: stock tends to move MORE than implied (favor long vol)
If ratio < 0.8: stock tends to move LESS than implied (favor short vol)

## Examples

| Trade ID | Symbol | Structure | Premium | Outcome | Key Lesson |
|----------|--------|-----------|---------|---------|------------|
| [To be filled] | | | | | |

## Lessons Log

| Date | Lesson | Source Trade |
|------|--------|-------------|
| | | |
