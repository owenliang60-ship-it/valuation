# Investment Policy Statement (IPS)

> 未来资本 -- Institutional-Grade Risk Governance for a Personal Portfolio
>
> Version: 1.0
> Effective Date: 2026-02-07
> Last Review: 2026-02-07
> Next Review: 2026-05-07 (Quarterly)

---

## 1. Mission & Scope

This IPS governs a multi-million dollar personal US equity and options portfolio managed through the 未来资本 AI Trading Desk. The portfolio targets long-term wealth compounding through concentrated, high-conviction positions in large-cap US equities, supplemented by options strategies for income and hedging.

**In scope**: US equities (NYSE + NASDAQ, market cap > $100B), equity options, cash equivalents.

**Out of scope**: Fixed income, commodities, crypto, international equities, private investments.

---

## 2. Return Objectives

### Hard IRR Hurdles

Every position must clear an expected IRR threshold before entry. No exceptions.

| Position Type | Minimum Expected IRR | Rationale |
|--------------|---------------------|-----------|
| **Long** | >= 15% | Compensates for concentration risk and opportunity cost vs. index |
| **Short** | >= 20-25% | Higher bar due to unlimited theoretical risk and negative carry |

### PASS Rule

If expected returns do not clear the above thresholds despite qualitative merit, the decision is **PASS**. Do not enter the position. Document the thesis for future review if conditions change.

### Benchmark

Primary benchmark: SPY (S&P 500 ETF). Secondary: QQQ (Nasdaq 100 ETF). The portfolio should generate meaningful alpha over a full market cycle (3-5 years) to justify its concentration and active management cost.

---

## 3. Position Limits (OPRMS DNA System)

Maximum position size is determined by the asset's DNA rating in the OPRMS system. These are hard caps, not targets.

| DNA Rating | Name | Max Position Size | Characteristics |
|-----------|------|------------------|----------------|
| **S** | Holy Grail | 20-25% | Civilization-altering assets. Durable competitive moats spanning decades. Maximum 2 S-tier positions at >20% simultaneously. |
| **A** | General | 15% | Sector leaders, proven compounders. Strong ROIC, clear competitive advantage. |
| **B** | Dark Horse | 7% | High narrative momentum, asymmetric payoff potential. Elevated uncertainty. |
| **C** | Follower | 2% | Catch-up logic, beta plays. Rarely used -- requires explicit justification. |

### DNA Rating Requirements

- S-tier requires documented investment memo scoring >= 7.0/10 on the memo quality rubric
- A-tier requires documented investment memo with complete kill conditions
- B-tier requires at minimum a thesis summary with kill conditions
- C-tier requires thesis summary only

---

## 4. Concentration Limits

These limits apply on top of individual OPRMS position caps.

### Single-Stock Concentration

| Metric | Limit | Action on Breach |
|--------|-------|-----------------|
| Largest single position | 25% of portfolio | Hard cap. Trim excess immediately. |
| Top 3 positions combined | 50% of portfolio | Soft cap. Review within 1 week; trim if not justified. |
| Top 5 positions combined | 70% of portfolio | Monitoring threshold. Ensure adequate diversification in remainder. |

### Sector Concentration

| Metric | Limit | Action on Breach |
|--------|-------|-----------------|
| Single sector | 40% of portfolio | Hard cap. No new positions in sector until below limit. |
| Top 2 sectors combined | 65% of portfolio | Soft cap. Review and document rationale if exceeded. |

### Allowed Sectors

Per the stock pool configuration:
- Technology
- Financial Services
- Healthcare
- Consumer Cyclical
- Communication Services (Entertainment sub-industry only)

### Excluded Sectors

No positions permitted:
- Consumer Defensive
- Energy
- Utilities
- Basic Materials
- Real Estate

---

## 5. Drawdown Protocols

### Position-Level Drawdown

| Drawdown from Entry | Action Required |
|--------------------|-----------------|
| **-15%** | **Mandatory Review**: Re-examine thesis, kill conditions, and evidence. Document findings. Decision: Hold / Reduce / Exit. |
| **-25%** | **Mandatory Reduction or Exit**: Must reduce position by at least 50% OR exit entirely, UNLESS a written re-underwriting memo is completed within 2 trading days that (a) confirms original thesis remains intact with new evidence, (b) updates kill conditions, and (c) is scored >= 6.0/10 on memo rubric. |
| **-40%** | **Mandatory Exit**: Exit entire position. No exceptions. Re-entry requires full new memo process with minimum 5-day cooling period. |

