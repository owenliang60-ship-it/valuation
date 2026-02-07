# Greeks Exposure Limits

> Portfolio-level limits on options Greeks exposure.
> Greeks measure the sensitivity of options positions to various market factors.
> Without limits, options can create hidden leverage and tail risk.

---

## Data Dependency

- **Required**: Live options data (Greeks per position) from Tradier / IBKR / Polygon.io (Phase 2c-1)
- **Current status**: No options data source integrated. FMP does not provide options data at any tier.
- **Interim**: Manual calculation of Greeks at trade entry. Track in spreadsheet or trade journal until automated dashboard exists.

---

## Greek Definitions (Quick Reference)

| Greek | Measures | Unit | Risk Type |
|-------|---------|------|-----------|
| **Delta** | Price sensitivity to $1 move in underlying | Shares equivalent | Directional risk |
| **Gamma** | Rate of change of delta per $1 move | Delta change per $1 | Convexity risk |
| **Theta** | Daily time decay | $/day | Carry cost/income |
| **Vega** | Sensitivity to 1% change in implied volatility | $/1% IV | Volatility risk |
| **Rho** | Sensitivity to 1% change in interest rates | $/1% rate | Rate risk (usually minor) |

---

## Portfolio-Level Delta Limits

Delta represents the net directional exposure of the portfolio in share-equivalent terms.

### Net Delta Exposure

| Market Regime | Max Net Long Delta | Max Net Short Delta |
|--------------|-------------------|-------------------|
| **Bull (normal)** | 120% of NAV | -30% of NAV |
| **Neutral / Range** | 100% of NAV | -20% of NAV |
| **Bear / Defensive** | 70% of NAV | -40% of NAV |
| **Crisis (IPS -20%)** | 50% of NAV | -10% of NAV |

**Calculation**: Sum of (equity positions * 1.0 delta) + (options positions * position delta * multiplier * quantity) / NAV

**Note**: 100 shares of stock = 100 delta. 1 ATM call option = ~50 delta * 100 multiplier = 5,000 notional delta per contract. Options can rapidly amplify directional exposure.

### Per-Position Delta

No single underlying's delta exposure (equity + options combined) may exceed the OPRMS DNA cap when expressed as a percentage of NAV.

---

## Gamma Limits

Gamma risk is most dangerous when short: a large move in the underlying accelerates losses. Short gamma exposure means you lose more as the market moves further against you.

### Short Gamma Budget

| Metric | Limit | Rationale |
|--------|-------|-----------|
| Net short gamma per underlying | <= 100 gamma (per 1% move, expressed as delta change) | Prevents excessive acceleration of losses |
| Total portfolio short gamma | <= 500 gamma | Portfolio-wide short convexity limit |

### Long Gamma

No explicit limit on long gamma (you are paying for protection/optionality). However, long gamma positions have theta decay costs -- see Theta limits below.

### Practical Guidance

- Selling options (covered calls, cash-secured puts, iron condors) = short gamma
- Buying options (protective puts, long calls, long straddles) = long gamma
- Avoid net short gamma into binary events (earnings, FDA decisions, elections)

---

## Theta Limits

Theta is the daily cost of maintaining options positions. Net positive theta means the portfolio earns from time decay (typically from selling options). Net negative theta means the portfolio pays for optionality.

### Daily Theta Budget

| Metric | Limit | Rationale |
|--------|-------|-----------|
| Maximum net negative theta | -0.05% of NAV per day | Cap on how much optionality costs daily |
| Maximum net positive theta | +0.10% of NAV per day | Cap on short premium exposure (correlated with short gamma risk) |

### Example

For a $5M portfolio:
- Max net negative theta: -$2,500/day (paying for protection)
- Max net positive theta: +$5,000/day (earning from premium selling)

### Earnings Theta

Pre-earnings, theta on short options positions accelerates as IV expands. Monitor theta for positions with earnings within T-5 per the earnings calendar protocol.

---

## Vega Limits

Vega measures sensitivity to implied volatility changes. Critical around earnings and macro events.

### Portfolio Vega Limits

| Metric | Limit | Rationale |
|--------|-------|-----------|
| Net vega per underlying | <= 0.5% of NAV per 1% IV change | Single-name IV exposure |
| Total portfolio net vega | <= 2.0% of NAV per 1% IV change | Portfolio-wide IV exposure |

### Example

For a $5M portfolio:
- Max net vega per name: $25,000 P&L impact per 1% IV move
- Max total portfolio vega: $100,000 P&L impact per 1% IV move

### Vega Considerations

- **Pre-earnings**: IV typically elevated. Selling vega into earnings = selling insurance before the hurricane.
- **VIX spikes**: All stock IV tends to rise. Portfolio vega exposure should be checked against VIX level.
- **Term structure**: Front-month vega is more volatile than back-month. Short-dated options carry higher vega risk per dollar invested.

---

## Combined Exposure Dashboard (Target State)

Future automated dashboard should display:

```
Portfolio Greeks Summary (as of {date})
========================================
NAV: ${total}

           | Net Value | % of NAV | Limit    | Status |
Delta      | {val}     | {pct}    | {limit}  | OK/WARN/BREACH |
Gamma      | {val}     | --       | {limit}  | OK/WARN/BREACH |
Theta/day  | {val}     | {pct}    | {limit}  | OK/WARN/BREACH |
Vega       | {val}     | {pct}    | {limit}  | OK/WARN/BREACH |

Per-Position Breakdown:
{ticker} | Delta | Gamma | Theta | Vega | DNA Cap | Exposure vs Cap |
...
```

---

## Interim Manual Tracking

Until the automated Greeks dashboard is built:

1. **At trade entry**: Calculate and record Delta, Gamma, Theta, Vega for every options position in the trade journal
2. **Weekly**: Update Greeks for all open options positions (prices change, Greeks change)
3. **Pre-earnings**: Recalculate for any position with earnings within T-5
4. **Spot check**: After any significant market move (>2% on SPY), recalculate portfolio delta

### Tools for Manual Calculation

- Broker platform (IBKR Trader Workstation has built-in Greeks)
- Options calculator websites (OptionsProfitCalculator, etc.)
- Black-Scholes formula in Python (future: integrate into Risk Desk tooling)

---

## Prohibited Exposures

| Exposure | Why |
|----------|-----|
| Undefined short gamma (naked short options) | Per IPS: naked short calls and uncovered strangles/straddles are prohibited |
| Net short vega > 3% NAV | Excessive IV expansion risk |
| Net delta > 150% NAV through options leverage | Hidden leverage beyond cash equity equivalent |

---

## Integration Points

| System | Integration |
|--------|-------------|
| **Data Desk** | Options data feed (Phase 2c-1) provides live Greeks per position |
| **Trading Desk** | Trade journal captures Greeks at entry; strategy library defines expected Greeks profile |
| **Portfolio Desk** | Holdings database includes options positions with Greeks snapshot |
| **Knowledge Base** | Greeks regime rules feed into OPRMS Timing adjustments |
