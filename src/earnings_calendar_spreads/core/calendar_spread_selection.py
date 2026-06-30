from datetime import date

from earnings_calendar_spreads.core.calendar_expiration_selection import (
  select_calendar_expirations,
)
from earnings_calendar_spreads.core.calendar_strike_selection import (
  select_atm_strike,
)
from earnings_calendar_spreads.core.models import CalendarSpreadPlan

VALID_OPTION_RIGHTS = {"C", "P"}


def build_calendar_spread_selection(
  symbol: str,
  expiration_dates: list[str],
  strikes: list[float],
  entry_date: date,
  earnings_date: date,
  underlying_price: float,
  right: str = "C",
  quantity: int = 1,
  target_long_dte: int = 45,
) -> CalendarSpreadPlan:
  """
  Velger expirations og ATM strike for en calendar spread.

  Forventer expiration_dates som ISO-datoer: YYYY-MM-DD.
  """
  cleaned_symbol = symbol.strip().upper()

  if not cleaned_symbol:
    raise ValueError("symbol is required.")

  cleaned_right = right.strip().upper()

  if cleaned_right not in VALID_OPTION_RIGHTS:
    raise ValueError("right must be C or P.")

  if quantity <= 0:
    raise ValueError("quantity must be greater than zero.")

  short_expiration, long_expiration = select_calendar_expirations(
    expiration_dates=expiration_dates,
    entry_date=entry_date,
    earnings_date=earnings_date,
    target_long_dte=target_long_dte,
  )

  strike = select_atm_strike(
    strikes=strikes,
    underlying_price=underlying_price,
  )

  return CalendarSpreadPlan(
    symbol=cleaned_symbol,
    short_expiration=short_expiration,
    long_expiration=long_expiration,
    strike=strike,
    right=cleaned_right,
    quantity=quantity,
  )