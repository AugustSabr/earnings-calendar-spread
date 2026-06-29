from datetime import date

import pytest

from earnings_calendar_spreads.core.option_expirations import filter_expiration_dates


def test_keeps_expirations_until_first_date_at_least_45_days_out():
  expirations = [
    "2026-07-03",
    "2026-07-10",
    "2026-08-14",
  ]

  result = filter_expiration_dates(
    expiration_dates=expirations,
    today=date(2026, 6, 29),
  )

  assert result == [
    "2026-07-03",
    "2026-07-10",
    "2026-08-14",
  ]


def test_removes_today_expiration_if_first():
  expirations = [
    "2026-06-29",
    "2026-07-03",
    "2026-08-14",
  ]

  result = filter_expiration_dates(
    expiration_dates=expirations,
    today=date(2026, 6, 29),
  )

  assert result == [
    "2026-07-03",
    "2026-08-14",
  ]


def test_raises_error_if_no_expiration_is_far_enough_out():
  expirations = [
    "2026-07-03",
    "2026-07-10",
  ]

  with pytest.raises(ValueError):
    filter_expiration_dates(
      expiration_dates=expirations,
      today=date(2026, 6, 29),
    )