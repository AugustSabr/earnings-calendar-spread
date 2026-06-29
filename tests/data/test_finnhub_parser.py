from datetime import date

from earnings_calendar_spreads.core.models import EarningsEvent
from earnings_calendar_spreads.data.finnhub_parser import parse_finnhub_earnings_events


def test_parses_finnhub_earnings_events():
  raw_events = [
    {"symbol": "AAPL", "date": "2026-06-29", "hour": "amc"},
    {"symbol": "MSFT", "date": "2026-06-30", "hour": "bmo"},
  ]

  result = parse_finnhub_earnings_events(raw_events)

  assert result == [
    EarningsEvent("AAPL", date(2026, 6, 29), "amc"),
    EarningsEvent("MSFT", date(2026, 6, 30), "bmo"),
  ]


def test_skips_events_with_missing_values():
  raw_events = [
    {"symbol": "AAPL", "date": "2026-06-29"},
    {"symbol": "MSFT", "hour": "bmo"},
    {"date": "2026-06-30", "hour": "amc"},
  ]

  result = parse_finnhub_earnings_events(raw_events)

  assert result == []