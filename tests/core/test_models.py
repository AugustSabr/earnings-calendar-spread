from datetime import date

from earnings_calendar_spreads.core.models import EarningsEvent
from earnings_calendar_spreads.core.models import ScreeningResult

def test_earnings_event_stores_values():
  event = EarningsEvent(
    symbol="AAPL",
    report_date=date(2026, 6, 29),
    report_time="amc",
  )

  assert event.symbol == "AAPL"
  assert event.report_date == date(2026, 6, 29)
  assert event.report_time == "amc"

def test_screening_result_stores_values():
  result = ScreeningResult(
    symbol="AAPL",
    average_volume=2_000_000,
    iv30_rv30=1.4,
    term_structure_slope=-0.005,
    expected_move="5.2%",
    passes_average_volume=True,
    passes_iv30_rv30=True,
    passes_term_structure_slope=True,
    qualifies=True,
  )

  assert result.symbol == "AAPL"
  assert result.qualifies
  assert result.expected_move == "5.2%"