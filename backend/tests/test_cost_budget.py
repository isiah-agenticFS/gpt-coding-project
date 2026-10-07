import pytest
from app.cost_budget import RollingApiBudget

def test_unused_budget_rolls_forward():
    budget = RollingApiBudget(monthly_cap_usd=100, baseline_daily_usd=5)
    budget.record_spend(1, 1)
    day2 = budget.snapshot(2)
    assert day2.bank_before_today_usd == pytest.approx(4)
    assert day2.max_available_today_usd == pytest.approx(9)

def test_high_spend_day_can_use_bank():
    budget = RollingApiBudget(monthly_cap_usd=100, baseline_daily_usd=5)
    budget.record_spend(1, 1)
    budget.record_spend(3, 2)
    day3 = budget.snapshot(3)
    assert day3.bank_before_today_usd == pytest.approx(6)
    assert day3.max_available_today_usd == pytest.approx(11)
    budget.record_spend(10, 3)
    assert budget.snapshot(3).max_available_today_usd == pytest.approx(1)

def test_cannot_borrow_from_future_days():
    budget = RollingApiBudget()
    assert budget.can_spend(5, 1)
    assert not budget.can_spend(5.01, 1)

def test_monthly_cap_is_absolute():
    budget = RollingApiBudget(monthly_cap_usd=10, baseline_daily_usd=5)
    budget.record_spend(5, 1)
    budget.record_spend(5, 2)
    assert budget.snapshot(3).max_available_today_usd == 0
