# AI in Investment Management: Practical Landscape (2025-2026)

Research date: 2026-02-06

---

## 1. AI-Powered Research Assistants for Investing

### How LLMs Analyze Financial Documents

**Earnings Call Analysis:**
- LLMs now process earnings call transcripts at scale, extracting sentiment per speaker, per sentence, and per topic
- AlphaSense's Smart Summaries use domain-fine-tuned LLMs on premium financial content to produce plain-language summaries with semantic search and sentiment analysis
- Verity's system maps executive and analyst word choices to 5-level sentiment (Positive / Slightly Positive / Neutral / Slightly Negative / Negative) by topic
- Needl.ai tracks how management sentiment evolves across consecutive quarters and compares against competitors
- LSEG's AI can identify 1,000+ topics, 4,000+ event types, and references to millions of entities in each transcript

**SEC Filing Analysis (10-K, 10-Q):**
- RAG (Retrieval-Augmented Generation) is the dominant architecture for filing analysis
- GPT-4 with RAG answers financial questions correctly 50-80% of the time vs ~19% without RAG (roughly 3x improvement)
- "Talk to EDGAR" platforms let users ask plain-English questions and get answers citing exact snippets from filings
- Agentic RAG (iterative, self-correcting retrieval) achieves a 68% win rate over simpler hierarchical approaches across 1,200 filings

**Agentic RAG Architecture for SEC Filings (6 steps):**
1. Query analysis and document identification (company, filing type, time period)
2. Retrieval strategy planning (target specific sections like MD&A, financial statements)
3. Document ingestion, chunking, and metadata tagging
4. Semantic vector retrieval
5. Corrective mechanisms (relevance filtering + fallback retrieval with query reformulation)
6. Answer synthesis with grounded citations

### Structured Outputs

Typical structured outputs from AI research pipelines include:

```json
{
  "ticker": "AAPL",
  "filing_type": "10-K",
  "period": "FY2025",
  "revenue_growth": 0.089,
  "sentiment": {
    "overall": "Slightly Positive",
    "score": 0.34,
    "management_tone": "Confident",
    "guidance_tone": "Cautious"
  },
  "key_risks": ["Supply chain concentration", "Regulatory pressure in EU"],
  "thesis_impact": "Supports bull case on services growth"
}
```

FinBERT provides per-sentence outputs: text, softmax probabilities for positive/negative/neutral, prediction label, and sentiment score. It achieves 89% accuracy on financial sentiment vs 76% for standard BERT.

### Example AI Research Workflows

**Workflow 1: Earnings Season Pipeline**
```
Earnings call transcript
  → FinBERT sentence-level sentiment scoring
  → LLM topic extraction (guidance, margins, competition, capex)
  → Structured summary (JSON with sentiment by topic)
  → Delta detection vs previous quarter
  → Thesis impact assessment
  → Alert if thesis-changing information detected
```

**Workflow 2: Filing Deep Dive**
```
New 10-K filed on EDGAR
  → Agentic RAG ingestion + chunking
  → Automated extraction of key financials
  → Risk factor comparison vs prior year (what changed?)
  → MD&A sentiment analysis
  → Flag material changes
  → Update company research note
```

**Workflow 3: MarketSenseAI Multi-Agent Approach**
```
Multiple data streams in parallel:
  Agent 1: Financial news processing
  Agent 2: Historical price analysis
  Agent 3: Company fundamentals (via SEC filings with RAG)
  Agent 4: Macroeconomic environment (institutional reports)
  → Merge signals → Investment recommendation with explanation

Performance: 125.9% cumulative return vs 73.5% for S&P 100 (2023-2024)
```

---

## 2. Automated Investment Analysis Pipelines

### Modern Automated Valuation Pipeline

