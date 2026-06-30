import pytest

from earnings_calendar_spreads.core.calendar_spread import (
  build_calendar_spread_plan,
  calculate_calendar_net_debit,
)


def test_calculate_calendar_net_debit():
  net_debit = calculate_calendar_net_debit(
    front_bid=1.20,
    back_ask=2.45,
  )

  assert net_debit == pytest.approx(1.25)


def test_calculate_calendar_net_debit_requires_positive_front_bid():
  with pytest.raises(ValueError, match="front_bid"):
    calculate_calendar_net_debit(
      front_bid=0,
      back_ask=2.45,
    )


def test_calculate_calendar_net_debit_requires_positive_back_ask():
  with pytest.raises(ValueError, match="back_ask"):
    calculate_calendar_net_debit(
      front_bid=1.20,
      back_ask=0,
    )


def test_calculate_calendar_net_debit_requires_positive_net_debit():
  with pytest.raises(ValueError, match="net_debit"):
    calculate_calendar_net_debit(
      front_bid=2.45,
      back_ask=1.20,
    )

def test_build_calendar_spread_plan():
  plan = build_calendar_spread_plan(
    symbol="aapl",
    short_expiration="2026-07-17",
    long_expiration="2026-08-21",
    strike=300,
    right="c",
    front_bid=1.20,
    back_ask=2.45,
    quantity=2,
  )

  assert plan.symbol == "AAPL"
  assert plan.short_expiration == "2026-07-17"
  assert plan.long_expiration == "2026-08-21"
  assert plan.strike == 300.0
  assert plan.right == "C"
  assert plan.quantity == 2
  assert plan.net_debit == pytest.approx(1.25)


def test_build_calendar_spread_plan_requires_later_long_expiration():
  with pytest.raises(ValueError, match="long_expiration"):
    build_calendar_spread_plan(
      symbol="AAPL",
      short_expiration="2026-08-21",
      long_expiration="2026-07-17",
      strike=300,
      right="C",
      front_bid=1.20,
      back_ask=2.45,
    )


def test_build_calendar_spread_plan_requires_valid_right():
  with pytest.raises(ValueError, match="right"):
    build_calendar_spread_plan(
      symbol="AAPL",
      short_expiration="2026-07-17",
      long_expiration="2026-08-21",
      strike=300,
      right="X",
      front_bid=1.20,
      back_ask=2.45,
    )