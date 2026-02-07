# Trade Journal

Structured database of every trade taken by the desk. Every entry captures the full lifecycle: pre-trade thesis, execution, and post-trade outcome.

## Purpose

1. **Enforce discipline** -- no trade without a written thesis and kill conditions
2. **Track execution quality** -- slippage, timing, sizing accuracy
3. **Enable learning** -- connect outcomes to decisions for pattern recognition

## Record Structure

Each trade record has three phases:

### Pre-Trade (filled before any order is placed)
- Falsifiable thesis statement
- Variant view (why the market is wrong)
- Investment bucket classification
- OPRMS DNA and Timing ratings
- Kill conditions (observable, measurable triggers)
- Target IRR and action price
- Entry rules and sizing plan
- Evidence sources (3+ primary, 8-10+ total)

### Execution (filled when orders are placed)
- Entry date, price, shares/contracts
- Actual position size vs. planned
- Slippage in basis points
- Sizing rationale and order type

### Post-Trade (filled when position is closed)
- Exit date, price, realized P&L
- Hold period
- Thesis accuracy assessment
- Which kill condition triggered (if any)
- Link to post-trade review

## Files

| File | Description |
|------|-------------|
| `schema.json` | JSON Schema defining the complete trade record structure |
| `template.md` | Markdown template for manual trade entry |
| `examples/AAPL-long-example.md` | Filled example demonstrating all fields |

## Usage

1. Before entering a trade, copy `template.md` and fill all pre-trade fields
2. If any required field cannot be filled, the trade is not ready
3. On execution, fill the execution section
4. On close, fill the post-trade section and create a review in `../review/`
