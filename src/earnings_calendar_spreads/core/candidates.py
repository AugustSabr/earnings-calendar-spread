from datetime import date

from earnings_calendar_spreads.core.earnings import filter_actionable_earnings
from earnings_calendar_spreads.core.models import EarningsEvent
from earnings_calendar_spreads.core.symbol_filter import filter_standard_symbols


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