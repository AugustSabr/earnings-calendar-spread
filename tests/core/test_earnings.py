from datetime import date

from earnings_calendar_spreads.core.earnings import filter_actionable_earnings


def test_filters_today_after_close_and_tomorrow_before_open():
  earnings = [
    {"symbol": "AAPL", "date": "2026-06-29", "hour": "amc"},
    {"symbol": "MSFT", "date": "2026-06-30", "hour": "bmo"},
    {"symbol": "NVDA", "date": "2026-06-29", "hour": "bmo"},
    {"symbol": "TSLA", "date": "2026-06-30", "hour": "amc"},
  ]

  result = filter_actionable_earnings(earnings, today=date(2026, 6, 29))

  assert result == {
    "today_after_close": ["AAPL"],
    "tomorrow_before_open": ["MSFT"],
  }


def test_skips_items_without_symbol():
  earnings = [
    {"date": "2026-06-29", "hour": "amc"},
  ]

  result = filter_actionable_earnings(earnings, today=date(2026, 6, 29))

  assert result == {
    "today_after_close": [],
    "tomorrow_before_open": [],
  }