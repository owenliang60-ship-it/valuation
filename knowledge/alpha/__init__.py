"""
Alpha Layer — Layer 2 求导层 (Second-Order Thinking)

消费 Layer 1 的完整输出，通过霍华德·马克斯/索罗斯的视角进行二阶思考。
回答"市场的预期在哪里错了？什么 risk 值得 take？"

3 sequential prompts:
  A. Red Team Gauntlet — 纯粹对抗性论点摧毁
  B. Cycle & Pendulum — 情绪/商业/技术周期 + 逆向信号
  C. Asymmetric Bet — 构建可执行的交易结构 (最重要)
"""
from knowledge.alpha.base import AlphaLens, AlphaPackage
from knowledge.alpha.red_team import generate_red_team_prompt
from knowledge.alpha.cycle_pendulum import generate_cycle_prompt
from knowledge.alpha.asymmetric_bet import generate_bet_prompt
