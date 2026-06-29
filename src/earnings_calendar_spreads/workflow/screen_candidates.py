from datetime import date

from earnings_calendar_spreads.core.models import ScreeningResult
from earnings_calendar_spreads.workflow.earnings_scan import scan_earnings_candidates
from earnings_calendar_spreads.workflow.screen_symbol import screen_symbol


def screen_earnings_candidates(today: date) -> list[ScreeningResult]:
  """
  Henter earnings-kandidater og screener hvert symbol.
  """
  symbols = scan_earnings_candidates(today=today)

  results = []

  for symbol in symbols:
    try:
      result = screen_symbol(
        symbol=symbol,
        today=today,
      )
      results.append(result)
    except Exception as error:
      print(f"Skipping {symbol}: {error}")

  return results