from datetime import date

from earnings_calendar_spreads.core.models import ScreeningResult
from earnings_calendar_spreads.workflow.screen_candidates import (
  screen_earnings_candidates,
)


def find_entry_candidates(today: date) -> list[ScreeningResult]:
  """
  Finner screening-resultater som kvalifiserer for mulig entry.
  """
  results = screen_earnings_candidates(today=today)

  return [
    result
    for result in results
    if result.qualifies
  ]