from dataclasses import dataclass

@dataclass(frozen=True)
class BudgetConfig:
    monthly_cap_usd: float = 100.0
    baseline_daily_usd: float = 5.0

@dataclass(frozen=True)
class TriggerConfig:
    discard_below: float = 0.60
    research_at: float = 0.68
    premium_at: float = 0.74
    critic_at: float = 0.80
    rollover_research_at: float = 0.75
    rollover_premium_at: float = 0.80
    rollover_critic_at: float = 0.85

BUDGET = BudgetConfig()
TRIGGERS = TriggerConfig()
