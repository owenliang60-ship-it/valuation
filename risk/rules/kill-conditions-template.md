# Kill Conditions Template

> Every position must have pre-defined, observable, measurable invalidation triggers.
> Kill conditions are set BEFORE entry and documented in the trade journal.
> They are the contract with yourself: if these conditions are met, the thesis is dead.

---

## Principles

1. **Observable**: Based on publicly available data (financial reports, price action, corporate announcements). Not on feelings or calendar dates.
2. **Measurable**: Has a specific numeric threshold or binary event. "The company is doing poorly" is not a kill condition. "Revenue growth below 10% YoY for 2 consecutive quarters" is.
3. **Pre-committed**: Set before entry. Modifications require written justification filed in `risk/exceptions/`.
4. **Comprehensive**: Cover multiple failure modes, not just price.

---

## Kill Condition Categories

### Category 1: Financial Metric Breach

Triggers based on deterioration in key financial metrics.

| Template | Example |
|----------|---------|
| `{metric} {direction} {threshold} for {duration}` | Gross margin below 60% for 2 consecutive quarters |
| `{metric} misses consensus by {amount} for {count} quarters` | EPS misses consensus by >10% for 2 consecutive quarters |
| `{growth_metric} decelerates below {rate} for {duration}` | Revenue growth below 10% YoY for 3 consecutive quarters |
| `{leverage_metric} exceeds {threshold}` | Net debt / EBITDA exceeds 3.0x |
| `Free cash flow turns negative for {duration}` | Free cash flow negative for 2 consecutive quarters |

**Guidance**: Choose 2-3 financial kill conditions per position. Focus on the metrics most critical to the investment thesis (e.g., gross margin for a SaaS compounder, same-store sales for retail).

### Category 2: Management & Governance

Triggers based on leadership or governance changes that undermine the thesis.

| Template | Example |
|----------|---------|
| `CEO departs without named successor within {days} days` | CEO departs without named successor within 30 days |
| `{key_executive} departs` | CFO who led the turnaround departs |
| `Board adopts {governance_change}` | Board adopts poison pill or dual-class reclassification |
| `Insider selling exceeds {threshold} in {period}` | CEO sells >25% of holdings in any 90-day period |
| `Accounting restatement or SEC investigation announced` | (Binary event -- immediate review) |

**Guidance**: Include at least 1 management kill condition. The CEO/founder is often the thesis for S-tier and A-tier names.

### Category 3: Competitive Moat Erosion

Triggers based on loss of competitive advantage.

| Template | Example |
|----------|---------|
| `Market share loss of {amount} in {market}` | Loses >5% market share in cloud infrastructure |
| `{competitor} achieves {capability} parity` | Competitor achieves feature parity in core product |
| `{pricing_metric} declines by {amount}` | Average selling price declines >15% YoY |
| `Key customer {customer} churns or reduces spend by {amount}` | Top 3 customer reduces spend by >30% |
| `Regulatory action: {specific_threat}` | Antitrust ruling forces structural separation |

**Guidance**: Most relevant for S-tier (moat is the thesis) and B-tier (narrative may not survive competition).

### Category 4: Thesis Invalidation Events

Binary events that directly negate the core investment thesis.

| Template | Example |
|----------|---------|
| `{catalyst} fails to materialize by {date}` | FDA approval not received by Q2 2027 |
| `{assumption} proven false by {evidence}` | TAM estimate revised down >40% by industry analysts |
| `Macro regime shifts to {scenario}` | Fed raises rates above 6%, destroying growth multiple thesis |
| `Acquisition of {target} at {price} destroying value` | Overpays for acquisition at >15x revenue |

**Guidance**: These are thesis-specific. The more specific your original thesis, the more specific your kill conditions.

---

## Template: Per-Position Kill Conditions Card

```markdown
## Kill Conditions: {TICKER}

**Position opened**: {date}
**DNA Rating**: {S/A/B/C}
**Core thesis**: {one sentence}

### Financial Kills
1. {condition_1}
2. {condition_2}

### Management Kills
1. {condition_1}

### Moat Kills
1. {condition_1}

### Thesis Invalidation
1. {condition_1}

### Price-Based Emergency Stop
- Hard stop: -{X}% from entry (per IPS drawdown protocol)
- Trailing stop: -{Y}% from peak (optional, for B/C tier)

### Review Triggers (Not Automatic Kills)
- {event that triggers review but not automatic exit}

---
Last reviewed: {date}
Next review: {date}
```

---

## Process

### Pre-Trade
1. Fill out the kill conditions card as part of the trade journal entry
2. Minimum kill conditions: 2 financial + 1 management + 1 thesis invalidation = 4 minimum
3. Get sign-off: review conditions for specificity and measurability before entry

### During Hold
1. Weekly scan: check if any kill condition has been triggered or is approaching
2. Earnings review: after each quarterly report, evaluate all financial kill conditions
3. Event check: material news triggers immediate kill condition review

### On Trigger
1. **Kill condition met**: Exit position within 2 trading days. No negotiation with yourself.
2. **Kill condition approaching**: Reduce position by 1/3 as early warning action. Document.
3. **Kill condition modification**: Only permitted with written justification. Must be filed BEFORE the condition is triggered, not after. Post-hoc rationalization is not allowed.

---

## Anti-Patterns (What NOT to Do)

| Bad Kill Condition | Why It Fails | Better Version |
|-------------------|-------------|----------------|
| "If the stock drops 20%" | Price alone is not a thesis | "If gross margin drops below 55% AND stock drops 20%" |
| "If things get worse" | Not measurable | "If revenue growth decelerates below 15% for 2 quarters" |
| "Re-evaluate in 6 months" | Calendar-based, not event-based | "If product launch fails to gain 1M users by Q3" |
| "If macro deteriorates" | Too vague | "If 10Y yield exceeds 5.5% for 30+ days" |
| "If I feel uncomfortable" | Emotional, not systematic | Define the specific metrics that would cause discomfort |
