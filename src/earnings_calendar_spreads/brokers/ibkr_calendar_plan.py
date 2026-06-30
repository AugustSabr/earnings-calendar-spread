from datetime import date

from earnings_calendar_spreads.brokers.ibkr_option_chain import (
  IBKROptionChainParameters,
  ibkr_expiration_to_iso,
  select_option_chain_parameters,
)
from earnings_calendar_spreads.core.calendar_spread_selection import (
  build_calendar_spread_selection,
)
from earnings_calendar_spreads.core.models import CalendarSpreadPlan


def build_calendar_spread_plan_from_ibkr_chain(
  symbol: str,
  parameters: list[IBKROptionChainParameters],
  entry_date: date,
  earnings_date: date,
  underlying_price: float,
  right: str = "C",
  quantity: int = 1,
  preferred_exchange: str = "SMART",
  target_long_dte: int = 45,
) -> CalendarSpreadPlan:
  """
  Bygger en broker-uavhengig calendar spread plan fra IBKR option chain metadata.

  IBKR bruker expiration-format YYYYMMDD.
  Core-logikken bruker YYYY-MM-DD.
  """
  selected_parameters = select_option_chain_parameters(
    parameters=parameters,
    preferred_exchange=preferred_exchange,
  )

  expiration_dates = [
    ibkr_expiration_to_iso(expiration)
    for expiration in selected_parameters.expirations
  ]

  return build_calendar_spread_selection(
    symbol=symbol,
    expiration_dates=expiration_dates,
    strikes=selected_parameters.strikes,
    entry_date=entry_date,
    earnings_date=earnings_date,
    underlying_price=underlying_price,
    right=right,
    quantity=quantity,
    target_long_dte=target_long_dte,
  )