"""
OPRMS 数据模型

DNARating (资产基因) + TimingRating (时机系数) → PositionSize (仓位)
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Tuple


class DNARating(Enum):
    """
    资产基因评级 (Y 轴)

    决定单只股票的仓位上限。
    """
    S = "S"  # 圣杯: 改变人类进程的超级核心资产
    A = "A"  # 猛将: 强周期龙头，细分赛道霸主
    B = "B"  # 黑马: 强叙事驱动，赔率高但不确定
    C = "C"  # 跟班: 补涨逻辑，基本不做

    @property
    def max_position_pct(self) -> float:
        """仓位上限百分比 (占总资产)"""
        return {
            DNARating.S: 0.25,
            DNARating.A: 0.15,
            DNARating.B: 0.07,
            DNARating.C: 0.02,
        }[self]

    @property
    def label(self) -> str:
        return {
            DNARating.S: "圣杯",
            DNARating.A: "猛将",
            DNARating.B: "黑马",
            DNARating.C: "跟班",
        }[self]


class TimingRating(Enum):
    """
    时机系数评级 (X 轴)

    决定当前时点应该用多少比例的 DNA 上限。
    """
    S = "S"  # 千载难逢: 历史性时刻，暴跌坑底/突破
    A = "A"  # 趋势确立: 主升浪确认，右侧突破
    B = "B"  # 正常波动: 回调支撑，震荡
    C = "C"  # 垃圾时间: 左侧磨底，无催化剂

    @property
    def coefficient_range(self) -> Tuple[float, float]:
        """时机系数范围 (min, max)"""
        return {
            TimingRating.S: (1.0, 1.5),
            TimingRating.A: (0.8, 1.0),
            TimingRating.B: (0.4, 0.6),
            TimingRating.C: (0.1, 0.3),
        }[self]

    @property
    def midpoint(self) -> float:
        """系数范围中点"""
        lo, hi = self.coefficient_range
        return (lo + hi) / 2

    @property
    def label(self) -> str:
        return {
            TimingRating.S: "千载难逢",
            TimingRating.A: "趋势确立",
            TimingRating.B: "正常波动",
            TimingRating.C: "垃圾时间",
        }[self]


@dataclass
class OPRMSRating:
    """单只股票的 OPRMS 评级"""
    symbol: str
    dna: DNARating
    timing: TimingRating
    timing_coeff: float  # 精确系数 (在 timing.coefficient_range 内)
    evidence: List[str] = field(default_factory=list)
    investment_bucket: str = ""  # Long-term Compounder / Catalyst-Driven Long / Short / Secular Short
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "dna": self.dna.value,
            "timing": self.timing.value,
            "timing_coeff": self.timing_coeff,
            "evidence": self.evidence,
            "investment_bucket": self.investment_bucket,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "OPRMSRating":
        return cls(
            symbol=d["symbol"],
            dna=DNARating(d["dna"]),
            timing=TimingRating(d["timing"]),
            timing_coeff=d["timing_coeff"],
            evidence=d.get("evidence", []),
            investment_bucket=d.get("investment_bucket", ""),
            updated_at=d.get("updated_at", ""),
        )


@dataclass
class PositionSize:
    """仓位计算结果"""
    symbol: str
    total_capital: float
    dna: DNARating
    dna_cap_pct: float        # DNA 仓位上限 %
    timing: TimingRating
    timing_coeff: float       # 精确时机系数
    target_position_pct: float  # 最终仓位 % = dna_cap * timing_coeff
    target_position_usd: float  # 最终仓位金额

    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "total_capital": self.total_capital,
            "dna": self.dna.value,
            "dna_cap_pct": round(self.dna_cap_pct * 100, 2),
            "timing": self.timing.value,
            "timing_coeff": self.timing_coeff,
            "target_position_pct": round(self.target_position_pct * 100, 2),
            "target_position_usd": round(self.target_position_usd, 2),
        }
