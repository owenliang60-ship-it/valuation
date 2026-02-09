# Architecture — Finance Workspace

**System Design for 未来资本 AI Trading Desk**

---

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Claude (Analyst)                         │
│  Reads structured prompts → Applies 6 lenses → Writes memos    │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ Calls terminal commands
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                    Terminal Layer (7 files, 1462 lines)         │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐ │
│  │ commands.py  │ pipeline.py  │ company_db.py│ monitor.py   │ │
│  │ (Public API) │ (Analysis)   │ (Storage)    │ (Risk Sweep) │ │
│  └──────────────┴──────────────┴──────────────┴──────────────┘ │
│  ┌──────────────┬──────────────┬──────────────┐                │
│  │ themes.py    │ regime.py    │ __init__.py  │                │
│  │ (Clustering) │ (Macro)      │ (Exports)    │                │
│  └──────────────┴──────────────┴──────────────┘                │
└───────────────────────────┬─────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│  Knowledge    │   │  Data Desk    │   │  Portfolio    │
│  Desk         │   │  (src/)       │   │  Desk         │
│  (knowledge/) │   │  (data/)      │   │  (portfolio/) │
│               │   │               │   │               │
│ - OPRMS       │   │ - FMP API     │   │ - Holdings    │
│ - 6 Lenses    │   │ - SQLite      │   │ - Exposure    │
│ - Debate      │   │ - Indicators  │   │ - Watchlists  │
│ - Memo        │   │ - Price CSV   │   │ - Attribution │
└───────────────┘   └───────────────┘   └───────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │  Company DB   │
                    │  (data/       │
                    │   companies/) │
                    │               │
                    │ - Memos       │
                    │ - OPRMS       │
                    │ - Kill Conds  │
                    │ - Analyses    │
                    └───────────────┘
```

**Core Principle**: Claude IS the analyst. The system generates structured prompts with data context, Claude responds with insights, and results are stored for reuse.

---

## Layer 1: Terminal (Orchestration)

**Location**: `terminal/` (7 files, 1462 lines)

### Purpose
Public API for Claude to interact with the Finance workspace. Orchestrates data collection, prompt generation, analysis workflows, and storage.

### Files

#### 1. `commands.py` (252 lines)
Top-level entry points Claude calls directly in conversation.

**Functions**:
- `analyze_ticker(symbol, depth, price_days)` → Full analysis pipeline
  - `depth="quick"`: Data snapshot only (5 sec, $0)
  - `depth="standard"`: + 6 lens prompts (~1 min, ~$2)
  - `depth="full"`: + debate + memo + scoring (~5 min, ~$13-15)
- `portfolio_status()` → Holdings + exposure alerts + company DB coverage
- `position_advisor(symbol, total_capital)` → OPRMS-based position sizing
- `company_lookup(symbol)` → Everything in company DB for a ticker
- `run_monitor()` → Full portfolio health sweep
- `theme_status(slug)` → Investment theme membership

**Data Flow**:
```
Claude → analyze_ticker("NVDA", depth="full")
       → collect_data() [pipeline.py]
       → prepare_lens_prompts() [pipeline.py]
       → Claude runs 6 lens analyses
       → prepare_debate_prompts() [pipeline.py]
       → Claude runs 5-round debate
       → Claude writes memo using memo_skeleton
       → score_memo() [knowledge/memo/scorer.py]
       → save to company_db [company_db.py]
