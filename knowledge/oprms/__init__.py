"""
OPRMS 评级系统 — DNA + Timing → 仓位计算

核心公式: 最终仓位 = 总资产 x DNA上限 x Timing系数
"""
from knowledge.oprms.models import DNARating, TimingRating, OPRMSRating, PositionSize
from knowledge.oprms.ratings import calculate_position_size, generate_sensitivity_table
