# Dexter 架构分析与 Finance 工作区借鉴

## 一、Dexter 核心设计模式

### 1.1 Agent 执行引擎

**迭代式循环架构**：
```typescript
// 伪代码示意
while (iteration < MAX_ITERATIONS) {
  response = llm.call(prompt + scratchpad)

  if (response.has_tool_calls) {
    for (tool_call in response.tool_calls) {
      if (!hasExecutedSkill(tool_call)) {
        result = executeTool(tool_call)
        scratchpad.append(result)
        markAsExecuted(tool_call)
      }
    }
  } else {
    // 生成最终答案
    return formatAnswer(scratchpad)
  }
}
```

**关键特性**：
- **去重机制**：每个skill在单次查询中仅执行一次，避免重复调用
- **上下文管理**：token超限时自动清除最早的工具结果，保留最近 N 个
- **软限制**：工具调用超限时 yield 警告而非强制阻止，引导 LLM 自主决策
- **流式事件**：实时 yield 工具事件（start/progress/end/error）

### 1.2 工具注册系统

**三层抽象架构**：

```typescript
interface RegisteredTool {
  name: string;           // 工具名称
  tool: StructuredTool;   // 工具实例
  systemPrompt: string;   // 给 LLM 的使用说明
}

// 1. 注册层：完整工具对象
getToolRegistry() → RegisteredTool[]

// 2. 工具层：纯实例供 LLM 绑定
getTools() → StructuredTool[]

// 3. 描述层：系统提示格式化
buildToolDescriptions() → string
```

**条件加载机制**：
- 基础工具固定注册（财务搜索、浏览器）
- 可选工具根据环境变量动态加载（Exa → Tavily 降级）
- 技能工具按需发现和加载

### 1.3 Scratchpad 追踪系统

**JSONL 格式日志**：
```
.dexter/scratchpad/YYYY-MM-DD-HHMMSS_hashid.jsonl
```

**记录内容**：
- 初始查询
- 工具调用参数和原始结果
- LLM 总结的可读性结果
- 推理步骤

**价值**：
- 完整追踪数据获取和解释过程
- 支持回放和调试
- 可用于评估和改进

### 1.4 评估系统

**LLM-as-Judge 方法**：
- LangSmith 集成追踪实验
- 自动评分答案正确性
- 支持全量/采样评估
- 实时显示进度和准确率

---

## 二、对 Finance 工作区的关键启发

### 2.1 当前架构对比

| 维度 | Dexter | Finance (现状) | 启发 |
|------|--------|----------------|------|
| **执行模式** | Agent 自主循环 | Pipeline 单向流 | 引入迭代验证机制 |
| **工具管理** | 注册表 + 条件加载 | 硬编码数据源 | 工具抽象层 |
| **追踪系统** | JSONL scratchpad | 无 | 分析追踪日志 |
| **评估** | LLM-as-Judge | 人工 review | 自动评分系统 |
| **上下文管理** | 智能截断 | 固定深度参数 | 动态 token 管理 |

### 2.2 借鉴方向一：Agent 模式升级

**现状问题**：
- `pipeline.py` 是单向流水线：数据 → 6 lens → debate → memo → score
- 无法处理"数据不足需要追加查询"的场景
- Claude 无法主动决定需要什么数据

**Dexter 启发**：
```python
# 当前：pipeline.py
def analyze_ticker(symbol, depth):
    data = fetch_all_data(symbol)  # 一次性加载
    results = []
    for lens in LENSES:
        results.append(llm.call(lens_prompt + data))
    return combine(results)

# 改进：agent-based
def analyze_ticker(symbol, depth):
    tools = [
        FetchPriceTool(),
        FetchFundamentalTool(),
        FetchNewsTool(),
        FetchEstimatesTool(),
        SearchSECTool(),
    ]

    agent = ResearchAgent(tools=tools, max_iterations=10)
    return agent.run(f"分析 {symbol} 的投资价值")

    # Agent 自主决定：
    # 1. 先看 price + fundamental
    # 2. 发现估值偏高 → 调用 estimates 看未来预期
    # 3. 仍不确定 → 搜索 SEC 最新财报
```

**优势**：
- **数据按需加载**：只调用必要的 API，节省配额和时间
- **动态深度调整**：简单情况 3 步结束，复杂情况自动深挖
- **自我验证**：Agent 可以"检查自己的工作"，发现逻辑漏洞后补充分析

### 2.3 借鉴方向二：工具注册系统

**现状问题**：
- 数据源硬编码在各个模块（`src/data/fmp_client.py`）
- 新增数据源需要修改多个文件
- 无法根据可用性动态选择数据源

