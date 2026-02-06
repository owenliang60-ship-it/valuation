# Professional Hedge Fund Operations: Comprehensive Research Report

**Date:** 2026-02-06
**Purpose:** Understanding institutional hedge fund operations to identify replicable practices for a solo/small fund operator

---

## Table of Contents

1. [Desk/Department Structure](#1-deskdepartment-structure)
2. [Technology Infrastructure](#2-technology-infrastructure)
3. [Data Infrastructure](#3-data-infrastructure)
4. [Workflow/Process: Research to Execution](#4-workflowprocess-research-to-execution)
5. [Risk Management Framework](#5-risk-management-framework)
6. [Systematic vs. Discretionary: Key Differences](#6-systematic-vs-discretionary-key-differences)
7. [Essential Subset for Solo/Small Fund Operator](#7-essential-subset-for-solosmall-fund-operator)

---

## 1. Desk/Department Structure

### 1.1 Multi-Strategy Hedge Fund Organizational Models

There are two dominant organizational paradigms:

**"One-Book" Model (e.g., Citadel)**
- Centralized CIO makes top-level allocation decisions
- Shared formats, investment styles, ideas, and analysis across pods
- More "Citadel formula" — universal experience
- Pods have less autonomy but access deeper firm-wide resources
- Technology, risk, compliance, and ops are centralized

**"Platform/Pod-Shop" Model (e.g., Millennium)**
- Each PM runs a quasi-independent mini hedge fund ("pod")
- Pods manage their own P&L within their sector focus
- Higher autonomy, less cross-pollination of ideas
- The parent fund provides infrastructure: data, trading systems, compliance, capital
- More aggressive about closing underperforming pods (strict drawdown limits)

### 1.2 Core Desks/Departments

#### Front Office (Revenue-Generating)

| Desk/Department | Function | Key Personnel |
|-----------------|----------|---------------|
| **Equity Long/Short** | Fundamental stock picking, sector-specific analysis, long and short positions | PM, Senior Analysts, Junior Analysts |
| **Global Macro** | Trading based on macroeconomic themes across rates, FX, commodities, equities | PM, Macro Strategists, Economists |
| **Quantitative/Systematic** | Algorithm-driven strategies, factor models, statistical arbitrage | Quant Researchers, Quant Developers, Data Scientists |
| **Event-Driven/Special Situations** | M&A arbitrage, distressed debt, restructurings, activist positions | PM, Event Analysts, Legal Specialists |
| **Credit/Fixed Income** | Corporate bonds, structured products, interest rate trading | PM, Credit Analysts, Traders |
| **Relative Value/Arbitrage** | Exploiting price dislocations between related instruments | PM, Quant Analysts, Execution Traders |
| **Options/Volatility** | Volatility trading, options strategies, Greeks management | Volatility PM, Options Traders, Quant Analysts |
| **Trading/Execution** | Execution of all orders, best execution, market microstructure | Head Trader, Execution Traders, Algo Traders |

#### Middle Office (Risk & Analytics)

| Desk/Department | Function | Key Personnel |
|-----------------|----------|---------------|
| **Risk Management** | Firm-wide risk monitoring, VaR, stress testing, exposure limits, drawdown controls | Chief Risk Officer (CRO), Risk Analysts, Quant Risk Modelers |
| **Portfolio Analytics** | Performance attribution, factor decomposition, P&L explanation | Portfolio Analysts, Quant Analysts |
| **Compliance** | Regulatory compliance, trade surveillance, reporting (Form PF, Form SHO, etc.) | Chief Compliance Officer (CCO), Compliance Analysts |

#### Back Office (Operations)

| Desk/Department | Function | Key Personnel |
|-----------------|----------|---------------|
| **Operations** | Trade settlement, reconciliation, cash management, corporate actions | COO, Operations Analysts |
| **Fund Accounting** | NAV calculation, investor reporting, fee computation | CFO, Fund Accountants |
| **Technology/Infrastructure** | Systems development, data engineering, platform maintenance | CTO, Software Engineers, DevOps, Data Engineers |
| **Investor Relations** | Capital raising, LP reporting, communication | IR Director, IR Associates |
| **Legal** | Fund structuring, regulatory, contract negotiation | General Counsel, Legal Associates |
| **HR/Talent** | Recruiting (especially PM talent for pod shops) | HR Director |

### 1.3 The Pod Model in Detail

A "pod" in a multi-manager platform typically consists of:
- **1 Portfolio Manager** — full P&L authority, position sizing, strategy selection
- **2-5 Analysts** — research, modeling, idea generation
- **0-1 Dedicated Trader** — execution (or shared execution desk)

The parent platform provides:
- Centralized risk management (sits outside pods by design to prevent gaming)
- Shared technology infrastructure (data feeds, compute, networks)
- Compliance and operations
- Capital allocation (can increase/decrease pod allocations based on performance)
- Intraday monitoring and firm-wide drawdown controls

**Key pod economics:**
- PMs typically receive 10-20% of their pod's P&L as compensation
- Strict stop-loss limits (e.g., a pod hitting -5% drawdown may get capital cut; -7% to -10% may be shut down)
- Millennium is more aggressive about closing pods; Citadel considers longer-term track record

### 1.4 Reporting Hierarchy

```
Board of Directors / Founder
├── Chief Investment Officer (CIO)
│   ├── Pod 1: PM → Analysts → Trader
│   ├── Pod 2: PM → Analysts → Trader
│   ├── Pod N: PM → Analysts → Trader
│   └── Quant Research Team (shared)
├── Chief Risk Officer (CRO)
│   └── Risk Analysts & Quant Risk
├── Chief Operating Officer (COO)
│   ├── Operations
│   ├── Fund Accounting
│   └── Investor Relations
├── Chief Technology Officer (CTO)
│   ├── Trading Systems
│   ├── Data Engineering
│   └── Infrastructure
├── Chief Compliance Officer (CCO)
│   └── Compliance & Legal
└── Chief Financial Officer (CFO)
    └── Finance & Reporting
```

---

## 2. Technology Infrastructure

### 2.1 Core Systems Architecture

The institutional hedge fund technology stack is layered:

```
┌─────────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                          │
│  Dashboards / Risk Reports / PM Workstations / Mobile Alerts   │
├─────────────────────────────────────────────────────────────────┤
│                     APPLICATION LAYER                           │
│  OMS │ EMS │ PMS │ Risk Engine │ Compliance │ Analytics        │
├─────────────────────────────────────────────────────────────────┤
│                     DATA LAYER                                  │
│  Market Data │ Reference Data │ Position Data │ Historical DB   │
├─────────────────────────────────────────────────────────────────┤
│                     INFRASTRUCTURE LAYER                        │
│  Cloud/On-Prem │ Low-Latency Network │ Co-location │ DR/BCP    │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 System-by-System Breakdown

#### Order Management System (OMS)

**What it does:**
- Central hub for all order lifecycle management
- Order creation, routing, allocation, and compliance checks
- Pre-trade compliance (position limits, restricted lists, regulatory constraints)
- Order blotter — real-time view of all orders and their status
- Allocation across accounts/funds
- Audit trail for regulatory purposes

**Leading vendors:**
- **Charles River IMS** (State Street) — market leader for buy-side
- **Bloomberg AIM** — integrated with Bloomberg data ecosystem
- **Eze OMS** (SS&C) — popular with mid-size hedge funds
- **Enfusion** — cloud-native, integrated OMS/PMS
- **AlphaDesk** (LSEG) — integrated order management

**Key features hedge funds look for (2025 trends):**
- Tight OMS/EMS integration (or unified OEMS)
- Cross-asset class support (equities, options, futures, FX, credit)
- API-driven architecture for custom integration
- Real-time compliance checks embedded in workflow
- Multi-prime broker connectivity

#### Execution Management System (EMS)

**What it does:**
- Real-time market data display and trading interface
- Smart order routing (SOR) across venues
- Algorithmic execution (VWAP, TWAP, implementation shortfall, etc.)
- Direct market access (DMA)
- Transaction cost analysis (TCA)
- Real-time execution analytics

**Leading vendors:**
- **FlexTrade** — highly customizable, multi-asset
- **Bloomberg EMSX** — integrated with Bloomberg terminal
- **Fidessa** (ION) — strong in equities
- **Portware** (FactSet) — algorithmic execution
- **LSEG (Refinitiv) EMS** — advanced multi-asset EMS

**Key distinction from OMS:**
- OMS = "what to trade" (portfolio-level, compliance, allocation)
- EMS = "how to trade" (market access, execution quality, speed)
- Modern trend: Converging into OEMS (Order & Execution Management Systems)

#### Portfolio Management System (PMS)

**What it does:**
- Real-time portfolio positions and P&L
- NAV calculation
- Performance attribution (by sector, factor, strategy, time period)
- Cash management and forecasting
- What-if scenario analysis
- Multi-currency, multi-asset class support
- Shadow accounting (verifying administrator NAV)

**Leading vendors:**
- **Enfusion** — cloud-native, all-in-one (PMS + OEMS + analytics + compliance)
- **Geneva** (SS&C) — industry standard for complex funds
- **Eze PMA** (SS&C) — portfolio management and accounting
- **BlackRock Aladdin** — enterprise-grade (used by the largest funds)
- **SimCorp Dimension** — comprehensive investment management
- **Quantifi** — strong in derivatives pricing and risk
- **HedgeGuard** — specialized for hedge funds

**2025 trends:**
- Cloud-native SaaS solutions reducing infrastructure burden
- Real-time data replacing end-of-day batch processing
- Embedded trade controls and compliance
- Open APIs for custom analytics integration

#### Risk Management System

**What it does:**
- Real-time risk aggregation across all portfolios/pods
- VaR (Value-at-Risk) — historical, parametric, Monte Carlo
- Expected Shortfall (CVaR)
- Stress testing (historical scenarios + hypothetical)
- Factor exposure analysis (market, sector, style, geography)
- Correlation monitoring and regime detection
- Liquidity risk assessment
- Counterparty risk monitoring
- Greeks aggregation (for options portfolios)
- Limit monitoring and alerting (hard and soft limits)

**Leading vendors:**
- **BlackRock Aladdin** — gold standard for large institutions
- **MSCI RiskMetrics / Barra** — factor models and risk analytics
- **Axioma** (SimCorp) — factor-based risk models
- **Bloomberg PORT** — integrated with Bloomberg terminal
- **Northstar Risk** — performance and risk attribution
- **RiskVal** — fixed income and derivatives risk
- Custom in-house systems (most large quant funds build their own)

**Key metrics monitored:**
- Portfolio VaR (1-day, 10-day) at 95% and 99% confidence
- Gross and net exposure
- Beta-adjusted exposure
- Sector/geography/factor concentration
- Maximum drawdown tracking
- Correlation matrices (rolling, real-time)

#### Market Data Systems

**What it does:**
- Real-time streaming prices (Level I and Level II)
- Historical time series (tick, minute, daily)
- Reference data (corporate actions, identifiers, classifications)
- News feeds and event data
- Economic data releases

**Leading vendors:**
- **Bloomberg** — $32,000/year per terminal, the industry standard
- **Refinitiv/LSEG Workspace** — ~$22,000/year, strong historical data
- **FactSet** — ~$12,000/year, comprehensive analytics
- **ICE Data Services** — broad market data coverage
- **Nasdaq Global Data Services** — exchange data
- **Polygon.io** — API-first, cost-effective for equities/options/crypto
- **Databento** — modern, low-cost market data API

**Cost context:** Large multi-strategy funds spend millions annually on data, typically working with 20+ data vendors at ~$80,000 per dataset average.

#### Analytics Platforms

**What it does:**
- Quantitative research environment
- Backtesting frameworks
- Factor modeling
- Statistical analysis
- Visualization and reporting

**Common tools:**
- **Python ecosystem** (pandas, numpy, scipy, scikit-learn, PyTorch)
- **R** (still used for statistical research)
- **MATLAB** (legacy, declining)
- **Jupyter notebooks** / JupyterHub (research collaboration)
- **kdb+/q** (KX) — ultra-fast time series database, industry standard for tick data
- **Databricks** — cloud-based data engineering and ML
- **AWS/GCP/Azure** — cloud compute for backtesting at scale
- Custom in-house platforms (most serious quant funds)

#### Compliance & Reporting Systems

**What it does:**
- Pre-trade compliance checks (embedded in OMS)
- Post-trade surveillance
- Regulatory reporting (Form PF, Form SHO, Form 13F, etc.)
- AML/KYC monitoring
- Communication archiving (Bloomberg chat, email, WhatsApp, WeChat — now required)
- Code of ethics monitoring
- Restricted/watch list management

**Key regulatory requirements (2025-2026):**
- **Form PF** — Required for funds with $150M+ AUM; quarterly for $500M+. Updated requirements effective October 2025.
- **Form SHO** — New requirement effective January 2, 2025. Institutional managers must disclose short positions.
- **Form 13F** — Quarterly disclosure of holdings for managers with $100M+ in 13F securities.
- **AML compliance** — Enhanced due diligence requirements.
- **Communication archiving** — Must capture and archive all business messages across all platforms.

**Leading vendors:**
- **SteelEye** — trade surveillance and compliance for hedge funds
- **NICE Actimize** — market abuse surveillance
- **Global Relay** — communication archiving
- **ComplySci** — personal trading compliance
- **ACA Compliance** — outsourced compliance

#### Communication Systems

| System | Purpose | Cost Indication |
|--------|---------|-----------------|
| **Bloomberg Terminal** | Market data + messaging + execution + analytics (the Swiss Army knife) | $32K/year |
| **Symphony** | Secure messaging (many funds moved from Bloomberg chat) | Varies |
| **Slack/Teams** | Internal collaboration | Standard enterprise pricing |
| **Bloomberg IB (Instant Bloomberg)** | Industry-standard trader-to-trader communication | Included with terminal |
| **Recorded phone lines** | All trading lines must be recorded | Part of telecom setup |
| **Email archiving** | Regulatory requirement | Part of compliance stack |

### 2.3 Integration Architecture

A critical challenge is making all these systems talk to each other:

```
Bloomberg Terminal ←→ OMS ←→ EMS ←→ Brokers/Exchanges
       ↓                ↓        ↓
    Market Data    Compliance   TCA Reports
       ↓                ↓
      PMS ←→ Risk Engine ←→ Factor Models
       ↓                ↓
   Accounting     Stress Tests
       ↓
  Investor Reports
```

**Integration methods:**
- FIX Protocol (Financial Information eXchange) — standard for order routing
- REST/WebSocket APIs — modern data feeds and system integration
- FTP/SFTP — legacy file-based integration (still common for end-of-day)
- Message queues (Kafka, RabbitMQ) — event-driven architecture

---

## 3. Data Infrastructure

### 3.1 Market Data

#### Real-Time Data
- **Level I:** Best bid/ask, last trade, volume — essential for all trading
- **Level II/Order Book:** Full depth of market — critical for execution quality
- **Options chains:** Real-time Greeks, implied volatility surfaces
- **Futures:** Contract specs, roll schedules, open interest
- **FX:** Interbank rates, crosses
- **Fixed Income:** Bond prices, yields, spreads (harder to get, less centralized)

#### Historical Data
- **Tick data:** Every trade and quote, timestamped to microsecond — used for backtesting, microstructure research
- **Bar data:** OHLCV at various frequencies (1-min, 5-min, daily)
- **Adjusted prices:** Corporate action adjusted for accurate total return calculation
- **Options historical:** Historical chains, implied volatility surfaces, Greeks
- **Fundamental snapshots:** Point-in-time financial data (critical for avoiding look-ahead bias in backtesting)

#### Storage & Processing
- **kdb+/q** — The industry standard for tick data storage and analysis. Column-oriented, optimized for time series. Used by most serious quant funds.
- **Arctic** (Man AHL) — Open-source high-performance datastore for pandas DataFrames
- **TimescaleDB** / **InfluxDB** — Time series databases
- **Parquet/Delta Lake** — Columnar storage on cloud data lakes
- **Cloud solutions** — Snowflake, BigQuery, Redshift for analytical workloads

### 3.2 Fundamental Data

| Data Type | Sources | Use Case |
|-----------|---------|----------|
| Financial statements | Bloomberg, FactSet, S&P Capital IQ, Refinitiv | Valuation models, screening |
| Earnings estimates | Bloomberg, FactSet, I/B/E/S | Earnings surprise models |
| Ownership/13F | SEC EDGAR, WhaleWisdom | Institutional positioning |
| Insider transactions | SEC EDGAR, Bloomberg | Sentiment signal |
| Corporate actions | Bloomberg, ICE, Exchange feeds | Portfolio maintenance |
| Credit ratings | Moody's, S&P, Fitch | Credit analysis |
| ESG data | MSCI ESG, Sustainalytics | Compliance, screening |

### 3.3 Alternative Data

The alternative data market has exploded. Hedge funds spend ~$1.6M annually across ~20 vendors on average, though only 48% of large funds ($1B+ AUM) currently invest in it.

| Data Category | Examples | Vendors | Signal Type |
|---------------|----------|---------|-------------|
| **Satellite imagery** | Parking lot counts, oil storage, crop health, construction | SkyFi, RS Metrics, Orbital Insight | Nowcasting economic activity |
| **Geolocation/foot traffic** | Store visits, foot traffic patterns | SafeGraph, Placer.ai | Consumer activity |
| **Credit card/transaction** | Consumer spending patterns | Bloomberg Second Measure, Earnest | Revenue estimation |
| **Web scraping** | Pricing data, product listings, job postings | Bright Data, Thinknum | Competitive intelligence |
| **Social media/sentiment** | Twitter/X, Reddit, StockTwits | RavenPack, Sentifi | Sentiment signals |
| **News/NLP** | News analytics, earnings call transcripts | RavenPack, AlphaSense | Event detection |
| **Patent filings** | Innovation pipeline | IFI Claims, Google Patents | R&D signals |
| **Government data** | Regulatory filings, customs data | Quandl/Nasdaq, ImportGenius | Policy/trade signals |
| **App usage** | Download counts, usage patterns | Apptopia, Sensor Tower | Product adoption |
| **Supply chain** | Shipping data, supplier relationships | Panjiva, AxeTrading | Supply chain signals |

**2025 reality:** The largest datasets from the biggest providers are now ubiquitous — consumed by thousands of trading desks simultaneously, leading to overcrowded trades and faster alpha decay. The edge increasingly comes from:
1. **Unique datasets** that aren't widely available
2. **Superior processing** — extracting signals others miss
3. **Speed** — acting on data faster than competitors
4. **Combination** — synthesizing multiple datasets in novel ways

### 3.4 News & Sentiment Data

- **RavenPack** — Converts unstructured content to structured data using NLP for 12M+ entities
- **AlphaSense** — AI-powered search across filings, transcripts, news, broker research
- **Bloomberg News** — Integrated with terminal, machine-readable news feed
- **Dow Jones/Factiva** — Comprehensive news database
- **Reuters News** — Real-time news feed

### 3.5 Macro Economic Data

| Data Type | Sources |
|-----------|---------|
| GDP, CPI, employment, etc. | FRED (free), Bloomberg, Refinitiv |
| Central bank communications | Fed, ECB, BOJ websites; NLP-parsed via vendors |
| Yield curves | Bloomberg, Treasury Direct |
| PMI, ISM | IHS Markit, ISM |
| Housing data | Case-Shiller, Census Bureau |
| Trade data | Census Bureau, customs data |
| Nowcasting models | Atlanta Fed GDPNow, Bloomberg Economics |
| High-frequency indicators | Weekly unemployment, daily mobility |

---

## 4. Workflow/Process: Research to Execution

### 4.1 The Investment Pipeline

```
IDEA GENERATION → RESEARCH → RISK ASSESSMENT → SIZING → APPROVAL → EXECUTION → MONITORING → POST-TRADE
```

### 4.2 Stage-by-Stage Detail

#### Stage 1: Idea Generation

**Sources of ideas:**
- **Systematic/Quant:** Factor screens, statistical anomalies, model signals, alternative data signals
- **Fundamental:** Industry contacts, conferences, channel checks, supply chain analysis, management meetings
- **Top-down:** Macro regime analysis, policy changes, geopolitical events, sector rotation signals
- **Cross-desk:** Ideas from one strategy informing another (more common in Citadel-style one-book models)
- **AI/GenAI (2025 trend):** LLMs analyzing earnings transcripts, filings, and news to surface ideas faster. Generative AI is being used to "expedite research workflows and enable faster identification of alpha-generating ideas"

**What makes a good idea (the "edge"):**
- **Informational edge** — You know something others don't (from unique data or deep primary research)
- **Analytical edge** — You interpret widely available data better
- **Behavioral edge** — You can act differently from the crowd (true contrarian conviction)
- **Structural edge** — You can access markets/instruments others can't (e.g., illiquid credit, emerging markets)

**Standardized idea format:** Most funds require analysts to present ideas in a structured format:
- Investment thesis (1-2 sentences)
- Key catalysts (what will make the market reprice)
- Variant perception (why the market is wrong)
- Target price and timeframe
- Risk factors and downside scenario
- Suggested position size
- Conviction level (high/medium/low)

#### Stage 2: Research & Due Diligence

**Fundamental approach:**
1. Financial modeling (3-statement model, DCF, comparable analysis)
2. Industry/competitive analysis
3. Management quality assessment
4. Channel checks (talking to suppliers, customers, competitors)
5. Expert network calls (GLG, AlphaSights)
6. Site visits
7. Earnings call review and transcript analysis

**Quantitative approach:**
1. Data collection and cleaning
2. Feature engineering
3. Model development (factor models, ML models)
4. In-sample/out-of-sample testing
5. Walk-forward analysis
6. Parameter sensitivity analysis
7. Regime analysis

**Time spent:** Research analysts typically spend 60-70% of their time on financial modeling, data screening, and earnings forecasting.

#### Stage 3: Risk Assessment

Before any position is approved:
- **Standalone risk:** What's the max loss on this position?
- **Portfolio context:** How does this correlate with existing positions?
- **Factor exposure:** Does this add unwanted factor tilts (momentum, value, size, quality)?
- **Liquidity:** How many days to exit the position? (ADV analysis)
- **Event risk:** Upcoming earnings, regulatory decisions, macro events?
- **Tail risk:** What happens in a 2008-type scenario?
- **Concentration:** Does this breach sector/geography/position limits?

#### Stage 4: Position Sizing

**Common approaches:**
- **Equal risk contribution** — Each position contributes equal volatility to portfolio
- **Kelly Criterion / Fractional Kelly** — Optimal geometric growth sizing. In practice, professional money managers use 0.10x to 0.15x Kelly to manage career risk (a 30% drawdown can be career-ending)
- **Volatility-adjusted sizing** — Position size inversely proportional to expected volatility
- **Conviction-weighted** — Higher conviction = larger size, within risk limits
- **Risk budget allocation** — Each strategy/pod gets a VaR budget, positions sized to fit within it
- **Maximum position limits** — Hard caps (e.g., no single position > 5% of portfolio)

#### Stage 5: Approval & Compliance

**Pre-trade checks (automated in OMS):**
- Restricted list check
- Position limit check
- Concentration limit check
- Leverage limit check
- Regulatory compliance (short-selling rules, etc.)
- Cross-fund compliance (avoiding conflicts)

**PM/CIO approval:**
- Small positions within risk budget: PM discretion (no additional approval)
- Larger positions or new strategies: CIO sign-off required
- In pod shops: PM has full authority within their allocated risk budget

#### Stage 6: Execution

**Execution workflow:**
1. PM sends order to trading desk (or directly via EMS if PM also trades)
2. Trader selects execution strategy:
   - **Algorithmic:** VWAP, TWAP, Implementation Shortfall, Percentage of Volume
   - **Direct Market Access (DMA):** For speed-sensitive trades
   - **Dark pools:** For large orders to minimize market impact
   - **Broker facilitation:** For less liquid instruments
3. Smart order routing splits across venues for best execution
4. Real-time monitoring of execution quality
5. Post-trade TCA (Transaction Cost Analysis)

**Systematic/quant funds:**
- Execution is automated end-to-end
- Models generate signals → orders auto-generated → algo execution
- Humans monitor but rarely intervene
- Focus on minimizing market impact and execution costs

#### Stage 7: Monitoring

**Real-time monitoring (continuous):**
- P&L by position, strategy, pod, firm
- Risk metrics (VaR, exposure, Greeks)
- Factor exposure drift
- Correlation changes
- News and event alerts on holdings
- Liquidity conditions
- Margin and cash positions

**Periodic monitoring:**
- Daily: P&L review, risk report, exposure summary
- Weekly: Strategy review, sector/factor tilt analysis
- Monthly: Performance attribution, investor reporting
- Quarterly: Deep strategy review, allocation decisions

#### Stage 8: Post-Trade Analysis

**P&L Attribution (PnL Explain):**
Decomposes daily P&L into root causes:
- Market moves (delta)
- Volatility changes (vega)
- Time decay (theta)
- Curve/spread changes
- Residual/unexplained

**Performance Attribution:**
- **Ex-post (Brinson-Fachler):** Allocation effect, selection effect, interaction effect
- **Factor-based:** Returns decomposed into factor exposures (market, size, value, momentum, quality)
- **Ex-ante:** Risk-based attribution predicting future contribution to risk and return

**Trade Journal / Lessons Learned:**
- Was the thesis correct?
- Was the sizing appropriate?
- Was execution optimal?
- What signals should have prompted earlier exit?
- How did the position contribute to portfolio risk?

---

## 5. Risk Management Framework

### 5.1 Multi-Level Risk Architecture

Institutional risk management operates at multiple levels simultaneously:

```
FIRM LEVEL
├── Total firm VaR limit
├── Gross/Net exposure limits
├── Maximum drawdown triggers
├── Liquidity reserves
│
├── STRATEGY/POD LEVEL
│   ├── Per-pod VaR allocation
│   ├── Per-pod drawdown limit (e.g., -5% warning, -7% capital cut, -10% close)
│   ├── Sector/factor concentration limits
│   ├── Leverage limits per strategy
│   │
│   └── POSITION LEVEL
│       ├── Max position size (% of portfolio or ADV)
│       ├── Stop-loss per position
│       ├── Single-name concentration
│       └── Liquidity threshold (days to exit)
```

### 5.2 Key Risk Metrics

| Metric | What It Measures | Typical Limits |
|--------|-----------------|----------------|
| **VaR (95%, 1-day)** | Expected daily loss not exceeded 95% of the time | 1-3% of NAV for aggressive funds |
| **VaR (99%, 1-day)** | Tail risk measure | Often 1.5-2x the 95% VaR |
| **Expected Shortfall (CVaR)** | Average loss beyond VaR threshold | Supplements VaR for tail risk |
| **Gross Exposure** | Total longs + total shorts as % of NAV | 200-600% for pod shops (leveraged) |
| **Net Exposure** | Longs - Shorts as % of NAV | -20% to +40% for market neutral; wider for directional |
| **Beta-Adjusted Net** | Net exposure adjusted for portfolio beta | Target near 0 for market neutral |
| **Single Position Limit** | Max size of any one position | 2-5% of NAV typically |
| **Sector Concentration** | Max exposure to any one sector | 15-25% of gross |
| **Top 5 Concentration** | Weight of top 5 positions | Monitored, varies by strategy |
| **Liquidity (Days to Exit)** | How many days to liquidate at 20-25% of ADV | 80-90% of portfolio liquidable in <5 days |
| **Maximum Drawdown** | Peak-to-trough loss threshold | -5% warning; -10% emergency action |
| **Factor Exposure** | Exposure to systematic risk factors | "Stock-specific risk should drive returns; factor risk typically <20%" |

### 5.3 Stress Testing

**Historical scenarios:**
- 2008 Global Financial Crisis
- 2020 COVID crash
- 2022 UK Gilt crisis
- 1998 LTCM / Russian default
- 2011 European sovereign crisis
- Flash crashes (2010, 2015)

**Hypothetical scenarios:**
- Interest rates +300bps
- Equity markets -30%
- Credit spreads +500bps
- Volatility spike (VIX to 80)
- Correlation convergence (all assets correlate to 1)
- Liquidity freeze (no ability to exit positions)
- Geopolitical shock (Taiwan, Middle East, etc.)
- Currency crisis

**Frequency:** Daily for key scenarios; weekly for full battery; ad hoc for emerging risks.

### 5.4 Correlation Monitoring

This is one of the most critical and often underappreciated risk functions:

- **Rolling correlation matrices** between all positions and strategies
- **Regime detection** — correlations change dramatically in stress (assets that appeared uncorrelated become highly correlated)
- **Pod independence monitoring** — in multi-manager platforms, checking that pods aren't inadvertently taking similar bets (crowding risk)
- **Factor correlation** — monitoring correlation to systematic factors
- **Cross-asset correlation** — equities vs. rates vs. credit vs. FX vs. commodities

**Key lesson from 2008 and recent pod shop stress:**
> "When volatility rises, correlations converge and pods that looked independent started moving together. Risk models built on historical correlations failed to capture the speed of regime change."

### 5.5 Drawdown Management

**Institutional approach:**
1. **Stop-loss levels** per position, per pod, per firm
2. **Dynamic risk budgeting** — reduce position sizes as drawdown increases
3. **Automatic de-risking triggers** — at certain drawdown levels, systematic reduction
4. **Circuit breakers** — halt new position-taking at firm-level drawdown thresholds
5. **Recovery protocol** — after drawdown, gradually rebuild positions with tighter risk limits

**Pod shop specifics (Millennium/Citadel model):**
- -3% to -5% drawdown: Risk review, possible capital reduction
- -5% to -7% drawdown: Significant capital reduction, strategy review
- -7% to -10% drawdown: Pod closure considered
- These strict limits allow the platform to lever up the strategies with confidence

---

## 6. Systematic vs. Discretionary: Key Differences

### 6.1 Structural Comparison

| Dimension | Discretionary Fund | Systematic/Quant Fund | Hybrid (2025 trend) |
|-----------|-------------------|----------------------|---------------------|
| **Decision maker** | Human PM | Algorithm/model | Human guided by systematic signals |
| **Research output** | Investment memos, models | Code, backtests, papers | Both |
| **Holding period** | Weeks to months | Minutes to weeks (varies) | Mixed |
| **Number of positions** | 20-80 | 100-10,000+ | 50-500 |
| **Key talent** | Analysts, sector experts | Quant researchers, data scientists, engineers | Both |
| **Edge source** | Deep domain expertise, relationships | Data processing, speed, scale | Combined |
| **Capacity** | Often capacity-constrained | Can scale with capital and data | Moderate |
| **Tech spend** | Moderate (Bloomberg, PMS) | Very high (custom infrastructure) | High |
| **Human headcount** | Analyst-heavy | Engineer-heavy | Balanced |

### 6.2 Technology Stack Differences

**Discretionary fund tech stack:**
- Bloomberg Terminal (primary workstation)
- OMS/EMS (commercial off-the-shelf)
- PMS (commercial)
- Excel (still widely used for modeling)
- CRM for investor relations
- Communication archiving

**Systematic/quant fund tech stack:**
- Custom execution engine
- Custom risk engine
- kdb+/q or custom time series database
- Python/C++/Java research and production code
- Kubernetes/cloud infrastructure for compute
- Custom backtesting framework
- ML/AI infrastructure (GPUs, model training pipeline)
- Data engineering pipeline (Airflow, Spark, etc.)
- Monitoring and alerting systems
- Version control and CI/CD for trading strategies

### 6.3 Performance Characteristics

Recent research (2025):
- Systematic funds exhibit **higher Sharpe ratios** and **factor-adjusted alphas** than discretionary funds in equity hedge strategies
- Discretionary traders tend to **outperform during periods of uncertainty** (economic downturns, market crashes) — when models trained on historical data may fail
- By 2025, algorithmic trading accounts for ~89% of global trading volume

### 6.4 The Convergence Trend

The line between discretionary and systematic is blurring:
- **Macro funds** are using systematic overlays and data-driven frameworks
- **Quant funds** are incorporating qualitative inputs and human override capabilities
- **Multi-strategy platforms** often house both discretionary and systematic pods
- **"Quantamental"** — term for firms combining quantitative signals with fundamental research
- Discretionary PMs increasingly rely on systematic screening tools, factor monitors, and risk dashboards
- AI/LLMs are accelerating this convergence by automating parts of the research process

---

## 7. Essential Subset for Solo/Small Fund Operator

### 7.1 The Core Question

For a solo operator managing a few million dollars, the goal is NOT to replicate a Citadel. It's to identify which institutional practices provide the highest ROI relative to effort and cost, and adapt them to a one-person operation.

### 7.2 Tier 1: Non-Negotiable (Must Have)

These are practices that, if skipped, will eventually cause significant losses:

#### A. Risk Management Framework (Cost: $0 — just discipline)

This is the single most valuable institutional practice to replicate.

**What to implement:**
1. **Position sizing rules** — Define max position size (e.g., 2-5% of portfolio). Use fractional Kelly (0.1-0.25x Kelly) or volatility-targeted sizing.
2. **Hard stop-losses** — Per position (e.g., -10% to -15%) and portfolio-level (e.g., -5% monthly drawdown triggers reduced sizing).
3. **Exposure limits** — Define max gross exposure, max net exposure, max sector concentration.
4. **Daily risk review** — 10 minutes each morning reviewing exposure, P&L, correlations. Non-negotiable.
5. **Drawdown protocol** — Written rules for what happens at -5%, -10%, -15%, -20% drawdown. Decide now, not during the drawdown.
6. **Correlation awareness** — Understand how your positions correlate. Periodically check if your "diversified" portfolio is actually taking one big bet.

**The institutional insight:** The pod shops' strict drawdown limits (close the pod at -7%) are brutal but they work. Having pre-defined, automatic de-risking rules removes emotion.

#### B. Trade Journal & Post-Trade Analysis (Cost: $0 — just discipline)

**What to implement:**
1. Log every trade: thesis, entry, size, exit, P&L, lessons
2. Monthly performance attribution: what drove returns? (market, sector, stock-specific, timing)
3. Quarterly strategy review: what's working, what isn't, should anything change?

**The institutional insight:** Every institutional desk does P&L attribution daily. You need to know if you're making money from skill or from hidden factor bets.

#### C. Structured Investment Process (Cost: $0 — just discipline)

**What to implement:**
1. Written investment thesis for every position
2. Pre-defined catalysts and timeframe
3. Pre-defined exit criteria (both profit and loss)
4. Checklist before each trade (risk check, correlation check, sizing check)

**The institutional insight:** Standardized idea formats force rigor. Analysts who must write down their thesis catch more flaws than those who trade on gut feel.

### 7.3 Tier 2: High Value (Should Have)

These provide significant edge or efficiency but require some investment:

#### D. Market Data & Research Platform (Cost: $50-500/month)

**Recommended stack for a solo operator:**
- **Koyfin** ($35-65/month) — Bloomberg-like analytics, screening, charting at 1/40th the cost
- **TradingView** ($15-60/month) — Charting, screening, community
- **Polygon.io or Databento** ($29-200/month) — API access to market data for systematic work
- **FRED** (free) — Macro data
- **SEC EDGAR** (free) — Filings
- **OpenBB** (free/open-source) — Open-source financial terminal

**Skip Bloomberg** ($32K/year) unless you need the messaging network or institutional-grade bond/derivatives data.

#### E. Portfolio Management & Tracking (Cost: $0-200/month)

**Options:**
- **Interactive Brokers** — Built-in portfolio analytics, risk, and reporting (if they're your broker)
- **Custom Python dashboard** — Build your own using your existing quant skills. Track positions, P&L, risk metrics, factor exposures.
- **Sharesight/Portfolio Visualizer** — Simple tracking
- **Notion/Obsidian + spreadsheet** — Manual but flexible for a small portfolio

**What to track:**
- Real-time P&L by position
- Gross and net exposure
- Sector concentration
- Greeks (if trading options)
- Correlation matrix of top positions
- Performance vs. benchmark

#### F. Systematic Screening & Signal Pipeline (Cost: $0-200/month)

**What to implement:**
- Automated daily screens (you already have scanners for PMARP, RVOL, ADL, EMA120 in Quant/)
- Signal aggregation dashboard
- Backtest framework for new ideas
- Universe definition and maintenance

**The institutional insight:** Even discretionary PMs at top funds now rely on systematic screening. The idea isn't to fully automate, but to systematically surface opportunities and let human judgment do the final filtering.

### 7.4 Tier 3: Nice to Have (When Scaling)

These become important if/when AUM grows or you take on outside capital:

#### G. Formal Compliance Framework (Cost: varies)

**When needed:** If managing OPM (Other People's Money), Form PF/ADV filing, personal trading policies, communication archiving.

**For self-managed capital:** Keep clean records for tax purposes, but formal compliance is overkill.

#### H. Execution Management (Cost: $0 with good broker)

**For a few million:** Your broker's built-in algos (VWAP, TWAP) are sufficient. Interactive Brokers offers sophisticated algo execution.

**When to upgrade:** If you're trading enough volume that market impact matters, or if you're executing systematically at high frequency.

#### I. Professional Fund Administration (Cost: $2-5K/month)

**When needed:** If you launch a formal fund structure with outside investors.

**For self-managed:** Your broker's statements + your own tracking is sufficient.

### 7.5 The Solo Operator's Daily Workflow

Adapting institutional workflow to one person:

```
MORNING (30 min)
├── Review overnight/pre-market developments
├── Check risk dashboard (exposure, P&L, margin)
├── Review signals from automated scanners
├── Check economic calendar for today's events
└── Prioritize: any positions need attention?

MID-DAY (as needed)
├── Execute planned trades
├── Monitor open positions
├── Research new ideas (deep work time)
└── Log any trades taken

END OF DAY (15 min)
├── Daily P&L review
├── Update trade journal
├── Scan for tomorrow's catalysts
└── Assess: are all positions within risk limits?

WEEKLY (1 hour)
├── Performance attribution review
├── Factor exposure check
├── Correlation analysis
├── Pipeline review (what ideas are developing?)
└── Adjust risk budget if needed

MONTHLY (2-3 hours)
├── Full performance review and attribution
├── Strategy-level analysis (what's working/not)
├── Market regime assessment
├── Review and update watchlists
└── Administrative (tax records, broker reconciliation)
```

### 7.6 Recommended Technology Stack (Total: ~$100-400/month)

| Function | Tool | Cost |
|----------|------|------|
| **Broker** | Interactive Brokers | Per-trade commissions |
| **Market Data/Research** | Koyfin + TradingView | $50-125/month |
| **Data API** | Polygon.io or yfinance (free) | $0-79/month |
| **Portfolio Dashboard** | Custom Python + IB API | $0 (your time) |
| **Risk Monitoring** | Custom Python scripts | $0 (your time) |
| **Screening/Signals** | Your existing Quant scanners | Already built |
| **Trade Journal** | Notion or custom | $0-10/month |
| **Backtesting** | Python (backtrader/vectorbt) | $0 |
| **Macro Data** | FRED + TradingEconomics | $0-50/month |
| **Cloud Compute** | Your existing Aliyun server | Already have |
| **Communication** | Standard (no institutional need) | $0 |

### 7.7 The 80/20 of Institutional Practices

**What matters most (ranked):**

1. **Risk management discipline** — Position limits, stop-losses, drawdown protocols. This alone separates survivors from blow-ups.
2. **Structured process** — Written theses, checklists, standardized formats. Forces rigor.
3. **Post-trade review** — P&L attribution, trade journal, learning from mistakes. The institutional "error log."
4. **Factor awareness** — Understanding your hidden exposures. Are you long beta? Long momentum? Know what's driving your P&L.
5. **Systematic screening** — Let computers scan the universe; let your brain make the final call.
6. **Correlation monitoring** — Your "diversified" portfolio may be one big bet in disguise.
7. **Data quality** — Clean, reliable data for decisions. Don't trade on garbage data.

**What you can safely skip:**

- Multi-prime broker setups (you have one broker)
- Formal compliance infrastructure (until managing OPM)
- Enterprise OMS/EMS (your broker handles this)
- Communication archiving (until regulatory requirement)
- Investor relations infrastructure (no LPs)
- Fund administration (until formal fund structure)
- Real-time intraday risk systems (unless high-frequency)

---

## Sources

- [Goldman Sachs: Industrializing Alpha — Multi-Manager Hedge Funds](https://am.gs.com/en-us/advisors/insights/article/2024/multi-manager-hedge-funds-modern-allocation-strategies)
- [CAIS: Introduction to Multi-Strategy Hedge Funds](https://www.caisgroup.com/articles/an-introduction-to-multi-strategy-hedge-funds)
- [HedgeCo: Largest Hedge Funds Diversifying Strategy 2026](https://www.hedgeco.net/news/01/2026/todays-largest-hedge-funds-are-diversifying-strategy-and-redefining-alpha-in-2026.html)
- [The Pod Shop Revolution: How Multi-Strategy Funds Generated 13.6% Returns](https://medium.com/@navnoorbawa/the-pod-shop-revolution-how-multi-strategy-funds-generated-13-6-returns-while-markets-stumbled-8e090d97b68b)
- [How Millennium, Citadel & Point72 Structure Pods](https://navnoorbawa.substack.com/p/how-millennium-citadel-and-point72)
- [Citadel is from Mars and Millennium is from Venus](https://rupakghose.substack.com/p/citadel-is-from-mars-and-millennium)
- [Fintech4Funds: Top Asset Management Systems 2025](https://fintech4funds.com/fund-managers-guide-to-asset-management-systems-2024/)
- [LSEG: EMS Solutions for Hedge Funds](https://www.lseg.com/en/insights/data-analytics/unlocking-the-power-of-advanced-ems-solutions-for-hedge-funds)
- [Quantifi: 10 Factors Driving Hedge Funds to Adopt New PMS/OMS](https://www.quantifisolutions.com/the-10-factors-driving-hedge-funds-to-adopt-a-new-pms-oms/)
- [Enfusion Portfolio Management](https://www.enfusion.com/portfolio-management/)
- [PromptCloud: Alternative Data Strategies for Hedge Funds](https://www.promptcloud.com/blog/alternative-data-strategies-for-hedge-funds/)
- [AIMA: Casting The Net — How Hedge Funds Use Alternative Data](https://www.aima.org/static/8778b1e4-75c3-44e4-b35dc38e1495001e/Casting-The-Net-v10.pdf)
- [Sigma Computing: Evolution of Hedge Funds in the Data Era](https://www.sigmacomputing.com/blog/the-evolution-of-hedge-funds-in-the-data-era)
- [Verity: 5 Hedge Fund Workflows That Drive Operational Alpha](https://verityplatform.com/resources/hedge-fund-workflows/)
- [Street of Walls: Stock Idea Generation](https://www.streetofwalls.com/finance-training-courses/hedge-fund-training/stock-idea-generation/)
- [Resonanz Capital: Risk Mitigation with Hedge Funds](https://resonanzcapital.com/insights/risk-mitigation-with-hedge-funds-an-allocators-approach-and-the-lessons-that-endure)
- [Resonanz Capital: Checklist for Assessing Risk Management](https://resonanzcapital.com/insights/checklist-for-assessing-hedge-fund-managers-risk-management-approach)
- [FundCount: Risk Management in Hedge Funds](https://fundcount.com/risk-management-in-hedge-funds/)
- [HedgeGuard: Risk & Compliance System](https://www.hedgeguard.com/portfolio-management-system-hedge-fund/risk-compliance/)
- [The Hedge Fund Journal: Portfolio Management with Drawdowns](https://thehedgefundjournal.com/portfolio-management-with-drawdowns/)
- [Alpha Theory: Kelly Criterion in Practice](https://www.alphatheory.com/blog/kelly-criterion-in-practice-1)
- [QuantStart: Money Management via Kelly Criterion](https://www.quantstart.com/articles/Money-Management-via-the-Kelly-Criterion/)
- [Confluence GP: Systematic vs. Discretionary Trading](https://www.confluencegp.com/articles-and-news/systematic-vs-discretionary-trading-which-strategy-fits-your-fund/)
- [HedgeCo: Biggest Hedge Funds Doubling Down on Machine-Driven Scale](https://www.hedgeco.net/news/02/2026/why-the-biggest-hedge-funds-are-doubling-down-on-machine-driven-scale.html)
- [BlueGamma: Bloomberg Terminal Alternatives 2025](https://www.bluegamma.io/post/bloomberg-terminal-alternatives)
- [Koyfin: Best Bloomberg Terminal Alternatives 2026](https://www.koyfin.com/blog/best-bloomberg-terminal-alternatives/)
- [V-Comply: Hedge Fund Compliance Requirements 2025](https://www.v-comply.com/blog/hedge-fund-compliance-requirements/)
- [Arcesium: Regulatory Reporting Requirements Explained](https://www.arcesium.com/blog/hedge-funds-regulatory-reporting-requirements-explained)
- [FundCount: How Small Hedge Funds Can Survive 2024](https://fundcount.com/how-small-to-mid-size-hedge-funds-can-survive-2024/)
- [Broadridge: Hedge Funds Leveraging Technology for Growth](https://www.broadridge.com/article/asset-management/hedge-funds-leveraging-innovative-technology-for-growth)
- [KX: Real-Time Hedge Fund Analytics](https://kx.com/blog/best-practices-for-hedge-fund-analytics/)
- [KX: Building Unified Data Ecosystem for Hedge Funds](https://kx.com/blog/hedge-funds-build-unified-data-ecosystem/)
- [Bookmap: Complete Guide to Real-Time Market Data Feeds 2025](https://bookmap.com/en/blog/the-complete-guide-to-real-time-market-data-feeds-what-traders-need-to-know-in-2025)
- [RyanEyes: Hedge Funds — Front, Middle and Back Office Roles](https://www.ryaneyes.com/blog/roles-in-a-hedge-fund/)
- [Mergers & Inquisitions: Hedge Fund Career Path](https://mergersandinquisitions.com/hedge-fund-career-path/)
- [Northstar Risk: Performance Attribution Analysis](https://www.northstarrisk.com/expostperformanceattributionanalysis)
- [KX: P&L Attribution Analysis in Finance](https://kx.com/glossary/pl-attribution-analysis-in-finance/)