### Portfolio-Level Drawdown

| Drawdown from Peak | Action Required |
|-------------------|-----------------|
| **-10%** | **Position Triage**: Review every position. Rank by conviction. Identify weakest holdings for potential trim. No new positions until review complete. |
| **-15%** | **Defensive Posture**: Reduce total equity exposure to <= 70%. Close all B-tier and C-tier positions. Only hold S-tier and A-tier names. |
| **-20%** | **Crisis Mode**: Reduce to core holdings only (S-tier). Total equity exposure <= 50%. Remaining capital in cash or short-term treasuries. No new positions until drawdown recovers to -10%. |

### Adding to Positions

- **Add to winners only**: A position must be profitable before adding. Exception: S-tier Timing downgrade (averaging into a crash) requires explicit memo.
- **Thesis strengthening**: Adding requires new evidence that strengthens the thesis since original entry. Document the new evidence.
- **Respect position caps**: Adding cannot cause the position to exceed its OPRMS DNA cap.

---

## 6. Options-Specific Rules

### Covered Strategies (Lower Risk)

| Strategy | Permitted | Conditions |
|----------|-----------|-----------|
| Covered calls | Yes | Only on existing long equity positions. Strike >= 10% OTM or above resistance. |
| Cash-secured puts | Yes | Only on names with completed investment memo. Strike at or below target entry price. |
| Protective puts | Yes | Portfolio insurance. No restrictions on usage. |

### Spread Strategies (Moderate Risk)

| Strategy | Permitted | Conditions |
|----------|-----------|-----------|
| Vertical spreads | Yes | Maximum risk must be quantified and within position DNA cap equivalent. |
| Calendar spreads | Yes | Defined risk only. |
| Iron condors | Yes | On individual names only with defined thesis on range. |

### Prohibited Strategies

| Strategy | Reason |
|----------|--------|
| Naked short calls | Unlimited risk. Never permitted. |
| Naked short puts beyond cash-secured | Margin risk exceeds position limits. |
| Short strangles/straddles | Undefined risk on both sides. |
| Leveraged positions (margin > 1x) | No margin usage for directional bets. |

### Options Sizing

Options positions are sized by their maximum potential loss (for defined-risk strategies) or delta-equivalent notional exposure (for directional plays). The resulting exposure must fit within the OPRMS DNA position cap for the underlying.

---

## 7. Evidence Requirements

Per the BidClub ticker-to-thesis framework, position sizing scales with evidence quality:

| Position Size | Evidence Required |
|--------------|-------------------|
| **Starter (1/3 of target)** | Thesis summary + kill conditions + 3 primary sources minimum |
| **Half position (1/2 of target)** | Investment memo draft + 5+ total sources |
| **Full position** | Complete investment memo scoring >= 7.0/10, 3+ primary sources, 8-10+ total sources |

### Primary Source Types
- Direct voice: CEO interviews, earnings calls, conference presentations
- Stakeholder signals: Glassdoor reviews, customer feedback, supplier commentary
- Behavioral data: Patent filings, job postings, insider trading activity

---

## 8. Review Cadence

| Frequency | Activity | Responsible |
|-----------|----------|-------------|
| **Weekly** | Position weights snapshot, concentration check, kill condition scan | Portfolio Desk + Risk Desk |
| **Monthly** | Deep portfolio review: thesis status for each position, drawdown check, sector exposure analysis | All Desks |
| **Quarterly** | IPS compliance audit, OPRMS rating review, benchmark comparison, rebalance assessment | All Desks |
| **Annual** | Full IPS review and amendment consideration | Owner decision |

---

## 9. Amendment Process

1. **Proposal**: Written rationale for the proposed change, including what triggered it and expected impact.
2. **Cooling period**: 48 hours minimum between proposal and implementation. No IPS changes during active drawdown protocols.
3. **Documentation**: All amendments recorded with date, rationale, and before/after comparison.
4. **Version control**: IPS is version-controlled in git. Every change is a commit with clear message.

---

## 10. Enforcement

This IPS is enforced through:
- **Pre-trade checklist**: Every trade must pass IPS compliance check before execution (see Trading Desk trade journal)
- **Automated alerts**: Position limit and concentration breaches flagged by Portfolio Desk (future automation)
- **Post-trade review**: Monthly review verifies all active positions comply with current IPS
- **Escalation**: Any IPS override requires written exception memo filed in `risk/exceptions/` with expiration date

---

*This document is the supreme governance authority for all investment activity at 未来资本. When in conflict with any other desk's guidelines, the IPS takes precedence.*
