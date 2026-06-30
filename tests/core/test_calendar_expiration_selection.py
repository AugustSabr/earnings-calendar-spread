from datetime import date

import pytest

from earnings_calendar_spreads.core.calendar_expiration_selection import (
  select_calendar_expirations,
)


def test_select_calendar_expirations():
  short_expiration, long_expiration = select_calendar_expirations(
    expiration_dates=[
      "2026-07-03",
      "2026-07-10",
      "2026-07-17",
      "2026-08-21",
    ],
    entry_date=date(2026, 7, 1),
    earnings_date=date(2026, 7, 2),
    target_long_dte=45,
  )

  assert short_expiration == "2026-07-03"
  assert long_expiration == "2026-08-21"


def test_select_calendar_expirations_sorts_dates():
  short_expiration, long_expiration = select_calendar_expirations(
    expiration_dates=[
      "2026-08-21",
      "2026-07-17",
      "2026-07-03",
    ],
    entry_date=date(2026, 7, 1),
    earnings_date=date(2026, 7, 2),
    target_long_dte=45,
  )

  assert short_expiration == "2026-07-03"
  assert long_expiration == "2026-08-21"


def test_select_calendar_expirations_requires_expirations():
  with pytest.raises(ValueError, match="expiration_dates"):
    select_calendar_expirations(
      expiration_dates=[],
      entry_date=date(2026, 7, 1),
      earnings_date=date(2026, 7, 2),
    )


def test_select_calendar_expirations_requires_short_expiration():
  with pytest.raises(ValueError, match="short expiration"):
    select_calendar_expirations(
      expiration_dates=[
        "2026-07-03",
        "2026-07-10",
      ],
      entry_date=date(2026, 7, 1),
      earnings_date=date(2026, 7, 20),
    )


def test_select_calendar_expirations_requires_long_expiration():
  with pytest.raises(ValueError, match="long expiration"):
    select_calendar_expirations(
      expiration_dates=[
        "2026-07-03",
        "2026-07-10",
        "2026-07-17",
      ],
      entry_date=date(2026, 7, 1),
      earnings_date=date(2026, 7, 2),
    )