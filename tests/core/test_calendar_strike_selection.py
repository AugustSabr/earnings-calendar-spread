import pytest

from earnings_calendar_spreads.core.calendar_strike_selection import (
  select_atm_strike,
  select_common_atm_strike,
)


def test_select_atm_strike():
  strike = select_atm_strike(
    strikes=[
      90.0,
      95.0,
      100.0,
      105.0,
    ],
    underlying_price=103.0,
  )

  assert strike == 105.0


def test_select_atm_strike_sorts_not_required():
  strike = select_atm_strike(
    strikes=[
      105.0,
      90.0,
      100.0,
      95.0,
    ],
    underlying_price=101.0,
  )

  assert strike == 100.0


def test_select_atm_strike_requires_strikes():
  with pytest.raises(ValueError, match="strikes"):
    select_atm_strike(
      strikes=[],
      underlying_price=100.0,
    )


def test_select_atm_strike_requires_positive_underlying_price():
  with pytest.raises(ValueError, match="underlying_price"):
    select_atm_strike(
      strikes=[
        95.0,
        100.0,
        105.0,
      ],
      underlying_price=0,
    )

def test_select_common_atm_strike():
  strike = select_common_atm_strike(
    short_strikes=[
      280.0,
      282.5,
      285.0,
    ],
    long_strikes=[
      275.0,
      280.0,
      285.0,
    ],
    underlying_price=281.74,
  )

  assert strike == 280.0


def test_select_common_atm_strike_requires_common_strikes():
  with pytest.raises(ValueError, match="common strikes"):
    select_common_atm_strike(
      short_strikes=[
        282.5,
      ],
      long_strikes=[
        280.0,
        285.0,
      ],
      underlying_price=281.74,
    )