```
Data Collection Layer
  ├── Financial statements (SEC EDGAR API, Financial Datasets API)
  ├── Market data (real-time prices, volumes)
  ├── Consensus estimates (analyst forecasts)
  ├── Industry comps data
  └── Macroeconomic indicators

Processing Layer
  ├── AI data extraction (near-perfect accuracy vs manual transposition)
  ├── Financial statement normalization
  ├── Historical trend analysis
  └── Peer group identification

Valuation Models
  ├── DCF Agent: Revenue projections → margins → FCF → terminal value → WACC → intrinsic value
  ├── Comps Agent: Select peers → calculate multiples → apply to target
  ├── Precedent Transactions Agent: M&A database → relevant deals → implied valuation
  └── Scenario Agent: Bull / Base / Bear cases with probability weighting

Synthesis Layer
  ├── Cross-model validation
  ├── Sensitivity analysis (automated)
  ├── Natural language explanation of key assumptions
  └── Confidence interval / range output
```

### Building "AI Analysts"

**V7 Go** automates DCF model creation by:
- Extracting financial data from multiple sources
- Applying consistent valuation methodologies
- Generating sensitivity analyses automatically
- Using AI optimized for numerical data to extract figures with near-perfect accuracy

**Practical approach for a personal AI analyst:**
1. Use LLM to extract historical financials from 10-K/10-Q filings
2. Build projection templates in Python/Google Sheets
3. Use LLM to generate assumption sets (bull/base/bear)
4. Calculate DCF programmatically
5. Use LLM to pull comparable company multiples
6. Cross-validate DCF vs comps output
7. Generate natural language investment memo

### Required Data Feeds

| Data Type | Sources | Update Frequency |
|-----------|---------|-----------------|
| Financial statements | SEC EDGAR, Financial Datasets API | Quarterly |
| Market prices | Yahoo Finance, Alpha Vantage, Polygon.io | Real-time / Daily |
| Analyst estimates | Visible Alpha, Refinitiv | As updated |
| Macro indicators | FRED, BLS, Treasury | Monthly/Quarterly |
| News & sentiment | NewsAPI, Bloomberg, RSS feeds | Continuous |
| Earnings transcripts | Seeking Alpha, LSEG, FinancialModelingPrep | Quarterly |
| Alternative data | Web traffic, satellite, app downloads | Varies |

---

## 3. Portfolio Monitoring with AI

### AI-Driven Risk Alerts

**JPMorgan's approach:** ML models monitoring trading books for early warning signals, analyzing market data and trading positions. Result: ~40% reduction in Value-at-Risk limit breaches.

**Key capabilities in production today:**
- Real-time anomaly detection across portfolio positions
- Wash-sale risk identification
- Compliance violation flagging
- Position concentration alerts
- Correlation breakdown detection (when historically uncorrelated assets start moving together)

### Anomaly Detection in Holdings

Modern platforms run three types of monitoring:
1. **Trend analysis** - Detecting deviations from expected patterns
2. **Anomaly detection** - Statistical outliers in price, volume, or fundamental metrics
3. **Limits monitoring** - Automated checks against pre-defined risk limits

AI models analyze real-time market data and behavioral signals to detect patterns suggesting price shifts and volatility.

### News Monitoring and Relevance Filtering

**Pipeline architecture:**
```
News aggregation (multiple sources)
  → NLP relevance scoring (is this about my holdings?)
  → Sentiment classification (FinBERT / LLM)
  → Materiality assessment (will this move the stock?)
  → Priority routing:
      High: Immediate alert (earnings miss, regulatory action, M&A)
      Medium: Daily digest (analyst upgrades, sector news)
      Low: Weekly summary (general industry trends)
```

### Macro Regime Detection

**Two Sigma's Production Approach:**
- Model: Gaussian Mixture Model (GMM) - unsupervised learning
- Input: 17 factors from Two Sigma Factor Lens (equity, credit, rates, inflation, FX, plus equity style factors: value, momentum, quality, low risk, small cap, trend)
- Data: Historical returns back to early 1970s

**Four identified market regimes:**

