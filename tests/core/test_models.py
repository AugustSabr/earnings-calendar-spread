from datetime import date

from earnings_calendar_spreads.core.models import EarningsEvent


def test_earnings_event_stores_values():
  event = EarningsEvent(
    symbol="AAPL",
    report_date=date(2026, 6, 29),
    report_time="amc",
  )

  assert event.symbol == "AAPL"
  assert event.report_date == date(2026, 6, 29)
  assert event.report_time == "amc"