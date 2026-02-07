"""
投资哲学透镜 — 基础模型和工具函数
"""
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class InvestmentLens:
    """单个投资哲学透镜"""
    name: str                    # 英文名称
    philosophy: str              # 哲学描述
    core_metric: str             # 核心指标
    horizon: str                 # 投资期限
    persona: str                 # AI 角色描述
    key_questions: List[str]     # 必须回答的核心问题
    analysis_framework: str      # 分析框架描述
    prompt_template: str         # AI 分析的 prompt 模板
    tags: List[str] = field(default_factory=list)


def format_prompt(lens: InvestmentLens, ticker: str, context: Dict = None) -> str:
    """
    填充 prompt 模板

    Args:
        lens: 投资哲学透镜
        ticker: 股票代码
        context: 可选上下文 (财务数据、新闻等)

    Returns:
        填充后的 prompt 字符串
    """
    ctx_block = ""
    if context:
        ctx_parts = []
        for key, value in context.items():
            ctx_parts.append(f"### {key}\n{value}")
        ctx_block = "\n\n".join(ctx_parts)

    questions_block = "\n".join(f"  {i+1}. {q}" for i, q in enumerate(lens.key_questions))

    return lens.prompt_template.format(
        ticker=ticker,
        lens_name=lens.name,
        philosophy=lens.philosophy,
        core_metric=lens.core_metric,
        horizon=lens.horizon,
        persona=lens.persona,
        key_questions=questions_block,
        analysis_framework=lens.analysis_framework,
        context=ctx_block,
    )


def get_all_lenses() -> List[InvestmentLens]:
    """返回全部 6 个投资哲学透镜"""
    from knowledge.philosophies.quality_compounder import get_lens as qc
    from knowledge.philosophies.imaginative_growth import get_lens as ig
    from knowledge.philosophies.fundamental_ls import get_lens as fls
    from knowledge.philosophies.deep_value import get_lens as dv
    from knowledge.philosophies.event_driven import get_lens as ed
    from knowledge.philosophies.macro_tactical import get_lens as mt

    return [qc(), ig(), fls(), dv(), ed(), mt()]
