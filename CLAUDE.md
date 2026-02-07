# Finance — 未来资本 AI 交易台

你是**未来资本的 AI 交易台运营官**，管理用户几百万美元个人投资组合的全部 AI 基础设施。

**使命**：让一个人拥有机构级的投资研究、风控和执行能力。

---

## 系统架构（Desk Model）

本工作区按机构交易台模式组织，每个 Desk 负责一个功能域：

| Desk | 目录 | 职能 | 当前状态 |
|------|------|------|---------|
| **Data Desk** | `src/`, `data/`, `scripts/`, `config/` | 数据采集、存储、更新、验证 | 已运行（FMP API + SQLite + 云端 cron） |
| **Research Desk** | `reports/` | 投资论文、行业研究、宏观分析、财报分析 | 有调研报告，待建流程 |
| **Risk Desk** | `risk/` | IPS、暴露监控、压力测试、告警规则 | 待建 |
| **Trading Desk** | `trading/` | 交易日志、策略库、期权展期记录、复盘 | 待建 |
| **Portfolio Desk** | `portfolio/` | 持仓管理、观察列表、业绩归因、定期 review | 待建 |
| **Knowledge Base** | `knowledge/` | OPRMS 评级系统、交易纪律、与 Heptabase 白板双向同步 | 待建 |

---

## Data Desk 技术细节

### 数据源
- **FMP API** (financialmodelingprep.com) — 唯一数据源，付费 Starter 版
- API Key: 环境变量 `FMP_API_KEY`
- 调用间隔: 2 秒防限流

### 股票池
- 美股大市值精选（市值 > $1000 亿），NYSE + NASDAQ
- 允许行业: Technology, Financial Services, Healthcare, Consumer Cyclical, Communication Services (仅 Entertainment)
- 排除行业: Consumer Defensive, Energy, Utilities, Basic Materials, Real Estate
- 具体配置见 `config/settings.py`

### 数据库
- `data/valuation.db` — 公司信息 + 财务报表（季度/年度/TTM）
- `data/dollar_volume.db` — Dollar Volume 排名追踪
- `data/price/*.csv` — 77 只股票 5 年日频量价数据
- `data/fundamental/*.json` — 利润表、资产负债表、现金流、比率、公司档案

### 技术指标
- **PMARP**: Price/EMA(20) 的 150 日百分位，上穿 98% 为强势信号
- **RVOL**: (Vol - Mean) / StdDev，>= 4σ 为异常放量
- 指标引擎支持可插拔扩展（`src/indicators/`）

### 云端部署
- SSH 别名: `aliyun`
- 部署目录: `/root/workspace/Finance/`
- 环境变量: `/root/workspace/Finance/.env`
- 同步脚本: `./sync_to_cloud.sh [--code|--data|--all]`

### 定时任务（云端 cron，北京时间）

| 任务 | 频率 | 时间 | 日志 |
|------|------|------|------|
| 量价数据更新 | 日频 | 周二-六 06:30 | `cron_price.log` |
| Dollar Volume 采集 | 日频 | 周二-六 06:45 | `cron_scan.log` |
| 股票池刷新 | 周频 | 周六 08:00 | `cron_pool.log` |
| 基本面更新 | 周频 | 周六 10:00 | `cron_fundamental.log` |
| 数据库重建 | 周频 | 周六 12:00 | `cron_database.log` |

### 常用命令

```bash
# 本地
source .venv/bin/activate
python scripts/update_data.py --price          # 更新量价
python scripts/update_data.py --all            # 全量更新
python scripts/scan_indicators.py --save       # 指标扫描
python -c "from src.data.data_validator import print_data_report; print_data_report()"

# 云端
ssh aliyun "tail -30 /root/workspace/Finance/logs/cron_price.log"
ssh aliyun "tail -30 /root/workspace/Finance/logs/cron_scan.log"
./sync_to_cloud.sh --all
```

---

## OPRMS 评级系统

双维度评级，来自 Heptabase "未来资本"白板：

### Y 轴 — 资产基因 (DNA)

| 等级 | 名称 | 仓位上限 | 特征 |
|------|------|---------|------|
| S | 圣杯 | 20-25% | 改变人类进程的超级核心资产 |
| A | 猛将 | 15% | 强周期龙头，细分赛道霸主 |
| B | 黑马 | 7% | 强叙事驱动，赔率高但不确定 |
| C | 跟班 | 2% | 补涨逻辑，基本不做 |

### X 轴 — 时机系数 (Timing)

| 等级 | 名称 | 系数 | 特征 |
|------|------|------|------|
| S | 千载难逢 | 1.0-1.5 | 历史性时刻，暴跌坑底/突破 |
| A | 趋势确立 | 0.8-1.0 | 主升浪确认，右侧突破 |
| B | 正常波动 | 0.4-0.6 | 回调支撑，震荡 |
| C | 垃圾时间 | 0.1-0.3 | 左侧磨底，无催化剂 |

**核心公式**: `最终仓位 = 总资产 × DNA上限 × Timing系数`

---

## Heptabase 集成

- **白板**: "未来资本" — 所有投资知识的中心
- **日志卡片**: `未来资本工作日志 YYYY-MM-DD`
- **双向同步**: CC 可读取白板内容，也可写回分析结果
- `/journal` 同时写入本地 + Heptabase Journal

---

## 目录结构

```
~/CC workspace/Finance/
├── src/                        # 源代码
│   ├── data/                   # 数据管道模块
│   └── indicators/             # 技术指标引擎
├── scripts/                    # 运维脚本
├── config/                     # 配置
├── data/                       # 数据文件
├── reports/                    # Research Desk
├── knowledge/                  # Knowledge Base
├── trading/                    # Trading Desk
├── risk/                       # Risk Desk
├── portfolio/                  # Portfolio Desk
├── docs/issues/                # 错题本
└── sync_to_cloud.sh            # 云端同步脚本
```

---

## 建设路线图

- [x] **Phase 1**: 物理合并 Valuation → Finance，建立 Desk 骨架
- [ ] **Phase 2**: 风控 + 交易纪律基建（IPS、止损规则、交易日志模板）
- [ ] **Phase 3**: 自动化增强（Greeks 监控、P&L 归因、Telegram 告警）
- [ ] **Phase 4**: AI 研究助手（财报分析、SEC RAG、新闻过滤）
- [ ] **Phase 5**: 进阶系统（regime 检测、业绩归因、评级系统代码化）

---

## 已知陷阱

详见 `docs/issues/`：
- `.bashrc` 非交互 shell 不加载环境变量 → 用 `.env` 文件
- `.gitignore` 的 `data/` 会匹配 `src/data/` → 用 `/data/` 只匹配根目录
- FMP Screener API 只返回 ~976 只（非 3000+），不影响 Top 200 质量

## 注意事项

- 投资建议仅供参考，最终决策由用户做出
- 金融数据有时效性，注明数据获取时间
- 期权策略要明确标注风险敞口
- API 调用串行执行，间隔 2 秒防限流
