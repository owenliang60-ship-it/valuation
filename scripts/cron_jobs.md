# 定时任务配置

> 美股数据更新定时任务配置

## 数据更新策略

| 数据类型 | 更新频率 | 时间 (北京) | 说明 |
|----------|----------|-------------|------|
| 量价数据 | 日频 | 周二-六 06:30 | 美股收盘后更新 |
| 股票池 | 周频 | 周六 08:00 | 检查市值变化，更新进出名单 |
| 基本面数据 | 周频 | 周六 10:00 | profiles/ratios/income/balance_sheet/cash_flow |
| 数据库重建 | 周频 | 周六 12:00 | 重建 SQLite 数据库，计算 TTM |

### 基本面数据说明

基本面数据实际只在季度财报发布时变化（1/4/7/10月中下旬），但由于财报日历 API 无权限，
采用周度更新策略，简单可靠，少量冗余调用不影响使用。

---

## 时间设置说明

### 美股交易时间

| 项目 | 美东时间 (ET) | 北京时间 |
|------|---------------|----------|
| 盘前交易 | 04:00-09:30 | 17:00-22:30 (夏令时) / 18:00-23:30 (冬令时) |
| 正常交易 | 09:30-16:00 | 22:30-05:00 (夏令时) / 23:30-06:00 (冬令时) |
| 盘后交易 | 16:00-20:00 | 05:00-09:00 (夏令时) / 06:00-10:00 (冬令时) |

### 数据更新延迟

FMP API 数据更新通常有 15-60 分钟延迟，建议在收盘后 1-2 小时再更新。

---

## 推荐 Cron 配置

### 1. 日频量价更新 (每个交易日)

```bash
# 美股收盘后更新量价数据
# 北京时间 06:30 (美东时间约 17:30，考虑冬令时)
# 周二到周六执行 (对应美东周一到周五)
30 6 * * 2-6 cd /path/to/Valuation && /path/to/python scripts/update_data.py --price >> logs/cron_price.log 2>&1
```

### 2. 周频股票池刷新

```bash
# 每周六刷新股票池 (在基本面更新之前)
# 北京时间 08:00
0 8 * * 6 cd /path/to/Valuation && /path/to/python scripts/update_data.py --pool >> logs/cron_pool.log 2>&1
```

### 3. 周频基本面更新

```bash
# 每周六更新所有基本面数据
# 北京时间 10:00
# 包含: profiles, ratios, income, balance_sheet, cash_flow
0 10 * * 6 cd /path/to/Valuation && /path/to/python scripts/update_data.py --fundamental >> logs/cron_fundamental.log 2>&1
```

### 4. 周频数据库重建

```bash
# 每周六重建数据库，整合最新数据，计算 TTM
# 北京时间 12:00 (基本面更新完成后)
0 12 * * 6 cd /path/to/Valuation && /path/to/python scripts/init_database.py >> logs/cron_database.log 2>&1
```

### 5. 日频指标扫描 (可选)

```bash
# 量价数据更新后扫描指标
# 北京时间 07:00 (数据更新后 30 分钟)
0 7 * * 2-6 cd /path/to/Valuation && /path/to/python scripts/scan_indicators.py --save >> logs/cron_scan.log 2>&1
```

---

## 一键配置脚本

将以下内容保存为 `setup_cron.sh`:

```bash
#!/bin/bash

# 项目路径 (请修改为实际路径)
PROJECT_DIR="/Users/owen/CC workspace/Valuation"
PYTHON_PATH="$PROJECT_DIR/.venv/bin/python"

# 创建日志目录
mkdir -p "$PROJECT_DIR/logs"

# 写入 crontab
(crontab -l 2>/dev/null | grep -v "Valuation"; cat << EOF
# === Valuation Agent 定时任务 ===
# 日频量价更新 (周二-周六 06:30)
30 6 * * 2-6 cd "$PROJECT_DIR" && "$PYTHON_PATH" scripts/update_data.py --price >> logs/cron_price.log 2>&1
# 周频股票池刷新 (周六 08:00)
0 8 * * 6 cd "$PROJECT_DIR" && "$PYTHON_PATH" scripts/update_data.py --pool >> logs/cron_pool.log 2>&1
# 周频基本面更新 (周六 10:00)
0 10 * * 6 cd "$PROJECT_DIR" && "$PYTHON_PATH" scripts/update_data.py --fundamental >> logs/cron_fundamental.log 2>&1
# 周频数据库重建 (周六 12:00)
0 12 * * 6 cd "$PROJECT_DIR" && "$PYTHON_PATH" scripts/init_database.py >> logs/cron_database.log 2>&1
EOF
) | crontab -

echo "Cron jobs configured successfully!"
crontab -l | grep Valuation
```

---

## 任务串行执行原则

遵循 quant-development skill 规范:

1. **统一入口**: 所有任务通过 `scripts/update_data.py` 执行
2. **串行执行**: 避免并行调用 API，防止限流
3. **时间间隔**: 周末任务之间间隔 2 小时
4. **日志记录**: 每个任务独立日志文件

---

## 手动执行命令

```bash
# 进入项目目录
cd "/Users/owen/CC workspace/Valuation"

# 激活虚拟环境
source .venv/bin/activate

# === 日常更新 ===
# 更新量价数据 (每日)
python scripts/update_data.py --price

# === 周度更新 ===
# 刷新股票池
python scripts/update_data.py --pool

# 更新基本面数据 (包含 5 张表)
python scripts/update_data.py --fundamental

# 重建数据库 (整合数据，计算 TTM)
python scripts/init_database.py

# === 全量更新 ===
python scripts/update_data.py --all && python scripts/init_database.py

# === 数据验证 ===
python -c "from src.data.data_validator import print_data_report; print_data_report()"
```

---

## 监控建议

1. **日志检查**: 定期检查 `logs/` 下的日志文件
2. **数据验证**: 每周运行 `data_validator.py` 检查数据质量
3. **API 用量**: 监控 FMP API 调用次数，避免超限

---

## 节假日处理

美股休市日:
- 元旦 (1/1)
- 马丁·路德·金纪念日 (1月第三个周一)
- 总统日 (2月第三个周一)
- 耶稣受难日 (复活节前周五)
- 阵亡将士纪念日 (5月最后一个周一)
- 独立日 (7/4)
- 劳动节 (9月第一个周一)
- 感恩节 (11月第四个周四)
- 圣诞节 (12/25)

休市日无需更新数据，当前配置不会自动跳过休市日，但这不会造成问题（只是获取到与前一日相同的数据）。
