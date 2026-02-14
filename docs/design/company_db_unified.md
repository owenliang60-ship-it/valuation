# Company Database 统一项目说明

**日期**: 2026-02-13
**状态**: 设计完成，待实施

---

## 背景

深度分析流程（11 agent pipeline）已稳定运行，但分析成果存储存在结构性问题：

1. **company_db.py 架构空转** — 提供了 save_memo/save_analysis/save_debate/save_alpha_package 等完整接口，但几乎没有代码调用它们
2. **数据散落** — 分析结果以 markdown 文件形式写入 `data/companies/{SYMBOL}/research/` 目录，绕过了结构化存储
3. **无法查询** — 想看"所有 DNA=S 的公司"或"最近 30 天分析过的标的"需要手动翻文件
4. **股票池覆盖不一致** — 只有 18 个被分析过的 ticker 有 company 目录，池内 99 只大部分没有档案

## 目标

建立一个统一的 SQLite 数据库 (`data/company.db`)，作为公司档案的 single source of truth：

- 覆盖所有曾分析过的公司 + 当前股票池，用 `in_pool` 标记区分
- 每次深度分析后自动提取结构化摘要写入数据库
- `data/companies/{SYMBOL}/research/` 保留为原始 agent 输出归档
- 提供 HTML Dashboard 供人工浏览、排序、筛选
- 为未来 Portfolio（持仓/交易）预留扩展空间

## 架构设计

### 数据层级

```
data/company.db (SQLite)           ← 结构化查询入口
  ├── companies        全池公司基础档案
  ├── oprms_ratings    OPRMS 评级（当前 + 历史）
  ├── analyses         每次深度分析的结构化摘要
  └── kill_conditions  触杀条件

data/companies/{SYMBOL}/research/  ← 原始 agent 输出归档（不变）
  └── {YYYYMMDD_HHMMSS}/
      ├── lens_*.md, debate.md, memo.md, oprms.md, alpha_*.md
      ├── full_report_{date}.md / .html
      └── prompts/

data/valuation.db                  ← 原始财务数据（不变）
  ├── companies        FMP 公司档案
  └── financials       季度/年度财报
```

### SQLite Schema

```sql
-- 公司档案表
CREATE TABLE companies (
    symbol TEXT PRIMARY KEY,
    company_name TEXT DEFAULT '',
    sector TEXT DEFAULT '',
    industry TEXT DEFAULT '',
    exchange TEXT DEFAULT '',
    market_cap REAL,
    in_pool INTEGER DEFAULT 0,      -- 1 = 当前在股票池内
    source TEXT DEFAULT '',          -- pool / analysis / both
    first_seen TEXT,
    updated_at TEXT
);

-- OPRMS 评级（is_current=1 为最新，0 为历史）
CREATE TABLE oprms_ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL REFERENCES companies(symbol),
    dna TEXT NOT NULL,               -- S/A/B/C
    timing TEXT NOT NULL,            -- S/A/B/C
    timing_coeff REAL NOT NULL,      -- 0.1-1.5
    conviction_modifier REAL,        -- Alpha 层调整系数
    evidence TEXT,                   -- JSON array of strings
    investment_bucket TEXT DEFAULT '',-- Catalyst-Driven Long / Long-term Compounder / Watch / Pass
    verdict TEXT DEFAULT '',         -- BUY/HOLD/SELL/PASS
    position_pct REAL,              -- 最终仓位 %
    is_current INTEGER DEFAULT 1,
    created_at TEXT NOT NULL
);

-- 分析摘要（每次深度分析一行）
CREATE TABLE analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL REFERENCES companies(symbol),
    analysis_date TEXT NOT NULL,
    depth TEXT DEFAULT 'deep',
    -- 5 lens verdicts (每个 JSON: {stars, verdict, irr, thesis})
    lens_quality_compounder TEXT,
    lens_imaginative_growth TEXT,
    lens_fundamental_long_short TEXT,
    lens_deep_value TEXT,
    lens_event_driven TEXT,
    -- Debate
    debate_verdict TEXT,             -- BUY/HOLD/SELL
    debate_summary TEXT,
    -- Memo
    executive_summary TEXT,
    key_forces TEXT,                  -- JSON array
    -- Alpha layer
    red_team_summary TEXT,
    cycle_position TEXT,
    conviction_modifier REAL,
    asymmetric_bet_summary TEXT,
    -- OPRMS snapshot
    oprms_dna TEXT,
    oprms_timing TEXT,
    oprms_timing_coeff REAL,
    oprms_position_pct REAL,
    -- Context
    price_at_analysis REAL,
    regime_at_analysis TEXT,
    -- File paths
    research_dir TEXT,
    report_path TEXT,
    html_report_path TEXT,
    created_at TEXT NOT NULL
);

-- Kill conditions
CREATE TABLE kill_conditions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL REFERENCES companies(symbol),
    description TEXT NOT NULL,
    source_lens TEXT DEFAULT '',
    is_active INTEGER DEFAULT 1,
    created_at TEXT NOT NULL
);
```

### 未来扩展（Portfolio，暂不实施）

```sql
-- CREATE TABLE holdings (symbol, shares, avg_cost, ...);
-- CREATE TABLE trades (symbol, date, action, shares, price, reason, ...);
-- CREATE TABLE portfolio_snapshots (date, total_value, ...);
```

