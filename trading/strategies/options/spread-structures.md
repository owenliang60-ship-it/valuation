# Strategy: Spread Structures

> Category: Options
> Use Case: Directional bets with defined risk and capital efficiency
> Max Risk: Max spread width x contracts x 100
> Last Updated: 2026-02-07

---

## Overview

Options spread strategies for expressing directional or volatility views with defined risk. Spreads are more capital-efficient than outright stock positions and provide explicit maximum loss. This strategy covers vertical spreads, calendar spreads, and diagonal spreads.

**When to use**: You have a directional view and want defined risk, or you have a view on implied volatility term structure.

**When NOT to use**: High urgency (spreads can have wide bid-ask), earnings within the spread window (use Earnings Plays strategy instead), or illiquid options chains.

## Spread Types

### Vertical Spreads (Same Expiry, Different Strikes)

#### Bull Call Spread (Moderately Bullish)
- **Structure**: Buy lower strike call, sell higher strike call, same expiry
- **Max profit**: Width of strikes - net debit
- **Max loss**: Net debit paid
- **Use when**: Moderately bullish, want to reduce cost of long call

#### Bear Put Spread (Moderately Bearish)
- **Structure**: Buy higher strike put, sell lower strike put, same expiry
- **Max profit**: Width of strikes - net debit
- **Max loss**: Net debit paid
- **Use when**: Moderately bearish, defined-risk short thesis

#### Bull Put Spread / Credit Spread (Mildly Bullish)
- **Structure**: Sell higher strike put, buy lower strike put, same expiry
- **Max profit**: Net credit received
- **Max loss**: Width of strikes - net credit
- **Use when**: Mildly bullish, want income with defined risk (alternative to CSP)

#### Bear Call Spread / Credit Spread (Mildly Bearish)
- **Structure**: Sell lower strike call, buy higher strike call, same expiry
- **Max profit**: Net credit received
- **Max loss**: Width of strikes - net credit
- **Use when**: Mildly bearish, want income with defined risk

### Calendar Spreads (Same Strike, Different Expiries)

#### Long Calendar
- **Structure**: Sell near-term option, buy longer-term option, same strike
- **Use when**: Expect low volatility near-term, higher later. Or stock near a level where you expect it to stay short-term.
- **Max loss**: Net debit paid
- **Key risk**: Large move in either direction; near-term vol spike

#### Short Calendar
- **Structure**: Buy near-term, sell longer-term, same strike
- **Use when**: Expect a large move soon. Near-term IV higher than longer-term.
- **Rarely used**. More exotic.

### Diagonal Spreads (Different Strike AND Different Expiry)

#### Long Diagonal (Poor Man's Covered Call / Put)
- **Structure**: Buy longer-dated deep ITM option, sell shorter-dated OTM option
- **Use when**: Want covered call/put exposure with less capital
- **Behaves like**: Covered call but with less capital commitment and slightly different Greeks
- **Key advantage**: Capital-efficient way to replicate CC/CSP strategy

## Entry Criteria

### Required Conditions
- [ ] Directional thesis documented (or vol thesis for calendars)
- [ ] Max loss calculated before entry
- [ ] Bid-ask spread on all legs is < 5% of the option price (liquidity check)
- [ ] IV assessment: is current IV favorable for the spread type?
  - Selling premium (credit spreads): IV rank > 30% preferred
  - Buying premium (debit spreads): IV rank < 50% preferred
- [ ] Underlying stock has weekly or monthly options with sufficient open interest (>500 OI per leg)

### OPRMS Integration
- Directional spreads should align with OPRMS Timing assessment
- Timing A/S: favor debit spreads (directional conviction)
- Timing B/C: favor credit spreads (range-bound income)
- Position size at max loss must not exceed OPRMS position limits

### Pre-Entry Checklist
- [ ] All legs priced and max loss calculated
- [ ] No earnings within the spread window
- [ ] Liquidity verified (OI and bid-ask)
- [ ] Greeks profile assessed (see below)
- [ ] Exit rules defined for profit, loss, and time

## Strike and Expiry Selection

### Verticals
- **Width**: $5-$10 on stocks $100-300, $10-$20 on stocks $300+
- **Expiry**: 30-45 DTE for credit spreads, 45-60 DTE for debit spreads
- **Delta of short leg**: 0.20-0.35 for credit spreads

### Calendars
- **Strike**: ATM or slightly OTM in expected direction
- **Near-term expiry**: 21-30 DTE
- **Long-term expiry**: 45-90 DTE
- **Gap**: at least 3 weeks between expiries

### Diagonals
- **Long leg**: deep ITM (delta 0.70-0.80), 90-120 DTE
- **Short leg**: OTM (delta 0.20-0.30), 30-45 DTE
- **Roll short leg monthly** while maintaining long leg

## Sizing Rules

- **Max loss per spread**: 1-3% of portfolio
  - Standard: 1-2%
  - High conviction: up to 3% (requires OPRMS DNA A+ and documented thesis)
- **Number of contracts**: `Max acceptable loss / Max loss per contract`
- **Max concurrent spread positions**: 5-6
- **Never size based on max profit**. Always size based on max loss.

## Exit Protocol

### Profit Taking
- **Credit spreads**: Close at 50% of max profit. If you collected $2 credit, close when spread is worth $1.
- **Debit spreads**: Close at 50-75% of max profit, or when underlying reaches target.
- **Calendars**: Close when near-term option decays and spread value peaks.

### Loss Management
- **Credit spreads**: Close at 2x the credit received (e.g., sold for $2, close at $4 = $2 loss)
- **Debit spreads**: Close at 50% loss of premium paid
- **Time-based**: Close all spreads at 14 DTE if not already closed (gamma risk)

### Rolling
- **Credit spreads**: Roll out and away from the short strike for a net credit
- **Diagonals**: Roll the short leg each month; maintain the long leg
- **Never roll for a net debit**

## Greeks Management

| Spread Type | Delta | Theta | Vega | Gamma |
|-------------|-------|-------|------|-------|
| Bull call spread | Positive | Mixed | Mixed | Low |
| Bear put spread | Negative | Mixed | Mixed | Low |
| Credit put spread | Positive | Positive | Negative | Low |
| Credit call spread | Negative | Positive | Negative | Low |
| Long calendar | Neutral | Positive | Positive | Low |
| Long diagonal | Positive/Negative | Positive | Mixed | Low |

**Key principle**: Spreads should have low gamma. If net gamma exposure becomes significant, the position needs active management.

## Risk Controls

- **Max loss**: hard cap per trade (1-3% of portfolio)
- **No earnings**: close all spreads before earnings
- **Liquidity**: only trade spreads on underlyings with average daily option volume > 10K contracts
- **Correlation**: no more than 3 spread positions in the same sector
- **Assignment risk**: monitor short legs as they approach ITM. Close or roll before expiry if ITM.
- **Margin**: track margin requirements for credit spreads. Never use more than 50% of available margin.

## Examples

| Trade ID | Symbol | Structure | Max Loss | Outcome | Key Lesson |
|----------|--------|-----------|----------|---------|------------|
| [To be filled] | | | | | |

## Lessons Log

| Date | Lesson | Source Trade |
|------|--------|-------------|
| | | |
