# Earnings Calendar Risk Protocol

> Earnings releases are the highest-volatility events for individual stocks.
> This protocol governs position management before, during, and after earnings.

---

## Data Dependency

- **Required**: FMP `earnings-calendar` endpoint (Phase 2a-2 in roadmap)
- **Current status**: Not yet implemented
- **Interim**: Manual check of earnings dates via broker or earnings whispers before any new position

---

## Pre-Earnings Blackout (T-5 Rule)

### Rule

**No new equity positions within 5 trading days before a scheduled earnings release.**

This applies to:
- New long equity positions
- New short equity positions
- Increasing existing equity positions (adding shares)

This does NOT apply to:
- Reducing or exiting existing positions (always permitted)
- Rolling existing options positions to manage expiry risk
- Protective puts (hedging is always permitted)

### Rationale

Earnings are binary events with unknowable outcomes. Entering a position immediately before earnings is gambling, not investing. The 5-day buffer ensures:
1. You are not chasing pre-earnings momentum
2. Your thesis is based on fundamentals, not earnings speculation
3. Options IV has already expanded, making entry expensive

---

## Options-Specific Pre-Earnings Rules

### Prohibited Before Earnings (T-5)

| Action | Reason |
|--------|--------|
| Selling puts (cash-secured or otherwise) | IV crush after earnings makes timing poor; binary gap risk |
| Selling calls (naked or covered) | Upside surprise risk; covered calls cap upside at worst time |
| Entering short volatility positions | IV will expand into earnings, causing mark-to-market losses |

### Permitted Before Earnings (with Conditions)

| Action | Condition |
|--------|-----------|
| Buying protective puts | Always permitted; this is hedging |
| Buying straddles/strangles | Only if explicit earnings volatility thesis is documented with defined risk |
| Closing existing options | Always permitted; reducing risk is encouraged |

### Existing Options Through Earnings

If you hold options positions that will be open through an earnings release:

1. **Review all positions T-5**: Assess whether to close, roll, or hold through
2. **Document the decision**: For each position, record: current P&L, expected earnings move (implied by options market), your thesis on direction/magnitude, maximum acceptable loss
3. **Size check**: Total options exposure through earnings for a single name must not exceed 50% of the OPRMS DNA position cap in maximum loss terms

---

## Post-Earnings Protocol

### 24-Hour Observation Period

After earnings are released, observe for 24 hours (next trading day close) before taking action on new positions. This allows:
1. Full digest of earnings call commentary
2. Post-market and pre-market reaction to stabilize
3. Analyst revisions to publish
4. Avoidance of knee-jerk reactions

### Exceptions to 24-Hour Rule

| Exception | Condition |
|-----------|-----------|
| Kill condition triggered | If earnings data triggers a pre-defined kill condition, exit within 2 trading days per kill conditions protocol |
| Pre-planned entry | If you had a documented pre-earnings plan: "If revenue exceeds $X AND guidance raised, enter at market open" -- execute the plan |
| Protective actions | Hedging, stop-loss execution, and risk reduction are always permitted immediately |

### Post-Earnings Review Checklist

For every held position after its earnings release:

```markdown
## Post-Earnings Review: {TICKER} - {Quarter}

### Results vs. Expectations
- Revenue: {actual} vs {consensus} vs {your estimate}
- EPS: {actual} vs {consensus} vs {your estimate}
- Key metric: {actual} vs {your thesis assumption}

### Guidance
- Revenue guidance: {above/in-line/below} consensus
- Margin guidance: {expanding/stable/contracting}
- Management tone: {confident/cautious/defensive}

### Kill Condition Check
- [ ] All financial kill conditions still clear
- [ ] Management kill conditions still clear
- [ ] Thesis invalidation conditions still clear

### Action
- [ ] Hold -- thesis intact, no changes needed
- [ ] Trim -- results OK but thesis weakened, reduce by {X}%
- [ ] Add -- results strengthen thesis, increase by {X}% (subject to IPS limits)
- [ ] Exit -- kill condition triggered or thesis invalidated

### Notes
{free-form analysis}
```

---

## Earnings Season Portfolio Management

During peak earnings season (typically weeks 3-5 of Jan, Apr, Jul, Oct), when multiple portfolio holdings report:

1. **Stagger review**: Do not let earnings pile up without review. Process each within 48 hours.
2. **Reduce gross exposure**: Consider trimming marginal positions (B/C tier) before earnings season to create cash buffer for opportunities.
3. **Track IV**: Monitor implied volatility across holdings. High IV = market expects big moves = higher risk.

---

## Integration Points

| System | Integration |
|--------|-------------|
| **Data Desk** | Earnings calendar feed (FMP, Phase 2a-2) populates upcoming dates |
| **Trading Desk** | Trade journal pre-trade checklist includes earnings date verification |
| **Portfolio Desk** | Weekly snapshot flags positions within T-5 of earnings |
| **Knowledge Base** | Post-earnings reviews feed back into OPRMS rating adjustments |