| Regime | Characteristics | Historical Examples |
|--------|----------------|-------------------|
| **Crisis** | Negative returns across equity and credit, elevated volatility, increased correlations | 1987 crash, 2008 GFC, 2020 COVID |
| **Steady State** | Positive performance across most factors, "normal and healthy" | 2010-2019 dominantly |
| **Inflation** | Strong returns in inflation hedges, FX appreciation | 1970s-1980s stagflation |
| **Walking on Ice** | Higher volatility, positive equity returns but fragility | Tech bubble recovery, post-GFC/COVID rebounds |

**Other approaches in production:**
- Hidden Markov Models (HMMs) - best at identifying regime shifts per research comparisons
- K-means clustering, agglomerative clustering
- Spectral clustering HMM (SC-HMM) hybrid
- State Street Global Advisors published "Decoding Market Regimes with Machine Learning" (2025) applying similar techniques

**Application:** Stress-test portfolios by sampling from regime distributions; trigger tactical rebalancing when regime probability shifts.

---

## 4. Knowledge Management for Investors

### How Professional Investors Organize Research

**Best practices observed in 2025-2026:**

1. **Thesis-centric organization** - Every position has a written thesis document
2. **Catalyst tracking** - Each thesis links to specific upcoming catalysts with dates
3. **Kill criteria** - Pre-defined conditions under which you exit, written before entering
4. **Evidence accumulation** - New data points tagged to relevant theses
5. **Contrarian log** - Explicitly tracking arguments against your positions

### Investment Thesis Tracking Framework

```
Thesis Document Structure:
├── Company: [Name]
├── Date initiated: [Date]
├── Current conviction: [High / Medium / Low]
├── Position size: [% of portfolio]
│
├── Bull Case
│   ├── Core thesis: [1-2 sentences]
│   ├── Key assumptions: [list]
│   ├── Target price / return: [value]
│   └── Catalysts: [{event, expected_date, probability}]
│
├── Bear Case
│   ├── What could go wrong: [list]
│   ├── Kill criteria: [specific thresholds]
│   └── Maximum loss tolerance: [value]
│
├── Evidence Log
│   ├── [Date] - [Event] - [Supports/Challenges thesis] - [Impact assessment]
│   └── ...
│
└── Decision History
    ├── [Date] - [Action] - [Rationale]
    └── ...
```

### "Second Brain" Approaches for Investment Knowledge

**Tools used by investors in 2025:**
- **Notion** - Most popular for structured databases (thesis tracking, catalyst calendars, earnings trackers); templates available with API sync for price data
- **Obsidian** - Preferred by knowledge-graph thinkers; linking companies → themes → macro views; local-first with full control
- **Heptabase** - Visual whiteboard approach; good for mapping relationships between ideas and themes
- **Roam Research** - Daily notes approach, good for capturing fleeting observations

**The key principle:** Your system should make it trivially easy to:
1. Capture a new insight (low friction)
2. Connect it to existing knowledge (links/tags)
3. Surface it when relevant (search/backlinks)
4. Review and update periodically (spaced review)

### Maintaining a Living Investment Framework

**Best practice: Layered knowledge architecture**
```
Layer 1: Worldview / Macro Framework
  - Your beliefs about how the economy works
  - Updated: Quarterly or when major regime shift occurs

Layer 2: Sector / Theme Theses
  - Your views on specific industries or secular trends
  - Updated: Monthly or on material news

Layer 3: Company Theses
  - Individual position rationales
  - Updated: On every earnings report, material news, or catalyst

Layer 4: Daily Observations
  - Market notes, price action observations, news reactions
  - Updated: Daily
  - Periodically promoted to Layer 2 or 3 if pattern emerges
```

---

## 5. Notable Open-Source and Accessible Projects

### AI Hedge Fund Projects on GitHub