## 文件变更清单

### 新建

| 文件 | 行数 | 职责 |
|------|------|------|
| `terminal/company_store.py` | ~350 | SQLite CRUD 后端 |
| `terminal/dashboard.py` | ~400 | HTML Dashboard 生成器 |
| `scripts/migrate_company_db.py` | ~200 | 一次性数据迁移 |
| `tests/test_company_store.py` | ~250 | 单元测试 |

### 修改

| 文件 | 改动 | 内容 |
|------|------|------|
| `terminal/deep_pipeline.py` | +200 行 | `extract_structured_data()` + auto-save hook |
| `terminal/company_db.py` | +30 行 | 兼容桥接（双写 SQLite + 优先读 SQLite） |
| `terminal/commands.py` | +10 行 | `dashboard()` 命令 |

### 不修改

pipeline.py, monitor.py, freshness.py, html_report.py, themes.py — 通过 company_db.py 桥接层透明切换。

## 关键设计决策

### 1. 为什么新建 company_store.py 而不是改造 company_db.py？

company_db.py 是文件系统后端（JSON/JSONL/MD），接口设计围绕文件操作。SQLite 后端的接口语义不同（upsert, query, join），强行塞进去会让代码混乱。新建一个干净的 SQLite 模块，让 company_db.py 做薄桥接层，逐步迁移。

### 2. 为什么 analyses 表存摘要而不是完整内容？

完整 lens 分析 5 篇 × 3-5KB = 15-25KB，加上 debate/memo/alpha 总计 40-60KB。SQLite 能存，但这些富文本用 markdown 文件更适合（可直接阅读、版本控制）。analyses 表存结构化摘要（verdict、评分、关键结论），通过 `research_dir` 字段链接到原始文件。

### 3. extract_structured_data() 的容错策略

LLM 输出格式不可预测（已知陷阱：debate 格式至少 3 种变体）。提取策略：
- 复用 html_report.py 中已验证的正则提取函数（_extract_rating_line, _extract_debate_verdict, _extract_oprms_dna 等）
- 每个字段独立提取，失败存 None 不崩溃
- 记 warning log，分析行仍然创建（部分数据好过没数据）

### 4. company.db vs valuation.db 的关系

- **valuation.db**: 原始财务数据仓库（季度/年度财报，FMP 导入），96 家公司
- **company.db**: 分析成果档案（OPRMS 评级、分析摘要、kill conditions），所有分析过的公司
- 两者通过 symbol 关联，但各自独立。valuation.db 由云端 cron 维护，company.db 由本地分析流程维护

### 5. 迁移数据来源

| 数据源 | 记录数 | 导入内容 |
|--------|--------|---------|
| `data/valuation.db` companies 表 | 96 | company_name, sector, industry, exchange, market_cap |
| `data/pool/universe.json` | 99 | in_pool 标记, source |
| `data/companies/` 目录 | 18 | oprms.json → oprms_ratings, kill_conditions.json, 最新 research 数据 → analyses |

## HTML Dashboard 设计

单页自包含 HTML，复用 html_report.py 的 warm bright CSS 主题。

**功能**：
- 可排序表格（点击列头）
- Sector 筛选下拉框
- "全部 / 池内 / 已分析" 切换按钮
- DNA/Timing 颜色编码（S=gold, A=green, B=blue, C=muted）
- Verdict 颜色（BUY=green, HOLD=amber, SELL=red）
- Symbol 可点击跳转到完整 HTML 报告
- 顶部汇总统计（总数、已分析、DNA 分布）

**生成方式**：`dashboard()` 命令 → 读 company.db → 生成 `data/dashboard.html`

## 实施顺序

1. **Phase A**: company_store.py + tests — SQLite schema + CRUD
2. **Phase B**: extract_structured_data() + tests — 从 research markdown 提取结构化数据
3. **Phase C**: compile_deep_report() hook + company_db.py 桥接 — 接线
4. **Phase D**: migrate_company_db.py — 迁移现有数据
5. **Phase E**: dashboard.py + commands.py — HTML Dashboard
6. **Phase F**: 端到端验证 — 跑一次深度分析确认全链路

## 验证 Checklist

- [ ] `pytest tests/test_company_store.py -v` 全通过
- [ ] `pytest tests/ -v` 全量测试不回归（418+）
- [ ] 迁移脚本运行，`sqlite3 data/company.db "SELECT COUNT(*) FROM companies"` 返回 ~99+
- [ ] 对一个 ticker 跑深度分析，company.db 自动写入 analyses + oprms_ratings
- [ ] `data/dashboard.html` 浏览器打开，表格可排序、筛选正常
- [ ] 现有 `commands.py` 的 `company_lookup()` 功能不受影响

## 相关文件参考

- `terminal/company_db.py` (314 行) — 现有文件后端，将加桥接层
- `terminal/deep_pipeline.py` (690 行) — compile_deep_report() 在 554 行，hook 点
- `terminal/html_report.py` (950 行) — CSS 主题 + 提取函数可复用
- `knowledge/oprms/models.py` (120 行) — OPRMSRating/DNARating/TimingRating 定义
- `terminal/freshness.py` (500 行) — AnalysisContext/FreshnessReport 定义
- `data/valuation.db` — companies 表 96 行, financials 表 1247 行
- `data/pool/universe.json` — 99 只股票（77 screener + 22 analysis）
