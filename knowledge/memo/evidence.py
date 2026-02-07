"""
证据层级和验证规则

Primary sources (3+ required): direct voice, stakeholder signals, behavioral data
Total sources: 8-10+
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List


class EvidenceLevel(Enum):
    """证据层级"""
    PRIMARY = "primary"      # 直接来源: CEO 采访、财报电话会、客户反馈
    SECONDARY = "secondary"  # 二手来源: 分析师报告、行业研究
    TERTIARY = "tertiary"    # 三手来源: 新闻摘要、社交媒体、AI 生成


# 主要证据来源类型
PRIMARY_SOURCE_TYPES = {
    "direct_voice": {
        "description": "CEO interviews, earnings calls, conference presentations, shareholder letters",
        "examples": [
            "Q4 2025 earnings call transcript",
            "CEO interview at Goldman Sachs TMT conference",
            "Annual shareholder letter 2025",
        ],
    },
    "stakeholder_signals": {
        "description": "Glassdoor reviews, customer feedback, supplier commentary, channel checks",
        "examples": [
            "Glassdoor employee sentiment trend (6-month)",
            "G2/Trustpilot customer review analysis",
            "Supply chain channel check via industry contacts",
        ],
    },
    "behavioral_data": {
        "description": "Patent filings, job postings, insider trading activity, CAPEX patterns",
        "examples": [
            "USPTO patent filings in AI/ML (trailing 12 months)",
            "LinkedIn job posting trends by department",
            "SEC Form 4 insider purchases > $1M",
        ],
    },
}


@dataclass
class EvidenceItem:
    """单条证据"""
    source: str          # 来源描述
    level: EvidenceLevel
    source_type: str     # direct_voice / stakeholder_signals / behavioral_data / analyst / ...
    date: str            # 证据日期
    content: str         # 关键内容摘要
    url: str = ""        # 可选链接
    verified: bool = False


def validate_evidence_requirements(sources: List[EvidenceItem]) -> Dict:
    """
    验证证据是否满足要求

    Requirements:
    - 3+ primary sources
    - 8-10+ total sources

    Returns:
        {
            "total_count": int,
            "primary_count": int,
            "total_ok": bool,
            "primary_ok": bool,
            "passed": bool,
            "issues": list of strings,
        }
    """
    primary_count = sum(1 for s in sources if s.level == EvidenceLevel.PRIMARY)
    total_count = len(sources)

    issues = []
    if primary_count < 3:
        issues.append(f"Need 3+ primary sources, have {primary_count}")
    if total_count < 8:
        issues.append(f"Need 8+ total sources, have {total_count}")

    return {
        "total_count": total_count,
        "primary_count": primary_count,
        "total_ok": total_count >= 8,
        "primary_ok": primary_count >= 3,
        "passed": primary_count >= 3 and total_count >= 8,
        "issues": issues,
    }


def format_evidence_chain(sources: List[EvidenceItem]) -> str:
    """
    格式化证据链为 markdown

    Args:
        sources: 证据列表

    Returns:
        格式化的 markdown 字符串
    """
    lines = ["## Evidence Chain", ""]

    # Group by level
    by_level = {}
    for s in sources:
        by_level.setdefault(s.level, []).append(s)

    level_order = [EvidenceLevel.PRIMARY, EvidenceLevel.SECONDARY, EvidenceLevel.TERTIARY]
    level_labels = {
        EvidenceLevel.PRIMARY: "Primary Sources (direct)",
        EvidenceLevel.SECONDARY: "Secondary Sources (analyst/research)",
        EvidenceLevel.TERTIARY: "Tertiary Sources (news/commentary)",
    }

    for level in level_order:
        items = by_level.get(level, [])
        if not items:
            continue

        lines.append(f"### {level_labels[level]}")
        for i, item in enumerate(items, 1):
            verified = " [verified]" if item.verified else ""
            lines.append(f"{i}. **{item.source}** ({item.date}){verified}")
            lines.append(f"   {item.content}")
            if item.url:
                lines.append(f"   Source: {item.url}")
            lines.append("")

    # Summary
    validation = validate_evidence_requirements(sources)
    status = "PASS" if validation["passed"] else "NEEDS MORE"
    lines.append(f"**Evidence Status**: {status} "
                 f"({validation['primary_count']} primary, "
                 f"{validation['total_count']} total)")
    if validation["issues"]:
        for issue in validation["issues"]:
            lines.append(f"- WARNING: {issue}")

    return "\n".join(lines)
