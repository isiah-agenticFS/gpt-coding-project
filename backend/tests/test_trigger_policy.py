from app.cost_budget import RollingApiBudget
from app.trigger_policy import AgentTier, decide_agent_tier

def test_normal_budget_allows_research():
    snapshot = RollingApiBudget().snapshot(1)
    decision = decide_agent_tier(confidence=0.70, estimated_call_cost_usd=0.10, budget=snapshot)
    assert decision.allowed_tier == AgentTier.RESEARCH
    assert decision.using_rollover is False

def test_rollover_requires_higher_confidence():
    budget = RollingApiBudget()
    budget.record_spend(1.0, 1)
    budget.record_spend(5.0, 2)
    snapshot = budget.snapshot(2)
    decision = decide_agent_tier(confidence=0.70, estimated_call_cost_usd=0.10, budget=snapshot)
    assert decision.allowed_tier == AgentTier.LOCAL_ONLY
    assert decision.using_rollover is True

def test_strong_candidate_can_consume_rollover():
    budget = RollingApiBudget()
    budget.record_spend(1.0, 1)
    budget.record_spend(5.0, 2)
    snapshot = budget.snapshot(2)
    decision = decide_agent_tier(confidence=0.86, estimated_call_cost_usd=0.10, budget=snapshot)
    assert decision.allowed_tier == AgentTier.CRITIC
    assert decision.using_rollover is True