| Project | Stars | Description | Stack |
|---------|-------|-------------|-------|
| **virattt/ai-hedge-fund** | 20k+ | Multi-agent system with persona-based agents (Buffett, Munger, Burry, etc.) plus specialized agents (technicals, fundamentals, sentiment, risk) | Python, LangGraph, GPT-4o/Llama 3 |
| **The-Swarm-Corporation/AutoHedge** | ~1k | Build autonomous hedge fund in minutes using swarm intelligence | Python, Swarms framework |
| **AI-Brokers/AIBrokers** | ~500 | First real-world AI hedge fund framework for crypto, fully open source | Python |
| **51bitquant/ai-hedge-fund-crypto** | ~1k | AI-powered crypto trading with multi-LLM support and backtesting | Python |
| **Undervalued-ai/ai-hedge-fund** | ~500 | Focus on undervalued stocks, with live performance tracking on undervalued.ai | Python |

### virattt/ai-hedge-fund Architecture (Most Popular)

```
Agent Layer:
  ├── Persona Agents (investment philosophy-based)
  │   ├── Warren Buffett Agent (value, moat, margin of safety)
  │   ├── Charlie Munger Agent (quality, mental models)
  │   ├── Ben Graham Agent (deep value, net-nets)
  │   ├── Cathie Wood Agent (disruptive innovation)
  │   ├── Bill Ackman Agent (activist, catalysts)
  │   └── Michael Burry Agent (contrarian, macro risks)
  │
  ├── Specialist Agents
  │   ├── Fundamentals Agent (revenue, cash flow, earnings)
  │   ├── Technicals Agent (moving averages, signals)
  │   ├── Sentiment Agent (NLP on news headlines)
  │   └── Valuation Agent (DCF, multiples)
  │
  └── Decision Agents
      ├── Risk Manager (position sizing, exposure limits)
      └── Portfolio Manager (final trade decisions)

Data: Financial Datasets API (AAPL, MSFT, NVDA, GOOGL, TSLA)
Orchestration: LangGraph (stateful graph workflows)
LLMs: OpenAI GPT-4o, Groq, Anthropic, or Ollama (Llama 3 local)
Backtesting: Built-in historical performance evaluation
```

### Other Notable Projects

**MarketSenseAI** (academic, arxiv:2502.00415):
- RAG + multi-agent LLM framework for stock analysis
- Processes SEC filings, earnings calls, news, macro reports
- Achieved 125.9% cumulative return vs 73.5% S&P 100 benchmark (2023-2024)
- Transparent: provides explanations for every recommendation

**TradingAgents** (tradingagents-ai.github.io):
- Multi-agent LLM financial trading framework
- Academic research project with open documentation

**SEC-RAG** (GitHub: sheikhhanif/SEC-RAG):
- SEC data extraction with RAG
- Open-source starter for building EDGAR analysis tools

### AI Agent Frameworks Used in Finance

| Framework | Best For | Production Users |
|-----------|----------|-----------------|
| **LangGraph** | Complex stateful workflows, fine-grained control | LinkedIn, Uber, 400+ companies |
| **CrewAI** | Role-based multi-agent teams, faster to ship | 60% of Fortune 500, 150+ enterprise |
| **AutoGen** (Microsoft) | Research-oriented multi-agent conversations | Academic / research |
| **OpenAI Agents SDK** | Simple single-agent with tools | Broad adoption |

---

## 6. The "AI Trading Desk" Concept

### Ideal AI-Augmented Personal Trading Desk

