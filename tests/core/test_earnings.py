from datetime import date

from earnings_calendar_spreads.core.earnings import filter_actionable_earnings
from earnings_calendar_spreads.core.models import EarningsEvent


def test_filters_today_after_close_and_tomorrow_before_open():
  earnings = [
    EarningsEvent("AAPL", date(2026, 6, 29), "amc"),
    EarningsEvent("MSFT", date(2026, 6, 30), "bmo"),
    EarningsEvent("NVDA", date(2026, 6, 29), "bmo"),
    EarningsEvent("TSLA", date(2026, 6, 30), "amc")
  ]

  result = filter_actionable_earnings(earnings, today=date(2026, 6, 29))

  assert result == {
    "today_after_close": ["AAPL"],
    "tomorrow_before_open": ["MSFT"],
  }


def test_report_time_is_case_insensitive():
  earnings = [
    EarningsEvent("AAPL", date(2026, 6, 29), "AMC"),
    EarningsEvent("MSFT", date(2026, 6, 30), "BMO"),
  ]

  result = filter_actionable_earnings(earnings, today=date(2026, 6, 29))

  assert result == {
    "today_after_close": ["AAPL"],
    "tomorrow_before_open": ["MSFT"],
  }