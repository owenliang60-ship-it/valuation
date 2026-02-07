# Risk Desk

The Risk Desk is the guardian of capital at 未来资本. It enforces investment discipline through position limits, drawdown protocols, kill conditions, and exposure monitoring.

---

## Documents

### Governance

| Document | Path | Description |
|----------|------|-------------|
| **Investment Policy Statement** | [`ips.md`](ips.md) | Master governance document: IRR hurdles, OPRMS position limits, sector caps, drawdown protocols, review cadence |

### Risk Control Rules (`rules/`)

| Document | Path | Description |
|----------|------|-------------|
| **Kill Conditions Template** | [`rules/kill-conditions-template.md`](rules/kill-conditions-template.md) | Per-position invalidation trigger template. Every position must have observable, measurable kill conditions. |
| **Earnings Calendar Protocol** | [`rules/earnings-calendar-protocol.md`](rules/earnings-calendar-protocol.md) | 5-day blackout rule, options/IV crush rules, post-earnings observation period |
| **Correlation & Diversification** | [`rules/correlation-diversification.md`](rules/correlation-diversification.md) | Correlation thresholds, effective position count, stress correlation rules |
| **Greeks Exposure Limits** | [`rules/greeks-exposure-limits.md`](rules/greeks-exposure-limits.md) | Delta/Gamma/Theta/Vega portfolio-level limits for options positions |

### Position Sizing (`sizing/`)

| Document | Path | Description |
|----------|------|-------------|
| **Position Sizing Framework** | [`sizing/position-sizing-framework.md`](sizing/position-sizing-framework.md) | Core OPRMS formula, DNA cap table, timing coefficients, evidence thresholds, scaling protocol |
| **Sensitivity Tables** | [`sizing/sensitivity-tables.md`](sizing/sensitivity-tables.md) | Regime-based scenarios (Bull/Base/Bear/Crisis) with worked examples |

---

## Dependencies on Other Desks

| Dependency | Source Desk | Status |
|-----------|------------|--------|
| OPRMS DNA + Timing ratings | Knowledge Base | Pending (knowledge/oprms/) |
| Earnings calendar data | Data Desk | Pending (FMP `earnings-calendar`, Phase 2a-2) |
| Correlation matrix | Data Desk | Pending (from price CSVs, Phase 2b-1) |
| Options Greeks data | Data Desk | Pending (Tradier/IBKR/Polygon.io, Phase 2c-1) |
| Holdings data | Portfolio Desk | Pending (portfolio/holdings/) |
| Trade journal entries | Trading Desk | Pending (trading/journal/) |

---

## Future Automation Roadmap

1. **Phase 2b-1**: Automated rolling correlation matrix from `data/price/*.csv`
2. **Phase 2a-2**: Earnings calendar integration for automated blackout enforcement
3. **Phase 2c-1**: Options data source for live Greeks monitoring
4. **Phase 2c-2**: VIX + credit spread integration for regime detection
5. **Phase 3**: Telegram alerts on limit breaches