```
┌─────────────────────────────────────────────────────────┐
│                   HUMAN DECISION LAYER                   │
│  Strategy design, thesis formation, risk tolerance,      │
│  portfolio-level allocation, ethical/compliance judgment  │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                AI ORCHESTRATION LAYER                     │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ Research  │  │ Analysis │  │ Monitor  │              │
│  │ Agent     │  │ Agent    │  │ Agent    │              │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘              │
│       │              │              │                     │
│  ┌────▼─────┐  ┌────▼─────┐  ┌────▼─────┐              │
│  │ Earnings │  │ Valuation│  │ Risk     │              │
│  │ Screener │  │ Pipeline │  │ Alerts   │              │
│  │ News Agg │  │ DCF/Comps│  │ Regime   │              │
│  │ Filing   │  │ Scenario │  │ News     │              │
│  │ Analyzer │  │ Analysis │  │ Anomaly  │              │
│  └──────────┘  └──────────┘  └──────────┘              │
│                                                          │
│  ┌──────────────────────────────────────────┐           │
│  │         Knowledge Base / Second Brain     │           │
│  │  Thesis tracker, evidence log, catalyst   │           │
│  │  calendar, research notes, decision log   │           │
│  └──────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                   DATA LAYER                             │
│  Market data, EDGAR filings, news feeds, earnings       │
│  transcripts, macro indicators, alternative data         │
└─────────────────────────────────────────────────────────┘
```

### Functions That Benefit Most from AI Automation

| Function | AI Advantage | Automation Level |
|----------|-------------|-----------------|
| **Earnings call processing** | Read 100+ calls in hours vs weeks | Full automation |
| **Filing change detection** | Compare 10-K risk factors year-over-year | Full automation |
| **News relevance filtering** | Process thousands of articles, surface what matters | Full automation |
| **Sentiment scoring** | Consistent, scalable, no emotional bias | Full automation |
| **Data extraction** | Near-perfect accuracy from financial statements | Full automation |
| **Screening / scanning** | Process entire universes quickly | Full automation |
| **DCF model population** | Extract inputs, run calculations | High automation, human reviews assumptions |
| **Comparable analysis** | Identify peers, calculate multiples | High automation, human validates peer set |
| **Risk monitoring** | Real-time anomaly detection, limit checks | High automation, human sets limits |
| **Regime detection** | Pattern recognition across many variables | High automation, human interprets implications |
| **Research note drafting** | First draft from data, human edits | Medium automation |
| **Thesis updating** | Flag relevant new information | Medium automation, human updates thesis |

### What Should Remain Human-Judgment-Only

Based on 2025 consensus from industry practitioners and researchers:

1. **Strategy design and thesis formation** - "Algorithms don't create themselves; it takes human experience and market understanding"
2. **Risk tolerance and position sizing decisions** - Personal risk appetite is inherently human
3. **Interpreting unprecedented events** - AI trained on history struggles with truly novel situations (e.g., COVID, regulatory paradigm shifts)
4. **Ethical and compliance oversight** - What should and shouldn't be automated is a human decision
5. **Complex contextual analysis** - Politics, social behavior, second-order effects
6. **When to override the system** - Knowing when the model is wrong requires human judgment
7. **Capital allocation across strategies** - Meta-level portfolio decisions
8. **Relationship and qualitative judgment** - Management quality assessment, corporate culture evaluation

**The 2025 consensus:** "The best-performing funds are not those that rely exclusively on machines or humans but those that achieve seamless orchestration between the two."

---

## Key Takeaways for Building a Personal AI Investment System

### Start Here (Highest Impact, Lowest Effort)

1. **Earnings call summarizer** - Use FinBERT + LLM to process transcripts into structured summaries with sentiment
2. **SEC filing RAG** - Build a simple agentic RAG pipeline to query your holdings' filings in natural language
3. **News relevance filter** - Automated pipeline that scores and filters news for your specific holdings
4. **Thesis tracker** - Structured documents (Notion/Obsidian/Heptabase) with catalyst dates and kill criteria

### Build Next (Medium Effort, High Value)

5. **Multi-agent research system** - LangGraph-based pipeline inspired by virattt/ai-hedge-fund architecture
6. **Automated valuation pipeline** - DCF + comps with LLM-populated assumptions
7. **Regime detection** - GMM or HMM on factor data to identify current market regime

### Aspirational (High Effort, Transformative)

