from datetime import datetime

from earnings_calendar_spreads.core.models import CalendarSpreadPlan


VALID_OPTION_RIGHTS = {"C", "P"}


def calculate_calendar_net_debit(
  front_bid: float,
  back_ask: float,
) -> float:
  """
  Beregner net debit for en long calendar spread.

  Long calendar:
  - selg front option på bid
  - kjøp back option på ask
  """
  if front_bid <= 0:
    raise ValueError("front_bid must be greater than zero.")

  if back_ask <= 0:
    raise ValueError("back_ask must be greater than zero.")

  net_debit = back_ask - front_bid

  if net_debit <= 0:
    raise ValueError("net_debit must be greater than zero.")

  return net_debit


def build_calendar_spread_plan(
  symbol: str,
  short_expiration: str,
  long_expiration: str,
  strike: float,
  right: str,
  front_bid: float,
  back_ask: float,
  quantity: int = 1,
) -> CalendarSpreadPlan:
  """
  Bygger en broker-uavhengig trade plan for long calendar spread.
  """
  cleaned_symbol = symbol.strip().upper()

  if not cleaned_symbol:
    raise ValueError("symbol is required.")

  if quantity <= 0:
    raise ValueError("quantity must be greater than zero.")

  cleaned_right = right.strip().upper()

  if cleaned_right not in VALID_OPTION_RIGHTS:
    raise ValueError("right must be C or P.")

  short_date = datetime.strptime(short_expiration, "%Y-%m-%d").date()
  long_date = datetime.strptime(long_expiration, "%Y-%m-%d").date()

  if long_date <= short_date:
    raise ValueError("long_expiration must be after short_expiration.")

  net_debit = calculate_calendar_net_debit(
    front_bid=front_bid,
    back_ask=back_ask,
  )

  return CalendarSpreadPlan(
    symbol=cleaned_symbol,
    short_expiration=short_expiration,
    long_expiration=long_expiration,
    strike=float(strike),
    right=cleaned_right,
    quantity=quantity,
    net_debit=net_debit,
  )