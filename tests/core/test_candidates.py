from datetime import date

from earnings_calendar_spreads.core.models import EarningsEvent
from earnings_calendar_spreads.core.candidates import (
  find_earnings_candidate_events,
  find_earnings_candidates,
)

def test_finds_clean_earnings_candidates():
  earnings = [
    EarningsEvent("aapl", date(2026, 6, 29), "amc"),
    EarningsEvent("MSFT", date(2026, 6, 30), "bmo"),
    EarningsEvent("BRK.B", date(2026, 6, 29), "amc"),
    EarningsEvent("NVDA", date(2026, 6, 29), "bmo"),
  ]

  result = find_earnings_candidates(earnings, today=date(2026, 6, 29))

  assert result == ["AAPL", "MSFT"]

def test_find_earnings_candidate_events_keeps_earnings_date():
  today = date(2026, 7, 1)

  events = [
    EarningsEvent(
      symbol="AAPL",
      report_date=today,
      report_time="amc",
    ),
    EarningsEvent(
      symbol="MSFT",
      report_date=date(2026, 7, 2),
      report_time="bmo",
    ),
    EarningsEvent(
      symbol="BAD.W",
      report_date=today,
      report_time="amc",
    ),
  ]

  candidates = find_earnings_candidate_events(
    earnings=events,
    today=today,
  )

  assert [candidate.symbol for candidate in candidates] == [
    "AAPL",
    "MSFT",
  ]
  assert candidates[0].report_date == date(2026, 7, 1)
  assert candidates[1].report_date == date(2026, 7, 2)