**Dexter 启发**：
```python
# terminal/tools/registry.py
from typing import Protocol, Optional

class FinanceTool(Protocol):
    """所有金融工具的通用接口"""
    name: str
    description: str  # 给 Claude 的使用说明

    def execute(self, **kwargs) -> dict:
        ...

class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, FinanceTool] = {}

    def register(self, tool: FinanceTool):
        self._tools[tool.name] = tool

    def get_tools(self) -> list[FinanceTool]:
        return list(self._tools.values())

    def get_descriptions(self) -> str:
        """生成给 Claude 的工具说明"""
        return "\n\n".join([
            f"# {tool.name}\n{tool.description}"
            for tool in self._tools.values()
        ])

# 使用示例
registry = ToolRegistry()

# 基础工具
registry.register(FMPPriceTool())
registry.register(FMPFundamentalTool())

# 条件加载
if os.getenv("TRADIER_API_KEY"):
    registry.register(TradierOptionsTool())
if os.getenv("FRED_API_KEY"):
    registry.register(FREDMacroTool())

# Agent 使用
tools = registry.get_tools()
tool_docs = registry.get_descriptions()
```

**优势**：
- **易扩展**：新增数据源只需实现 `FinanceTool` 接口
- **条件加载**：根据 API key 可用性自动启用/禁用工具
- **统一文档**：工具说明集中管理，自动生成给 Claude 的 system prompt

### 2.4 借鉴方向三：Scratchpad 追踪系统

**现状问题**：
- 分析过程不透明，无法回放
- 调试困难，不知道哪个环节出错
- 无法评估"Claude 用了哪些数据做出结论"

**Dexter 启发**：
```python
# terminal/scratchpad.py
from datetime import datetime
from pathlib import Path
import json
import hashlib

class AnalysisScratchpad:
    def __init__(self, symbol: str, query: str):
        self.symbol = symbol
        self.query = query
        self.hash = hashlib.md5(query.encode()).hexdigest()[:8]
        self.timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")

        self.log_path = Path(
            f"data/companies/{symbol}/scratchpad/"
            f"{self.timestamp}_{self.hash}.jsonl"
        )
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

        # 记录初始查询
        self._append({
            "type": "query",
            "timestamp": self.timestamp,
            "symbol": symbol,
            "query": query,
        })

    def log_tool_call(self, tool_name: str, args: dict, result: dict):
        """记录工具调用"""
        self._append({
            "type": "tool_call",
            "timestamp": datetime.now().isoformat(),
            "tool": tool_name,
            "args": args,
            "result": result,
        })

    def log_reasoning(self, step: str, content: str):
        """记录推理步骤"""
        self._append({
            "type": "reasoning",
            "timestamp": datetime.now().isoformat(),
            "step": step,
            "content": content,
        })

    def _append(self, entry: dict):
        with open(self.log_path, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

# 使用示例
scratchpad = AnalysisScratchpad("NVDA", "分析投资价值")

# 工具调用
result = fmp.get_income_statement("NVDA")
scratchpad.log_tool_call("FMPFundamental", {"symbol": "NVDA"}, result)

# 推理步骤
scratchpad.log_reasoning(
    "valuation_check",
    "PE 60x 高于历史均值 45x，但 PEG 1.2 处于合理区间"
)
```

**优势**：
- **完整追踪**：每个分析的完整数据流
- **可回放**：复现任何历史分析
- **可评估**：检查 Claude 的推理质量
- **可调试**：快速定位问题环节

### 2.5 借鉴方向四：评估系统

**现状问题**：
- 分析质量依赖人工 review
- 无法量化"好的分析"标准
- 改进 prompt 无客观反馈

**Dexter 启发**：
```python
# terminal/evals/evaluator.py
from typing import Literal

class AnalysisEvaluator:
    def __init__(self, llm):
        self.llm = llm
        self.eval_prompt = """
你是一个严格的投资研究评审员。评估以下分析报告的质量。

评分标准：
1. 数据支撑 (0-10分)：结论是否有充分数据支持
2. 逻辑严密 (0-10分)：推理是否合理，有无明显漏洞
3. 风险意识 (0-10分)：是否识别主要风险
4. 可执行性 (0-10分)：建议是否具体可行

分析报告：
{report}

请给出评分和详细理由。JSON 格式：
{{
  "scores": {{"data": X, "logic": X, "risk": X, "actionable": X}},
  "total": X,
  "feedback": "..."
}}
"""

    def evaluate(self, report: str) -> dict:
        """评估单个报告"""
        response = self.llm.call(
            self.eval_prompt.format(report=report)
        )
        return json.loads(response)

    def batch_evaluate(
        self,
        reports: list[dict],
        sample_size: int | None = None
    ):
        """批量评估"""
        if sample_size:
            reports = random.sample(reports, sample_size)

        scores = []
        for report in reports:
            score = self.evaluate(report["content"])
            scores.append({
                "symbol": report["symbol"],
                "score": score,
            })

        # 统计
        avg_score = sum(s["score"]["total"] for s in scores) / len(scores)
        print(f"平均分: {avg_score:.1f}/40")

        return scores

# 使用示例
evaluator = AnalysisEvaluator(llm)

# 评估历史分析
reports = load_historical_reports()
results = evaluator.batch_evaluate(reports, sample_size=20)

# 追踪改进
# 修改 prompt → 重新分析 → 评估 → 对比分数变化
```

