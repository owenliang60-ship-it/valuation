# Strategy Library

Playbooks for recurring trade types. Each strategy defines entry criteria, sizing rules, exit protocol, and risk controls. Strategies are tied to the OPRMS rating system and the four investment buckets.

## Strategy Index

### Equity Strategies

| Strategy | Bucket | Typical Horizon | Key Signal |
|----------|--------|----------------|------------|
| [Compounder Accumulation](equity/compounder-accumulation.md) | Long-term Compounder | 3+ years | Quality + durable moat |
| [Catalyst-Driven](equity/catalyst-driven.md) | Catalyst-Driven Long | 6-18 months | Identified catalyst with timeline |
| [Breakout/Pullback](equity/breakout-pullback.md) | Any long bucket | Weeks to months | PMARP + RVOL technical signals |
| [Mean Reversion](equity/mean-reversion.md) | Long-term Compounder | Weeks to months | PMARP < 20% on high-conviction names |

### Options Strategies

| Strategy | Use Case | Max Risk | Key Constraint |
|----------|----------|----------|---------------|
| [Covered Calls](options/covered-calls.md) | Income on existing longs | Opportunity cost (capped upside) | No CCs through earnings |
| [Cash-Secured Puts](options/cash-secured-puts.md) | Accumulate watchlist names | Strike x 100 x contracts | Only on DNA A+ rated stocks |
| [Earnings Plays](options/earnings-plays.md) | Defined-risk earnings bets | 1-2% of portfolio | Defined risk structures only |
| [Spread Structures](options/spread-structures.md) | Directional with defined risk | Max spread width | Greeks-aware sizing |

## How Strategies Connect to OPRMS

```
DNA Rating (Asset Quality)     Timing Rating (Market Timing)
        |                               |
        v                               v
  Max Position Cap              Position Multiplier
  S=25%, A=15%,                 S=1.0-1.5x, A=0.8-1.0x
  B=7%, C=2%                    B=0.4-0.6x, C=0.1-0.3x
        |                               |
        +-----------> Position = Total Capital x DNA_cap x Timing_coeff
```

Each strategy specifies which DNA/Timing ratings are appropriate for its use.

## Adding New Strategies

Use [strategy-template.md](strategy-template.md) as a starting point. Every strategy must include:
1. Overview and rationale
2. Entry criteria (specific, observable conditions)
3. Sizing rules (tied to OPRMS)
4. Exit protocol (profit target, stop loss, thesis invalidation)
5. Risk controls (max loss, earnings blackout, correlation limits)
