"""
Macro regime interface — stub until macro data pipeline is built (Phase 2a+).

Other modules can reference this now; it returns NEUTRAL by default.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class MarketRegime(str, Enum):
    """Market regime classification."""
    RISK_ON = "risk_on"           # Expansion, bullish, add risk
    NEUTRAL = "neutral"           # Normal conditions
    RISK_OFF = "risk_off"         # Contraction, defensive, reduce risk
    CRISIS = "crisis"             # Severe stress, capital preservation


@dataclass
class RegimeAssessment:
    """Current macro regime assessment."""
    regime: MarketRegime
    confidence: str = "low"       # low / medium / high
    rationale: str = ""
    data_sources: int = 0         # Number of data sources used
    assessed_at: str = ""

    def to_dict(self) -> dict:
        return {
            "regime": self.regime.value,
            "confidence": self.confidence,
            "rationale": self.rationale,
            "data_sources": self.data_sources,
            "assessed_at": self.assessed_at,
        }


def get_current_regime() -> RegimeAssessment:
    """
    Get current market regime assessment.

    STUB: Returns NEUTRAL until macro data pipeline is built.
    Future implementation will use:
    - Fed funds rate trajectory
    - Yield curve shape
    - VIX / credit spreads
    - Leading economic indicators
    """
    from datetime import datetime

    return RegimeAssessment(
        regime=MarketRegime.NEUTRAL,
        confidence="low",
        rationale=(
            "Stub implementation — no macro data pipeline yet. "
            "Defaulting to NEUTRAL. Build macro data ingestion "
            "(FRED API, VIX, yield curve) to activate regime detection."
        ),
        data_sources=0,
        assessed_at=datetime.now().isoformat(),
    )


def get_regime_adjustment(regime: MarketRegime) -> float:
    """
    Suggested position sizing multiplier based on regime.

    In risk-off or crisis, reduce position sizes.
    """
    return {
        MarketRegime.RISK_ON: 1.0,
        MarketRegime.NEUTRAL: 1.0,
        MarketRegime.RISK_OFF: 0.7,
        MarketRegime.CRISIS: 0.4,
    }[regime]