8. **Full AI trading desk** - Integrated system with research, analysis, monitoring, and knowledge management
9. **Personalized AI analyst** - Fine-tuned on your investment style and historical decisions
10. **Automated thesis updating** - System that continuously evaluates new information against existing theses

---

## Sources

- [MarketSenseAI 2.0: Enhancing Stock Analysis through LLM Agents](https://arxiv.org/html/2502.00415v2)
- [LLMs for Financial Document Analysis: SEC Filings & Decks](https://intuitionlabs.ai/articles/llm-financial-document-analysis)
- [AI in Finance Part 3: Clues in Earnings Calls](https://stockfisher.app/ai-earnings-calls-analysis)
- [AWS: Building an AI-powered assistant for investment research](https://aws.amazon.com/blogs/machine-learning/part-3-building-an-ai-powered-assistant-for-investment-research-with-multi-agent-collaboration-in-amazon-bedrock-and-amazon-bedrock-data-automation/)
- [Best AI Tools for Investment Research in 2026](https://cognitivefuture.ai/best-ai-tools-for-investment-research/)
- [Benchmark of 30 Finance LLMs in 2026](https://research.aimultiple.com/finance-llm/)
- [V7 Go DCF Modeling Agent](https://www.v7labs.com/agents/dcf-modeling-agent)
- [How AI Enhances DCF Valuation Accuracy](https://www.lucid.now/blog/how-ai-enhances-dcf-valuation-accuracy/)
- [AI in Portfolio Management: A Comprehensive Guide (2025)](https://rtslabs.com/ai-in-portfolio-management/)
- [MSCI AI Portfolio Insights](https://www.msci.com/our-solutions/analytics/risk-management/ai-portfolio-insights)
- [Guardfolio AI Portfolio Risk Alerts](https://www.guardfolio.ai/blog/alerts)
- [Two Sigma: A Machine Learning Approach to Regime Modeling](https://www.twosigma.com/articles/a-machine-learning-approach-to-regime-modeling/)
- [BlackRock: How Machine Learning is Enhancing Macro Investing](https://www.blackrock.com/institutions/en-global/institutional-insights/thought-leadership/machine-learning-macro-investing)
- [State Street: Decoding Market Regimes with Machine Learning](https://www.ssga.com/library-content/assets/pdf/global/pc/2025/decoding-market-regimes-with-machine-learning.pdf)
- [virattt/ai-hedge-fund on GitHub](https://github.com/virattt/ai-hedge-fund)
- [Build an AI Hedge Fund with Open Source](https://apidog.com/blog/open-source-ai-hedge-fund/)
- [AutoHedge on GitHub](https://github.com/The-Swarm-Corporation/AutoHedge)
- [AlphaSense Smart Summaries for Earnings](https://www.alpha-sense.com/blog/product/smart-summaries-earnings-analysis/)
- [Captide: How to do Agentic RAG on SEC EDGAR Filings](https://www.captide.ai/insights/how-to-do-agentic-rag-on-sec-edgar-filings)
- [FinBERT on GitHub](https://github.com/ProsusAI/finBERT)
- [AI vs. Human Decision-Making in Algorithmic Trading](https://www.ainvest.com/news/ai-human-decision-making-algorithmic-trading-2025-investment-analysis-2601/)
- [The TRADE Predictions 2026: Artificial Intelligence](https://www.thetradenews.com/the-trade-predictions-series-2026-artificial-intelligence/)
- [AI-Driven Trading: How Intelligent Execution Tools Are Changing Retail Investing in 2026](https://centralbucksnews.com/news/2025/dec/11/ai-driven-trading-how-intelligent-execution-tools-are-changing-retail-investing-in-2026/)
- [TradingAgents: Multi-Agents LLM Financial Trading Framework](https://tradingagents-ai.github.io/)
- [LangGraph vs CrewAI Comparison](https://www.zenml.io/blog/langgraph-vs-crewai)
