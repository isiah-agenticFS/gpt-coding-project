from __future__ import annotations
from dataclasses import dataclass

_EPSILON = 1e-9

@dataclass(frozen=True)
class BudgetSnapshot:
    trading_day_index: int
    monthly_cap_usd: float
    monthly_spend_usd: float
    baseline_daily_usd: float
    earned_budget_usd: float
    bank_before_today_usd: float
    normal_remaining_today_usd: float
    rollover_available_today_usd: float
    max_available_today_usd: float
    remaining_monthly_budget_usd: float

class RollingApiBudget:
    def __init__(self, *, monthly_cap_usd: float = 100.0, baseline_daily_usd: float = 5.0) -> None:
        if monthly_cap_usd <= 0 or baseline_daily_usd <= 0:
            raise ValueError("budget values must be positive")
        self.monthly_cap_usd = float(monthly_cap_usd)
        self.baseline_daily_usd = float(baseline_daily_usd)
        self.monthly_spend_usd = 0.0
        self._daily_spend: dict[int, float] = {}

    def daily_spend(self, trading_day_index: int) -> float:
        self._validate_day(trading_day_index)
        return self._daily_spend.get(trading_day_index, 0.0)

    def earned_budget(self, trading_day_index: int) -> float:
        self._validate_day(trading_day_index)
        return min(self.monthly_cap_usd, trading_day_index * self.baseline_daily_usd)

    def snapshot(self, trading_day_index: int) -> BudgetSnapshot:
        self._validate_day(trading_day_index)
        today_spend = self.daily_spend(trading_day_index)
        spend_before_today = self.monthly_spend_usd - today_spend
        earned_before_today = min(self.monthly_cap_usd, max(0, trading_day_index - 1) * self.baseline_daily_usd)
        bank_before_today = max(0.0, earned_before_today - spend_before_today)
        normal_remaining = max(0.0, self.baseline_daily_usd - today_spend)
        earned_to_date = self.earned_budget(trading_day_index)
        earned_remaining = max(0.0, earned_to_date - self.monthly_spend_usd)
        month_remaining = max(0.0, self.monthly_cap_usd - self.monthly_spend_usd)
        max_available = min(earned_remaining, month_remaining)
        rollover_available = max(0.0, max_available - normal_remaining)
        return BudgetSnapshot(
            trading_day_index, self.monthly_cap_usd, self.monthly_spend_usd,
            self.baseline_daily_usd, earned_to_date, bank_before_today,
            min(normal_remaining, max_available), rollover_available,
            max_available, month_remaining,
        )

    def can_spend(self, amount_usd: float, trading_day_index: int) -> bool:
        self._validate_amount(amount_usd)
        return amount_usd <= self.snapshot(trading_day_index).max_available_today_usd + _EPSILON

    def record_spend(self, amount_usd: float, trading_day_index: int) -> BudgetSnapshot:
        self._validate_amount(amount_usd)
        if not self.can_spend(amount_usd, trading_day_index):
            raise ValueError("API spend exceeds currently available earned budget")
        self.monthly_spend_usd += amount_usd
        self._daily_spend[trading_day_index] = self._daily_spend.get(trading_day_index, 0.0) + amount_usd
        return self.snapshot(trading_day_index)

    @staticmethod
    def _validate_day(trading_day_index: int) -> None:
        if trading_day_index < 1:
            raise ValueError("trading_day_index must start at 1")

    @staticmethod
    def _validate_amount(amount_usd: float) -> None:
        if amount_usd < 0:
            raise ValueError("amount_usd cannot be negative")
