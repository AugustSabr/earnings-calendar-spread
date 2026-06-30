from datetime import date

from earnings_calendar_spreads.core.earnings import filter_actionable_earnings
from earnings_calendar_spreads.core.models import EarningsEvent
from earnings_calendar_spreads.core.symbol_filter import filter_standard_symbols
from earnings_calendar_spreads.core.symbols import is_standard_us_symbol


def find_earnings_candidates(
  earnings: list[EarningsEvent],
  today: date,
) -> list[str]:
  """
  Returnerer standard US-symboler med relevante earnings-hendelser.
  """
  filtered = filter_actionable_earnings(earnings, today)

  symbols = (
    filtered["today_after_close"]
    + filtered["tomorrow_before_open"]
  )

  return filter_standard_symbols(symbols)

def find_earnings_candidate_events(
  earnings: list[EarningsEvent],
  today,
) -> list[EarningsEvent]:
  """
  Finner actionable earnings events og beholder earnings-datoen.
  """
  actionable = filter_actionable_earnings(
    earnings=earnings,
    today=today,
  )

  symbols = set(
    actionable["today_after_close"]
    + actionable["tomorrow_before_open"]
  )

  return [
    event
    for event in earnings
    if event.symbol.strip().upper() in symbols
    and is_standard_us_symbol(event.symbol)
  ]