# Trading Desk

The Trading Desk manages trade lifecycle from thesis to execution to review. It enforces discipline: no trade enters without a falsifiable thesis, variant view, kill conditions, and target IRR.

## Components

| Component | Directory | Purpose |
|-----------|-----------|---------|
| **Trade Journal** | `journal/` | Structured record of every trade: pre-trade thesis, execution details, post-trade P&L |
| **Strategy Library** | `strategies/` | Playbooks for equity and options strategies with entry/sizing/exit rules |
| **Post-Trade Review** | `review/` | Systematic extraction of lessons from closed trades |

## Trade Lifecycle

```
1. PLAN        Write pre-trade entry in journal (thesis, variant view, kill conditions, IRR)
     |
2. VALIDATE    Check against Risk Desk IPS limits and earnings calendar
     |
3. EXECUTE     Record execution details (price, slippage, sizing)
     |
4. MANAGE      Monitor kill conditions and observable milestones
     |
5. CLOSE       Record exit and realized P&L
     |
6. REVIEW      Complete post-trade review within 48 hours
     |
7. LEARN       Extract lessons → feed back to Knowledge Base + Strategy Library
```

## Hard Rules

- **IRR hurdles**: Long >= 15%, Short >= 20-25%. If returns don't clear thresholds, PASS.
- **Kill conditions required**: Every position must have observable, measurable invalidation triggers. Not calendar dates.
- **Earnings blackout**: No new positions within 5 trading days of earnings (per Risk Desk protocol).
- **Evidence threshold**: 3+ primary sources before full position, 8-10+ total sources.
- **Position sizing**: `Position = Total Capital x DNA_cap x Timing_coeff` (OPRMS system).

## Cross-Desk Dependencies

- **Risk Desk** (`risk/`): IPS position limits, earnings calendar, kill conditions validation
- **Knowledge Base** (`knowledge/`): OPRMS ratings, investment philosophy lenses, memo templates
- **Portfolio Desk** (`portfolio/`): Holdings tracking, exposure monitoring
- **Data Desk** (`src/`, `data/`): PMARP/RVOL indicators, price data, fundamental data
