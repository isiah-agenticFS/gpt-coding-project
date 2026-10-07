from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from .config import TRIGGERS
from .cost_budget import BudgetSnapshot

class AgentTier(str, Enum):
    LOCAL_ONLY = "local_only"
    RESEARCH = "research"
    PREMIUM = "premium"
    CRITIC = "critic"

@dataclass(frozen=True)
class TriggerDecision:
    allowed_tier: AgentTier
    reason: str
    using_rollover: bool

def decide_agent_tier(*, confidence: float, estimated_call_cost_usd: float, budget: BudgetSnapshot) -> TriggerDecision:
    if not 0.0 <= confidence <= 1.0:
        raise ValueError("confidence must be between 0 and 1")
    if estimated_call_cost_usd < 0:
        raise ValueError("estimated_call_cost_usd cannot be negative")
    if confidence < TRIGGERS.discard_below:
        return TriggerDecision(AgentTier.LOCAL_ONLY, "Candidate is below the minimum quant threshold.", False)
    if estimated_call_cost_usd > budget.max_available_today_usd:
        return TriggerDecision(AgentTier.LOCAL_ONLY, "Paid call would exceed available earned API budget.", False)

    using_rollover = estimated_call_cost_usd > budget.normal_remaining_today_usd
    if using_rollover:
        if confidence >= TRIGGERS.rollover_critic_at:
            return TriggerDecision(AgentTier.CRITIC, "Rollover critic threshold met.", True)
        if confidence >= TRIGGERS.rollover_premium_at:
            return TriggerDecision(AgentTier.PREMIUM, "Rollover premium threshold met.", True)
        if confidence >= TRIGGERS.rollover_research_at:
            return TriggerDecision(AgentTier.RESEARCH, "Rollover research threshold met.", True)
        return TriggerDecision(AgentTier.LOCAL_ONLY, "Candidate is not strong enough to consume rollover budget.", True)

    if confidence >= TRIGGERS.critic_at:
        return TriggerDecision(AgentTier.CRITIC, "Critic threshold met.", False)
    if confidence >= TRIGGERS.premium_at:
        return TriggerDecision(AgentTier.PREMIUM, "Premium threshold met.", False)
    if confidence >= TRIGGERS.research_at:
        return TriggerDecision(AgentTier.RESEARCH, "Research threshold met.", False)
    return TriggerDecision(AgentTier.LOCAL_ONLY, "Candidate remains in local monitoring.", False)
