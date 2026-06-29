from datetime import date

from earnings_calendar_spreads.core.candidates import find_earnings_candidates
from earnings_calendar_spreads.core.models import EarningsEvent


def test_finds_clean_earnings_candidates():
  earnings = [
    EarningsEvent("aapl", date(2026, 6, 29), "amc"),
    EarningsEvent("MSFT", date(2026, 6, 30), "bmo"),
    EarningsEvent("BRK.B", date(2026, 6, 29), "amc"),
    EarningsEvent("NVDA", date(2026, 6, 29), "bmo"),
  ]

  result = find_earnings_candidates(earnings, today=date(2026, 6, 29))

  assert result == ["AAPL", "MSFT"]