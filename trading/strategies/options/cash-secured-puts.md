# Strategy: Cash-Secured Puts

> Category: Options
> Use Case: Accumulate watchlist names at a discount, generate income while waiting
> Max Risk: Strike price x 100 x contracts (obligation to buy at strike)
> Last Updated: 2026-02-07

---

## Overview

Sell put options on stocks you want to own at lower prices. You collect premium while waiting, and if assigned, you acquire shares below the current market price (strike - premium received). This is a disciplined accumulation strategy, not a yield play -- you must genuinely want to own the stock at the strike price.

**When to use**: stock is on your watchlist, approaching action price, you have cash allocated for the purchase.

**When NOT to use**: you wouldn't buy the stock at the strike price, you are selling puts purely for income on stocks you don't want to own, or the stock has binary risk (earnings, regulatory).

## Entry Criteria

### Required Conditions
- [ ] DNA rating A or S (only sell puts on highest-conviction names)
- [ ] Stock is on active watchlist with completed investment memo
- [ ] Strike price at or below action price from the memo
- [ ] Willing and able to take assignment (cash reserved)
- [ ] No earnings within the option's expiration window
- [ ] IV rank > 25% (decent premium available)

### OPRMS Requirements
- **Minimum DNA Rating**: A (selling puts creates obligation -- must be on highest-quality names)
- **Timing Rating**: B or C (you are waiting for the stock to come to your price)
- **Preferred Conditions**: DNA S with Timing C (maximum conviction, patient accumulation)

### Pre-Entry Checklist
- [ ] Cash reserved: strike x 100 x contracts (fully secured)
- [ ] Checked earnings calendar: no earnings before expiration
- [ ] Calculated break-even (strike - premium) and confirmed it meets valuation target
- [ ] Assessed maximum loss scenario (stock goes to $0 at strike)

## Strike and Expiry Selection

### Expiry
- **Target**: 30-45 DTE
- **Range**: 21-60 DTE
- **Longer DTE acceptable** (up to 90 days) if premium is significantly better and you are comfortable with the commitment

### Strike
- **Standard**: 0.20-0.30 delta OTM (strike below current price by 5-10%)
- **Strike must be at or below your action price**. Never sell puts above the price you'd willingly pay.
- **Aggressive** (want to own the stock more): 0.30-0.40 delta (closer to current price)
- **Conservative** (want more cushion): 0.10-0.20 delta (further OTM)

### Premium Target
- Minimum: 1.0% of strike value per month
- Target: 1.5-3.0% per month
- **Break-even**: strike - premium received. This is your effective buy price if assigned.

## Sizing Rules

- **Cash required**: Strike x 100 x contracts. This cash is committed.
- **Max exposure**: Position resulting from assignment must not exceed OPRMS limits
  - If DNA S (25% max position), the value at assignment (strike x shares) must be <= 25% of portfolio
- **Scaling**: May sell additional puts at lower strikes if the stock continues to decline (but total exposure must stay within OPRMS limits)

## Exit Protocol

### Profit Taking
- **Close at 50% profit**: Buy back the put once it has lost 50% of premium value. Redeploy into next cycle.
- **Close at 21 DTE**: Manage gamma risk by closing before the final weeks.

### Rolling
- **Roll out and down**: If stock moves toward strike, roll to next monthly cycle at same or lower strike for a net credit.
- **Never roll for a net debit.** If you can't roll for a credit, accept assignment.
- **Max rolls**: 2 times. After 2 rolls, either accept assignment or close the position.

### Assignment
- **Welcome assignment** on DNA S/A names at your target price. This was the plan.
- On assignment: convert to long equity position, update trade journal from "planned" to "active"
- Immediately assess: sell covered calls on the new position if appropriate

## Risk Controls

- **Earnings blackout**: NO puts open through earnings. Close or roll before earnings regardless of profit/loss.
- **Max concurrent CSP positions**: 3-4 (each ties up significant cash)
- **Cash utilization**: Never commit more than 30% of portfolio to CSP cash reserves. Maintain flexibility.
- **Correlation**: Don't sell puts on 3 stocks in the same sector. A sector decline could mean multiple assignments simultaneously.
- **Loss management**: If the stock drops >20% below strike while position is open, close the put and reassess whether the thesis is still intact before re-entering.

## Greeks Profile

| Greek | Target | Risk |
|-------|--------|------|
| Delta | -0.20 to -0.30 per contract (short put = positive delta) | Stock falls sharply, assignment at loss |
| Theta | Positive (income source) | Time decay works for you |
| Vega | Negative | IV spike increases put value (mark-to-market loss) |
| Gamma | Low at 30-45 DTE | Increases near expiry, close early |

## Assignment Workflow

```
Put expires ITM or you accept early assignment
         |
         v
Shares deposited at strike price
         |
         v
Update trade journal: new equity position
         |
         v
Review OPRMS: does position size fit?
         |
         v
Consider covered calls on new position
```

## Examples

| Trade ID | Symbol | Strike/Expiry | Premium | Outcome | Key Lesson |
|----------|--------|--------------|---------|---------|------------|
| [To be filled] | | | | | |

## Lessons Log

| Date | Lesson | Source Trade |
|------|--------|-------------|
| | | |