**优势**：
- **客观反馈**：量化分析质量
- **快速迭代**：A/B 测试不同 prompt
- **持续改进**：追踪评分趋势

---

## 三、具体实施建议

### 3.1 Phase 2b: 工具注册系统（1-2天）

**优先级**：P0（基础架构）

**任务**：
1. 创建 `terminal/tools/` 目录
2. 定义 `FinanceTool` 协议
3. 实现 `ToolRegistry` 类
4. 重构现有 FMP 客户端为工具
5. 集成到 `pipeline.py`

**验收标准**：
- [ ] 所有 FMP 端点包装为独立工具
- [ ] Registry 支持条件加载
- [ ] 自动生成工具文档字符串

### 3.2 Phase 2c: Scratchpad 追踪（1天）

**优先级**：P1（可观测性）

**任务**：
1. 创建 `terminal/scratchpad.py`
2. 修改 `pipeline.py` 记录所有工具调用
3. 在 `data/companies/{SYMBOL}/scratchpad/` 存储日志

**验收标准**：
- [ ] 每次分析生成 JSONL 日志
- [ ] 可回放任何历史分析
- [ ] Web UI 可视化 scratchpad

### 3.3 Phase 2d: Agent 模式（3-5天）

**优先级**：P2（增强能力）

**任务**：
1. 创建 `terminal/agent.py`
2. 实现迭代式执行引擎
3. 添加去重和上下文管理
4. 保留 pipeline 模式作为 fallback

**验收标准**：
- [ ] Agent 模式下 API 调用减少 30%+
- [ ] 复杂查询质量提升（人工评估）
- [ ] 支持 `--mode agent` 切换

### 3.4 Phase 3a: 评估系统（2-3天）

**优先级**：P2（质量保障）

**任务**：
1. 创建 `terminal/evals/` 目录
2. 实现 LLM-as-Judge 评估器
3. 建立黄金标准数据集（10-20 个案例）
4. 集成到 CI/CD

**验收标准**：
- [ ] 自动评分历史分析
- [ ] Prompt 改进可量化对比
- [ ] 每次部署前跑评估

---

## 四、风险和注意事项

### 4.1 不要过度工程化

**Dexter 的复杂度适合通用 agent**，Finance 有明确领域边界。

**原则**：
- 先实现工具注册（收益高，成本低）
- 再加 scratchpad（可观测性关键）
- Agent 模式谨慎引入（确认 pipeline 瓶颈后再做）

### 4.2 保持 Claude 主导地位

**Dexter 是完全自主 agent**，Finance 是 **Claude-assisted 系统**。

**区别**：
- Dexter: Agent 决定一切，人类只看结果
- Finance: Claude 是分析师，但用户做最终决策

**设计**：
- 保留人类介入点（OPRMS 评级、仓位建议）
- Agent 用于"数据收集和初步分析"，不用于"投资决策"

### 4.3 成本控制

**Agent 模式可能显著增加 API 调用**。

**措施**：
- 设置 `max_iterations` 上限（默认 5，复杂案例 10）
- 工具调用去重
- 缓存机制（相同查询 24h 内返回缓存）

---

## 五、总结

### 核心收获

1. **工具抽象**：注册表模式让数据源可插拔，易扩展
2. **可观测性**：Scratchpad 让"黑盒"变"玻璃盒"
3. **自主性**：Agent 模式让 Claude 按需获取数据，而非被动接收
4. **评估驱动**：LLM-as-Judge 让改进可量化

### 实施路线

```
Phase 2b: 工具注册系统 (P0, 1-2天)
    ↓
Phase 2c: Scratchpad 追踪 (P1, 1天)
    ↓
Phase 2d: Agent 模式 (P2, 3-5天)
    ↓
Phase 3a: 评估系统 (P2, 2-3天)
```

### Next Action

**立即可做**：
1. 创建 `terminal/tools/` 目录结构
2. 定义 `FinanceTool` 协议接口
3. 包装 1-2 个 FMP 端点测试可行性

**观望决策**：
- Agent 模式需要先跑几次 full depth 分析，确认 pipeline 的真实痛点
- 如果发现"数据不足导致结论薄弱"的情况多发，再引入 agent

---

*生成时间: 2026-02-08*
*基于: Dexter v2026.2.6*
