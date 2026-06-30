import pytest

from earnings_calendar_spreads.core.calendar_spread import (
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