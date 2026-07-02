import pytest

from earnings_calendar_spreads.core.models import CalendarSpreadPlan
from earnings_calendar_spreads.core.position_sizing import (
  apply_budget_to_calendar_plan,
  calculate_calendar_quantity_for_budget,
  calculate_calendar_spread_debit_usd,
)


def test_calculate_calendar_spread_debit_usd():
  assert calculate_calendar_spread_debit_usd(
    quoted_debit=10.5,
    quantity=2,
  ) == 2100.0


def test_calculate_calendar_quantity_for_budget():
  assert calculate_calendar_quantity_for_budget(
    max_debit_per_symbol_usd=2500.0,
    quoted_debit=10.5,
  ) == 2


def test_calculate_calendar_quantity_for_budget_returns_zero_when_too_small():
  assert calculate_calendar_quantity_for_budget(
    max_debit_per_symbol_usd=1000.0,
    quoted_debit=10.5,
  ) == 0


def test_apply_budget_to_calendar_plan():
  plan = CalendarSpreadPlan(
    symbol="AAPL",
    short_expiration="2026-07-02",
    long_expiration="2026-08-21",
    strike=295.0,
    right="C",
    quantity=1,
    net_debit=10.5,
  )

  sized_plan = apply_budget_to_calendar_plan(
    plan=plan,
    max_debit_per_symbol_usd=2500.0,
  )

  assert sized_plan.quantity == 2
  assert sized_plan.net_debit == 10.5


def test_apply_budget_to_calendar_plan_requires_net_debit():
  plan = CalendarSpreadPlan(
    symbol="AAPL",
    short_expiration="2026-07-02",
    long_expiration="2026-08-21",
    strike=295.0,
    right="C",
    quantity=1,
    net_debit=None,
  )

  with pytest.raises(ValueError, match="net_debit"):
    apply_budget_to_calendar_plan(
      plan=plan,
      max_debit_per_symbol_usd=2500.0,
    )


def test_apply_budget_to_calendar_plan_raises_when_budget_too_small():
  plan = CalendarSpreadPlan(
    symbol="AAPL",
    short_expiration="2026-07-02",
    long_expiration="2026-08-21",
    strike=295.0,
    right="C",
    quantity=1,
    net_debit=10.5,
  )

  with pytest.raises(ValueError, match="too small"):
    apply_budget_to_calendar_plan(
      plan=plan,
      max_debit_per_symbol_usd=1000.0,
    )