```

#### 2. `pipeline.py` (420 lines)
Analysis workflow orchestration. Generates structured prompts with injected data context.

**Key Components**:
- `DataPackage` (dataclass): Aggregates all data for a ticker
  - Company info, fundamentals, financials, price, indicators
  - Company DB record (existing OPRMS, memos, kill conditions)
  - `format_context()`: Renders data as markdown for Claude prompts
- `collect_data(symbol, price_days)`: Phase 1 data collection
  - Calls Data Desk (`src/data/data_query.py`)
  - Runs indicators (`src/indicators/engine.py`)
  - Loads company DB record (`terminal/company_db.py`)
- `prepare_lens_prompts(symbol, data_pkg)`: Phase 2 prompt generation
  - Injects DataPackage into 6 investment lens templates
  - Returns list of prompts for Claude to execute sequentially
- `prepare_debate_prompts(symbol, tensions)`: Phase 3 debate orchestration
  - Generates 5 rounds of adversarial debate prompts
  - Bull vs. Bear on identified tensions
- `prepare_memo_skeleton(symbol)`: Memo template with investment buckets
- `score_memo(memo_text)`: Quality gates (completeness + writing standards)
- `calculate_position(symbol, dna, timing, ...)`: OPRMS position sizing

**Extension Points**:
- Add new lenses: `knowledge/philosophies/*.py`
- Add new indicators: `src/indicators/*.py`
- Modify debate protocol: `knowledge/debate/*.py`

#### 3. `company_db.py` (324 lines)
Per-ticker knowledge storage and retrieval.

**Structure**:
```
data/companies/{SYMBOL}/
├── oprms.json              # Current OPRMS rating
├── oprms_history.jsonl     # OPRMS changelog (append-only)
├── kill_conditions.json    # Observable invalidation triggers
├── memos.jsonl             # Investment memos (timestamped)
├── analyses.jsonl          # Full analysis results (timestamped)
└── meta.json               # Theme memberships, tags
```

**Functions**:
- `get_company_record(symbol)` → `CompanyRecord` (dataclass with all files)
- `save_oprms(symbol, oprms)` → Write current + append to history
- `save_kill_conditions(symbol, conditions)` → Overwrite kill conditions
- `save_memo(symbol, memo)` → Append to memos.jsonl
- `save_analysis(symbol, analysis)` → Append to analyses.jsonl
- `update_meta(symbol, key, value)` → Patch meta.json
- `list_all_companies()` → List of all tracked tickers

**Design**: Flat file storage (JSON/JSONL) for human readability and git-trackable history.

#### 4. `monitor.py` (181 lines)
Portfolio health monitoring system.

**Functions**:
- `run_full_monitor()` → Sweep all holdings for:
  - **Exposure alerts**: Concentration, sector limits, correlation
  - **Kill condition checks**: Observable triggers per position
  - **Position drift**: Actual vs. target size divergence
  - **Staleness**: Last review date > 30 days
- Outputs structured report with CRITICAL/WARNING/INFO severity levels

**Integrations**:
- `portfolio/holdings/manager.py` → Holdings data
- `portfolio/exposure/alerts.py` → Alert rules
- `terminal/company_db.py` → Kill conditions lookup

#### 5. `themes.py` (348 lines)
Investment theme clustering and relevance detection.

**Theme Model**:
```json
{
  "slug": "ai-infrastructure",
  "name": "AI Infrastructure",
  "thesis": "Cloud compute + semiconductors powering AI revolution",
  "members": ["NVDA", "AMD", "MSFT"],
  "updated_at": "2026-02-07T12:00:00"
}
```

**Functions**:
- `create_theme(slug, name, thesis)` → New theme
- `add_member(slug, symbol)` → Add ticker to theme
- `remove_member(slug, symbol)` → Remove ticker
- `get_theme(slug)` → Retrieve theme with members
- `find_themes_for_ticker(symbol)` → Reverse lookup
- `detect_theme_relevance(symbol, theme_slug)` → AI-powered relevance scoring

**Storage**: `data/themes/{slug}.json`

#### 6. `regime.py` (78 lines)
Macro regime detection (stub implementation).

**Current**: Returns `NEUTRAL` regime placeholder.

**Future**: Integrate FRED API (VIX, yield curve, unemployment) for:
- Bull / Bear / Transition regime classification
- Risk-on / Risk-off positioning signals
- Position size adjustments by regime

#### 7. `__init__.py` (17 lines)
Public exports for terminal layer.

---

## Layer 2: Knowledge Desk

**Location**: `knowledge/` (4 subsystems)

### Purpose
Investment frameworks, rating systems, and analysis methodologies. Contains domain knowledge, not market data.

### Subsystems

#### 1. `knowledge/philosophies/` — 6-Lens Analysis Framework

**Files**:
- `base.py`: `InvestmentLens` protocol + lens registry
- `business_quality.py`: Competitive moats, unit economics
- `management_excellence.py`: Capital allocation, insider ownership
- `financial_strength.py`: Balance sheet, cash generation
- `growth_trajectory.py`: TAM expansion, margin trajectory
- `valuation.py`: Price vs. intrinsic value, peer multiples
- `technical_setup.py`: Momentum, volume patterns

**Usage**:
```python
from knowledge.philosophies.base import get_all_lenses, format_prompt

lenses = get_all_lenses()  # Returns 6 InvestmentLens objects
for lens in lenses:
    prompt = format_prompt(lens, symbol="NVDA", context=data_context)
    # Claude runs the prompt and responds
```

**Extension**: Add new lens by creating `knowledge/philosophies/new_lens.py` implementing `InvestmentLens` protocol.

#### 2. `knowledge/debate/` — Adversarial Analysis Protocol

**Files**:
- `protocol.py`: 5-round debate structure (Bull/Bear alternating)
- `director_guide.py`: Meta-prompts for identifying tensions

**Debate Flow**:
1. Claude identifies 3 key tensions from 6-lens analysis
2. `generate_round_prompt(round_num, role, tension)` creates adversarial prompts
3. Claude alternates Bull/Bear perspectives for 5 rounds
4. Synthesizes consensus view in memo

**Rationale**: Forces explicit consideration of counter-arguments, prevents confirmation bias.

#### 3. `knowledge/memo/` — Investment Memo System

**Files**:
- `template.py`: Memo skeleton with 9 investment buckets
- `scorer.py`: Quality gates (completeness + writing standards)

**Investment Buckets**:
1. Business Model DNA
2. Competitive Moats
3. Financial Performance
4. Growth Drivers
5. Risk Factors
6. Valuation
7. Technical Setup
8. Thesis Summary
9. Kill Conditions

**Scoring**:
- Completeness check: All 9 buckets filled (max 5 points)
- Writing standards: Clarity, specificity, evidence (max 5 points)
- Target: > 7.0/10 before saving to company DB

#### 4. `knowledge/oprms/` — Rating System

**Files**:
- `models.py`: `DNARating`, `TimingRating`, `OPRMSRating` (Enums + dataclasses)
- `ratings.py`: `calculate_position_size()` implementation
- `changelog.py`: OPRMS history tracking
- `integration.py`: Hooks for portfolio desk

**OPRMS Model**:
```python
@dataclass
class OPRMSRating:
    symbol: str
    dna: DNARating           # S/A/B/C (20-25% / 15% / 7% / 2% max)
    timing: TimingRating     # S/A/B/C (1.0-1.5 / 0.8-1.0 / 0.4-0.6 / 0.1-0.3 coeff)
    timing_coeff: float      # Actual coefficient in timing range
    investment_bucket: str   # "Core", "Growth", "Speculation"
    evidence: List[str]      # Primary sources (min 3 for full position)
    rationale: str           # Justification
    updated_at: str
```

**Position Sizing**:
```python
base_position = total_capital * dna.max_position_pct * timing_coeff
evidence_gate = min(len(evidence) / 3.0, 1.0)  # Scale if <3 sources
final_position = base_position * evidence_gate
```

**Single Source of Truth**: `knowledge/oprms/models.py` is imported by `portfolio/` and `risk/` modules. IPS in `risk/ips.md` documents rules but does NOT contain code.

---

## Layer 3: Data Desk

**Location**: `src/`, `data/`, `scripts/`, `config/`

### Purpose
Market data collection, validation, storage, and technical indicators.

### Components

#### 1. `src/data/` — Data Pipeline
- `fmp_client.py`: FMP API wrapper with rate limiting (2s interval)
- `data_query.py`: Unified query interface (`get_stock_data(symbol)`)
- `data_validator.py`: Schema validation + data quality checks
- `database.py`: SQLite schema for `data/valuation.db`

**Current FMP Endpoints**:
1. Stock screener (market cap, sector filter)
2. Company profile
3. Key metrics (P/E, ROE, margins)
4. Income statement (quarterly/annual)
5. Balance sheet
6. Cash flow
7. Financial ratios
8. Historical price (5 years daily)
9. Quote (latest price)

**Unused FMP Endpoints** (Starter plan access):
- Earnings estimates
- Earnings calendar
- Insider trades
- News feed
- Macro indicators (limited)

#### 2. `src/indicators/` — Technical Indicators
- `engine.py`: Indicator orchestration (`run_indicators(symbol)`)
- `pmarp.py`: Price momentum percentile (>98% = strong trend)
- `rvol.py`: Relative volume (>4σ = anomaly)
- `base.py`: `Indicator` protocol for extensibility

**Add New Indicator**:
```python
# src/indicators/new_indicator.py
from src.indicators.base import Indicator

class NewIndicator(Indicator):
    def calculate(self, symbol: str) -> dict:
        # Implementation
        return {"signal": "bullish", "value": 1.23}
```

Register in `src/indicators/engine.py`:
```python
from src.indicators.new_indicator import NewIndicator

INDICATORS = [PMARP(), RVOL(), NewIndicator()]
```

#### 3. `data/` — Data Storage
```
data/
├── valuation.db                 # SQLite (company info + financials)
├── dollar_volume.db             # Dollar volume rankings
├── price/{SYMBOL}.csv           # 5-year daily OHLCV (77 stocks)
├── fundamental/{SYMBOL}/        # JSON files (statements, ratios, profile)
│   ├── income_statement.json
│   ├── balance_sheet.json
│   ├── cash_flow.json
│   ├── ratios.json
│   └── profile.json
├── companies/{SYMBOL}/          # Company DB (per-ticker knowledge)
└── themes/{slug}.json           # Investment themes
```

#### 4. `scripts/` — Data Maintenance
- `update_data.py --price`: Update price CSVs (daily cron)
- `update_data.py --fundamental`: Update fundamentals (weekly cron)
- `update_data.py --all`: Full refresh
- `scan_indicators.py`: Run indicators on all stocks
- `refresh_stock_pool.py`: Rebuild stock pool from FMP screener

#### 5. `config/settings.py` — Configuration
```python
MARKET_CAP_MIN = 100_000_000_000  # $100B
ALLOWED_SECTORS = [
    "Technology",
    "Financial Services",
    "Healthcare",
    "Consumer Cyclical",
    "Communication Services",  # Entertainment only
]
```

---

## Layer 4: Portfolio Desk

**Location**: `portfolio/`

### Purpose
Holdings management, exposure monitoring, performance attribution.

### Subsystems

#### 1. `portfolio/holdings/` — Position Management
- `manager.py`: CRUD for positions
- `positions.json`: Current holdings (symbol, quantity, cost basis, entry date)
- `watchlist.json`: Observation list (not held but monitoring)

**Position Model**:
```json
{
  "symbol": "NVDA",
  "quantity": 100,
  "cost_basis": 450.00,
  "entry_date": "2024-01-15",
  "notes": "AI infrastructure thesis, S-tier DNA"
}
```

#### 2. `portfolio/exposure/` — Risk Monitoring
- `alerts.py`: Rule engine for exposure checks
- `rules.py`: Alert rule definitions

**Alert Types**:
- Single position > DNA max (e.g., S-tier > 25%)
- Sector concentration > 40%
- Total portfolio utilization > 95%
- Correlation cluster risk (>3 correlated positions > 60% of portfolio)

**Alert Severity**:
- CRITICAL: Immediate action required (hard limit breach)
- WARNING: Approaching limit (80% of threshold)
- INFO: Noteworthy but acceptable

#### 3. `portfolio/attribution/` (Stub)
Future: Performance attribution by sector, theme, DNA tier.

---

## Layer 5: Risk Desk

**Location**: `risk/`

### Purpose
Investment policy governance, position limits, kill conditions.

### Files

#### 1. `risk/ips.md` — Investment Policy Statement
**Sections**:
1. Mission & Scope
2. Return Objectives (IRR hurdles: 15% long, 20-25% short)
3. Position Limits (OPRMS DNA caps)
4. Risk Limits (sector, correlation, leverage)
5. Kill Condition Requirements (every position must have observable triggers)
6. Review Schedule (quarterly)

**Not Code**: IPS is documentation only. Enforcement logic lives in:
- `knowledge/oprms/models.py` (position limits)
- `portfolio/exposure/rules.py` (exposure alerts)
- `terminal/company_db.py` (kill condition storage)

#### 2. `risk/kill_conditions/` (Planned)
Future: Automated kill condition monitoring (price alerts, earnings misses, management changes).

---

## Layer 6: Trading Desk

**Location**: `trading/`

### Purpose
Trade execution logs, strategy library, post-mortems.

### Planned Structure
```
trading/
├── trades/
│   └── 2024/
│       ├── 01_january.jsonl    # Trade log (entry/exit, P&L)
├── strategies/
│   ├── covered_calls.md        # Options income strategies
│   ├── protective_puts.md      # Hedging strategies
└── postmortems/
    ├── NVDA_2024Q1.md          # Trade retrospectives
```

**Current Status**: Skeleton directories, awaiting real position input.

---

## Data Flow: Full Analysis

**User Request**: `analyze_ticker("NVDA", depth="full")`

1. **Terminal Layer** (`terminal/commands.py:analyze_ticker`)
   - Calls `collect_data("NVDA", price_days=60)`

2. **Data Collection** (`terminal/pipeline.py:collect_data`)
   - Query Data Desk: `src/data/data_query.get_stock_data("NVDA")`
     - Reads `data/valuation.db` (fundamentals, financials)
     - Reads `data/price/NVDA.csv` (price history)
     - Reads `data/fundamental/NVDA/*.json` (statements, ratios)
   - Run indicators: `src/indicators/engine.run_indicators("NVDA")`
     - Calculates PMARP, RVOL from price data
   - Load company record: `terminal/company_db.get_company_record("NVDA")`
     - Reads `data/companies/NVDA/*` (existing OPRMS, memos, kill conditions)
   - Returns `DataPackage` with all data

3. **Lens Prompts** (`terminal/pipeline.py:prepare_lens_prompts`)
   - Loads 6 lenses: `knowledge/philosophies/base.get_all_lenses()`
   - Injects `DataPackage.format_context()` into each lens template
   - Returns 6 structured prompts for Claude

4. **Claude Analysis** (in conversation)
   - Runs each lens prompt sequentially
   - Identifies 3 key tensions across perspectives
   - Requests debate prompts: `prepare_debate_prompts("NVDA", tensions)`

5. **Debate Prompts** (`terminal/pipeline.py:prepare_debate_prompts`)
   - Generates 5 rounds of Bull/Bear adversarial prompts
   - Injects tensions + DataPackage context
   - Returns debate prompt sequence

6. **Claude Debate** (in conversation)
   - Alternates Bull/Bear perspectives for 5 rounds
   - Synthesizes consensus view

7. **Memo Writing** (`terminal/pipeline.py:prepare_memo_skeleton`)
   - Returns memo template with 9 investment buckets
   - Claude fills in each section with analysis findings

8. **Memo Scoring** (`knowledge/memo/scorer.py:score_memo`)
   - Checks completeness (all 9 buckets filled)
   - Checks writing standards (clarity, specificity, evidence)
   - Returns score (target: > 7.0/10)

9. **OPRMS Rating** (Claude assigns, system calculates position)
   - Claude assigns DNA rating (S/A/B/C) + Timing rating (S/A/B/C)
   - `terminal/pipeline.py:calculate_position()` computes position size
   - Uses `knowledge/oprms/ratings.py:calculate_position_size()`

10. **Storage** (`terminal/company_db.py`)
    - `save_memo("NVDA", memo_text)` → Append to `data/companies/NVDA/memos.jsonl`
    - `save_oprms("NVDA", oprms_dict)` → Write `data/companies/NVDA/oprms.json` + append to history
    - `save_analysis("NVDA", full_result)` → Append to `data/companies/NVDA/analyses.jsonl`

**Result**: Complete investment memo with OPRMS rating stored in company DB, ready for position_advisor() to calculate sizing.

---

## Extension Points

### Add New Investment Lens
1. Create `knowledge/philosophies/new_lens.py`
2. Implement `InvestmentLens` protocol (name, prompt_template)
3. Register in `knowledge/philosophies/__init__.py`
4. Lens automatically included in `prepare_lens_prompts()`

### Add New Technical Indicator
1. Create `src/indicators/new_indicator.py`
2. Implement `Indicator` protocol (calculate method)
3. Register in `src/indicators/engine.py:INDICATORS` list
4. Indicator automatically runs in `collect_data()`

### Add New FMP Data Endpoint
1. Add method to `src/data/fmp_client.py` (e.g., `get_earnings_estimates()`)
2. Integrate into `src/data/data_query.py:get_stock_data()`
3. Update `DataPackage` in `terminal/pipeline.py` to include new field
4. New data available in `format_context()` for Claude prompts

### Add New Exposure Alert
1. Define rule in `portfolio/exposure/rules.py`
2. Implement check function (takes positions, returns alerts)
3. Register in `portfolio/exposure/alerts.py:run_all_checks()`
4. Alert automatically included in `run_monitor()` output

### Add New Investment Theme
1. Call `terminal/themes.py:create_theme(slug, name, thesis)`
2. Add members: `add_member(slug, "NVDA")`
3. Theme tracked in company DB meta: `data/companies/NVDA/meta.json`

---

## Testing Strategy

### Unit Tests
- Data Desk: `tests/test_data_query.py`
- Indicators: `tests/test_indicators.py`
- OPRMS: `tests/test_oprms.py`

### Integration Tests
- Full pipeline: `tests/test_pipeline.py`
- Company DB: `tests/test_company_db.py`

### Manual Validation
- End-to-end analysis: `analyze_ticker("AAPL", depth="full")`
- Monitor output: `run_monitor()`

---

## Performance Characteristics

| Operation | Time | Cost | Cache |
|-----------|------|------|-------|
| Data collection (FMP API) | 2-5s | $0 | 24h TTL |
| Indicator calculation | <1s | $0 | On-demand |
| Lens prompt generation | <1s | $0 | N/A |
| Claude lens analysis (6 lenses) | 30-60s | ~$2 | N/A |
| Claude debate (5 rounds) | 2-3min | ~$5-8 | N/A |
| Claude memo writing | 1-2min | ~$3-5 | N/A |
| Memo scoring | <1s | $0 | N/A |
| Company DB storage | <1s | $0 | N/A |

**Total for full analysis**: ~5 min, ~$13-15 (Claude API costs only, FMP free tier).

---

## Cloud Deployment

### Infrastructure
- **Server**: Aliyun ECS (Beijing region)
- **OS**: Ubuntu 20.04
- **SSH**: `ssh aliyun` (configured in `~/.ssh/config`)
- **Path**: `/root/workspace/Finance/`

### Sync Script
```bash
./sync_to_cloud.sh --code     # Sync src/, terminal/, knowledge/ only
./sync_to_cloud.sh --data     # Sync data/ only
./sync_to_cloud.sh --all      # Sync everything
```

Uses `rsync` with exclusions (`.venv/`, `.git/`, `__pycache__/`).

### Cron Jobs (Beijing Time)
```cron
# Price data update (daily, Tue-Sat 06:30)
30 6 * * 2-6 cd /root/workspace/Finance && .venv/bin/python scripts/update_data.py --price >> logs/cron_price.log 2>&1

# Dollar volume scan (daily, Tue-Sat 06:45)
45 6 * * 2-6 cd /root/workspace/Finance && .venv/bin/python scripts/update_data.py --scan >> logs/cron_scan.log 2>&1

# Stock pool refresh (weekly, Sat 08:00)
0 8 * * 6 cd /root/workspace/Finance && .venv/bin/python scripts/refresh_stock_pool.py >> logs/cron_pool.log 2>&1

# Fundamentals update (weekly, Sat 10:00)
0 10 * * 6 cd /root/workspace/Finance && .venv/bin/python scripts/update_data.py --fundamental >> logs/cron_fundamental.log 2>&1

# Database rebuild (weekly, Sat 12:00)
0 12 * * 6 cd /root/workspace/Finance && .venv/bin/python scripts/update_data.py --database >> logs/cron_database.log 2>&1
```

**Check Logs**:
```bash
ssh aliyun "tail -30 /root/workspace/Finance/logs/cron_price.log"
```

---

## File Count Summary

| Directory | Python Files | Total Lines | Purpose |
|-----------|--------------|-------------|---------|
| `terminal/` | 7 | 1,462 | Orchestration layer |
| `knowledge/` | 28 | ~3,500 | Investment frameworks |
| `src/` | 15 | ~2,000 | Data pipeline |
| `portfolio/` | 8 | ~1,200 | Holdings + exposure |
| `risk/` | 3 | ~500 | IPS + kill conditions |
| `trading/` | 2 | ~200 | Trade logs (stub) |
| `scripts/` | 10 | ~800 | Data maintenance |
| **Total** | **73** | **~9,662** | Entire workspace |

(Counts approximate, based on Phase 2 P0 commit `bda41f7`)

---

## Dependencies

**Python 3.10+** required.

**Core**:
- `numpy>=2.4` — Numerical computing (indicators)
- `pandas>=3.0` — Data manipulation (price data, financials)
- `requests>=2.32` — HTTP client (FMP API)
- `python-dateutil>=2.9` — Date parsing

**Optional** (for full feature set):
- Heptabase MCP server — Knowledge base integration
- FRED API — Macro regime detection

---

## Future Roadmap

### Phase 2a: Data Expansion
- Activate unused FMP endpoints (earnings estimates, insider trades, news)
- Add SPY/QQQ benchmarks for relative performance
- Integrate FRED API for macro indicators

### Phase 3: Automation
- Automated kill condition monitoring (price alerts, earnings triggers)
- Daily portfolio monitor with Telegram notifications
- Greeks monitoring for options positions

### Phase 4: Analytics
- Performance attribution by sector/theme/DNA tier
- Trade post-mortem automation (actual vs. expected IRR)
- Regime-adjusted position sizing

### Phase 5: AI Research Assistant
- SEC filing RAG (10-K/10-Q search + summarization)
- Earnings call transcript analysis
- News sentiment filtering

---

## Conventions

### File Naming
- Python modules: `snake_case.py`
- Data files: `{SYMBOL}.csv`, `{slug}.json`
- Markdown docs: `UPPERCASE.md` (top-level), `lowercase.md` (nested)

### Code Style
- Type hints required for all functions
- Docstrings: Google style
- Logging: Use `logger = logging.getLogger(__name__)`
- Error handling: Explicit try/except with context

### Data Formats
- **JSON**: Single-record data (oprms.json, meta.json)
- **JSONL**: Append-only logs (memos.jsonl, analyses.jsonl, oprms_history.jsonl)
- **CSV**: Tabular time series (price data)
- **SQLite**: Queryable aggregates (valuation.db)

### Git Workflow
- Main branch: `main`
- Commit message: `<type>: <description>` (e.g., "feat: Add earnings calendar endpoint")
- Data files: `data/companies/` is git-tracked (knowledge base), `data/price/` is `.gitignore`d (too large)

---

## Troubleshooting

### Data Desk Issues

**Problem**: FMP API rate limit exceeded
- **Cause**: >300 calls/min on Starter plan
- **Fix**: API client has 2s interval rate limiting (`src/data/fmp_client.py:15`)

**Problem**: Missing price data for ticker
- **Check**: `ls data/price/{SYMBOL}.csv`
- **Fix**: `python scripts/update_data.py --price`

**Problem**: Fundamentals outdated
- **Check**: `sqlite3 data/valuation.db "SELECT * FROM companies WHERE symbol='NVDA'"`
- **Fix**: `python scripts/update_data.py --fundamental`

### Terminal Layer Issues

**Problem**: `analyze_ticker()` fails on data collection
- **Check**: `python -c "from src.data.data_validator import print_data_report; print_data_report()"`
- **Fix**: Run data update scripts

**Problem**: Company DB read fails
- **Check**: `ls data/companies/{SYMBOL}/`
- **Fix**: Ensure directory exists; created on first `save_memo()` call

### Cloud Deployment Issues

**Problem**: Cron jobs not running
- **Check**: `ssh aliyun "crontab -l"`
- **Fix**: Verify cron syntax, check `.venv` activation in cron commands

**Problem**: Environment variables not loaded
- **Cause**: Cron runs non-interactive shell, `.bashrc` not sourced
- **Fix**: Use `.env` file, load with `python-dotenv`

---

## Glossary

- **DNA Rating**: Asset quality tier (S/A/B/C) determining max position size
- **Timing Rating**: Entry quality tier (S/A/B/C) determining position size coefficient
- **OPRMS**: Owen's Position & Risk Management System (DNA × Timing → Position)
- **Kill Condition**: Observable trigger for position invalidation (e.g., "Close below $400")
- **Investment Lens**: Analytical perspective (Business, Management, Financials, Growth, Valuation, Technical)
- **Debate Protocol**: 5-round adversarial analysis (Bull vs. Bear) to challenge thesis
- **DataPackage**: Aggregated ticker data (fundamentals, price, indicators, company record)
- **Company DB**: Per-ticker knowledge storage (`data/companies/{SYMBOL}/`)
- **Desk**: Functional domain in workspace (Data, Research, Risk, Trading, Portfolio, Knowledge)

---

Built with Claude Code by Anthropic.
