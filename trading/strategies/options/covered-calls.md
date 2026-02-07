# Strategy: Covered Calls

> Category: Options
> Use Case: Income generation / premium capture on existing long equity positions
> Max Risk: Opportunity cost (capped upside above strike)
> Last Updated: 2026-02-07

---

## Overview

Sell call options against existing long equity positions to generate income and reduce cost basis. The trade-off is capping upside potential at the strike price. Best used when a stock is near or above fair value with limited near-term upside catalysts, but you want to maintain the core long position.

**When to use**: stock is range-bound or slightly overvalued, no major catalyst imminent, you want yield while waiting.

**When NOT to use**: stock is in active breakout (PMARP > 90%), earnings within 30 days, or you expect a significant move higher.

## Entry Criteria

### Required Conditions
- [ ] Own at least 100 shares of the underlying (per contract)
- [ ] Stock at or above fair value estimate (no desire to add at current prices)
- [ ] No major catalyst expected within the option's expiration window
- [ ] IV rank > 30% (sufficient premium to justify the trade)
- [ ] Willing to be called away at the strike price (or willing to roll)

### OPRMS Context
- Works on any DNA rating with existing position
- Timing B or C preferred (range-bound, no strong trend)
- Do NOT sell covered calls on Timing S or A stocks (you are capping a winner)

### Pre-Entry Checklist
- [ ] Checked earnings calendar: no earnings before expiration
- [ ] Calculated premium as annualized yield (target > 8% annualized)
- [ ] Confirmed strike price is above cost basis (avoid locking in a loss)
- [ ] Assessed probability of assignment and willingness to accept it

## Strike and Expiry Selection

### Expiry
- **Target**: 30-45 DTE (optimal theta decay zone)
- **Range**: 21-60 DTE acceptable
- **Never**: weekly options (gamma risk too high) or >90 DTE (capital tied up too long)

### Strike
- **Standard**: 0.20-0.30 delta OTM (70-80% probability of expiring worthless)
- **Aggressive** (higher income, more assignment risk): 0.30-0.40 delta
- **Conservative** (lower income, safer): 0.10-0.20 delta
- **Rule**: strike must be above your cost basis

### Premium Target
- Minimum: 0.5% of underlying value per month (6% annualized)
- Target: 0.8-1.5% per month (10-18% annualized)
- If premium is < 0.5%/month, the trade is not worth the cap on upside

## Sizing Rules

- **Per contract**: 100 shares of underlying per call sold
- **Coverage**: Up to 100% of long equity position
- **Partial coverage**: Sell calls on 50-75% of position if you want some uncapped upside exposure
- **Max contracts**: total shares / 100 (never sell naked)

## Exit Protocol

### Profit Taking
- **Close at 50% profit**: If the call loses 50% of its value quickly, buy it back. Captures most of the premium with less time exposed to risk.
- **Close at 21 DTE**: If still open at 21 DTE, close and roll to next cycle. Gamma risk increases in final weeks.

### Rolling
- **Roll out and up**: If stock moves toward strike, roll to the next monthly cycle at a higher strike for a net credit.
- **Never roll for a net debit**. If you can't roll for a credit, let it get assigned or close the position.
- **Roll timing**: when stock is within 2% of strike and >7 DTE remaining.

### Assignment
- If assigned, evaluate: is this a stock you want to re-enter?
  - Yes: sell cash-secured puts to re-enter at a lower price
  - No: take the profit and redeploy capital

## Risk Controls

- **Earnings blackout**: NO covered calls through earnings. Close or roll before earnings. Earnings can cause gaps that make assignment painful.
- **Breakout risk**: If PMARP crosses above 90% while a CC is open, consider closing the call at a loss to preserve upside. The opportunity cost of capping a breakout is real.
- **Max covered call positions**: No limit, but track the total upside you are capping. If >50% of portfolio has covered calls, you are heavily betting on sideways.
- **Assignment tax impact**: Track short-term vs. long-term capital gains implications of potential assignment.

## Greeks Profile

| Greek | Target | Risk |
|-------|--------|------|
| Delta | -0.20 to -0.30 per contract | Stock rallies hard, opportunity cost |
| Theta | Positive (this is the income source) | Time is on your side |
| Vega | Negative (benefits from IV crush) | IV spike hurts mark-to-market |
| Gamma | Low at 30-45 DTE | Increases near expiry -- close early |

## Examples

| Trade ID | Symbol | Strike/Expiry | Premium | Outcome | Key Lesson |
|----------|--------|--------------|---------|---------|------------|
| [To be filled] | | | | | |

## Lessons Log

| Date | Lesson | Source Trade |
|------|--------|-------------|
| | | |
