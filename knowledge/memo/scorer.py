"""
备忘录质量评分引擎 — 5 维度评分体系

维度权重: Thesis Clarity 25%, Evidence Quality 25%,
Valuation Rigor 20%, Risk Framework 15%, Decision Readiness 15%
目标分数: > 7.0/10
"""
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from knowledge.memo.template import MEMO_SECTIONS


# 评分体系
SCORING_RUBRIC = {
    "thesis_clarity": {
        "weight": 0.25,
        "description": "Falsifiable thesis, explicit key forces, variant view",
        "criteria": {
            "9-10": "Thesis is razor-sharp, falsifiable, with 3+ clear forces and a compelling variant view",
            "7-8": "Thesis is clear and falsifiable with identified forces, variant view present",
            "5-6": "Thesis exists but is vague or not easily falsifiable, forces unclear",
            "3-4": "Thesis is generic, no variant view, forces missing",
            "1-2": "No clear thesis statement",
        },
    },
    "evidence_quality": {
        "weight": 0.25,
        "description": "3+ primary sources, 8-10+ total, fact-checked",
        "criteria": {
            "9-10": "10+ sources, 4+ primary, all fact-checked, evidence directly supports thesis",
            "7-8": "8+ sources, 3+ primary, well-organized evidence chain",
            "5-6": "5-7 sources, some primary, gaps in evidence chain",
            "3-4": "Few sources, no primary, mostly secondary/opinion",
            "1-2": "No evidence cited or all from single source",
        },
    },
    "valuation_rigor": {
        "weight": 0.20,
        "description": "Multiple methods, sensitivity tables, IRR calc",
        "criteria": {
            "9-10": "3+ valuation methods, detailed sensitivity, clear IRR calc, assumptions explicit",
            "7-8": "2+ methods, some sensitivity analysis, IRR stated",
            "5-6": "Single valuation method, limited sensitivity",
            "3-4": "Vague valuation, no sensitivity, no IRR",
            "1-2": "No valuation work",
        },
    },
    "risk_framework": {
        "weight": 0.15,
        "description": "Kill conditions, position sizing rationale, downside scenarios",
        "criteria": {
            "9-10": "3+ observable kill conditions, detailed downside scenarios, sizing tied to OPRMS",
            "7-8": "2+ kill conditions, downside modeled, sizing justified",
            "5-6": "Some risk factors listed but not as kill conditions, limited downside analysis",
            "3-4": "Generic risk section, no kill conditions",
            "1-2": "No risk analysis",
        },
    },
    "decision_readiness": {
        "weight": 0.15,
        "description": "Action price, entry/exit rules, observable milestones",
        "criteria": {
            "9-10": "Clear action price, specific entry/exit rules, 3+ observable milestones with dates",
            "7-8": "Action price stated, entry/exit rules present, some milestones",
            "5-6": "Vague price target, no clear entry/exit rules",
            "3-4": "No actionable conclusion",
            "1-2": "Memo ends without recommendation",
        },
    },
}

# 禁止的对冲词 (在观点表达中)
HEDGE_WORDS = [
    "might", "could potentially", "perhaps", "arguably", "it seems",
    "it appears", "it is possible that", "one could argue", "it may be",
    "it is worth noting", "interestingly", "it should be noted",
]


@dataclass
class ScoreCard:
    """备忘录评分结果"""
    dimension_scores: Dict[str, float]  # {dimension_id: score 1-10}
    dimension_feedback: Dict[str, str]  # {dimension_id: feedback text}
    weighted_total: float = 0.0
    pass_fail: str = ""  # PASS (>= 7.0) or NEEDS_REVISION (< 7.0)

    def __post_init__(self):
        total = 0.0
        for dim_id, score in self.dimension_scores.items():
            weight = SCORING_RUBRIC[dim_id]["weight"]
            total += score * weight
        self.weighted_total = round(total, 2)
        self.pass_fail = "PASS" if self.weighted_total >= 7.0 else "NEEDS_REVISION"

    def to_dict(self) -> dict:
        return {
            "weighted_total": self.weighted_total,
            "pass_fail": self.pass_fail,
            "dimensions": {
                dim_id: {
                    "score": self.dimension_scores[dim_id],
                    "weight": SCORING_RUBRIC[dim_id]["weight"],
                    "weighted": round(self.dimension_scores[dim_id] * SCORING_RUBRIC[dim_id]["weight"], 2),
                    "feedback": self.dimension_feedback.get(dim_id, ""),
                }
                for dim_id in self.dimension_scores
            },
        }


def check_completeness(memo_text: str) -> Dict[str, bool]:
    """
    检查备忘录是否包含所有必需章节

    Args:
        memo_text: 备忘录 markdown 文本

    Returns:
        {section_id: True/False}
    """
    results = {}
    text_lower = memo_text.lower()

    section_markers = {
        "executive_summary": ["executive summary"],
        "variant_view": ["variant view"],
        "thesis": ["investment thesis", "thesis"],
        "evidence": ["evidence base", "evidence"],
        "valuation": ["valuation"],
        "tensions": ["key analytical tensions", "tensions", "tension 1"],
        "risk_framework": ["risk framework", "kill conditions"],
        "action_plan": ["action plan", "entry rules", "exit rules"],
    }

    for section_id, markers in section_markers.items():
        results[section_id] = any(marker in text_lower for marker in markers)

    return results


def check_writing_standards(memo_text: str) -> Dict:
    """
    检查写作标准

    Returns:
        {
            "char_count": int,
            "char_count_ok": bool (12000-20000),
            "hedge_words_found": list,
            "hedge_count": int,
        }
    """
    char_count = len(memo_text)

    found_hedges = []
    text_lower = memo_text.lower()
    for hedge in HEDGE_WORDS:
        count = text_lower.count(hedge)
        if count > 0:
            found_hedges.append({"word": hedge, "count": count})

    return {
        "char_count": char_count,
        "char_count_ok": 12_000 <= char_count <= 20_000,
        "hedge_words_found": found_hedges,
        "hedge_count": sum(h["count"] for h in found_hedges),
    }


def print_rubric() -> None:
    """打印评分体系"""
    print("\n投资备忘录评分体系 (目标: > 7.0/10)")
    print("=" * 65)
    for dim_id, dim in SCORING_RUBRIC.items():
        pct = int(dim["weight"] * 100)
        print(f"\n{dim_id} ({pct}%): {dim['description']}")
        for range_str, criteria in dim["criteria"].items():
            print(f"  {range_str}: {criteria}")
    print("\n" + "=" * 65)
