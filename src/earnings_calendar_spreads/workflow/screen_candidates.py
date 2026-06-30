from datetime import date

from earnings_calendar_spreads.core.models import (
  ScreenedEarningsCandidate,
  ScreeningResult,
)
from earnings_calendar_spreads.workflow.earnings_scan import (
  scan_earnings_candidates,
  scan_earnings_candidate_events,
)
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

def screen_earnings_candidate_events(today):
  """
  Scanner og screener earnings candidates, men beholder earnings event-data.
  """
  events = scan_earnings_candidate_events(today=today)

  screened_candidates = []

  for event in events:
    try:
      screening_result = screen_symbol(
        symbol=event.symbol,
        today=today,
      )

      screened_candidates.append(
        ScreenedEarningsCandidate(
          earnings_event=event,
          screening_result=screening_result,
        )
      )

    except Exception as error:
      print(f"Skipping {event.symbol}: {error}")

  return screened_candidates