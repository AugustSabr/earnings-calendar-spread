from datetime import date

import pytest

from earnings_calendar_spreads.core.calendar_spread_selection import (
  build_calendar_spread_selection,
)


def test_build_calendar_spread_selection():
  selection = build_calendar_spread_selection(
    symbol="aapl",
    expiration_dates=[
      "2026-07-03",
      "2026-07-17",
      "2026-08-21",
    ],
    strikes=[
      290.0,
      300.0,
      310.0,
    ],
    entry_date=date(2026, 7, 1),
    earnings_date=date(2026, 7, 2),
    underlying_price=303.0,
    right="c",
    quantity=2,
  )

  assert selection.symbol == "AAPL"
  assert selection.short_expiration == "2026-07-03"
  assert selection.long_expiration == "2026-08-21"
  assert selection.strike == 300.0
  assert selection.right == "C"
  assert selection.quantity == 2
  assert selection.net_debit is None


def test_build_calendar_spread_selection_requires_symbol():
  with pytest.raises(ValueError, match="symbol"):
    build_calendar_spread_selection(
      symbol="",
      expiration_dates=[
        "2026-07-03",
        "2026-08-21",
      ],
      strikes=[
        300.0,
      ],
      entry_date=date(2026, 7, 1),
      earnings_date=date(2026, 7, 2),
      underlying_price=303.0,
    )


def test_build_calendar_spread_selection_requires_valid_right():
  with pytest.raises(ValueError, match="right"):
    build_calendar_spread_selection(
      symbol="AAPL",
      expiration_dates=[
        "2026-07-03",
        "2026-08-21",
      ],
      strikes=[
        300.0,
      ],
      entry_date=date(2026, 7, 1),
      earnings_date=date(2026, 7, 2),
      underlying_price=303.0,
      right="X",
    )


def test_build_calendar_spread_selection_requires_positive_quantity():
  with pytest.raises(ValueError, match="quantity"):
    build_calendar_spread_selection(
      symbol="AAPL",
      expiration_dates=[
        "2026-07-03",
        "2026-08-21",
      ],
      strikes=[
        300.0,
      ],
      entry_date=date(2026, 7, 1),
      earnings_date=date(2026, 7, 2),
      underlying_price=303.0,
      quantity=0,
    )