from dataclasses import replace

from earnings_calendar_spreads.brokers.ibkr_contracts import (
  make_option_expiration_query_contract,
)
from earnings_calendar_spreads.brokers.ibkr_option_chain import (
  iso_expiration_to_ibkr,
)
from earnings_calendar_spreads.core.calendar_strike_selection import (
  select_common_atm_strike,
)
from earnings_calendar_spreads.core.models import CalendarSpreadPlan

def get_available_strikes_for_expiration(
  client,
  symbol: str,
  expiration: str,
  right: str,
  timeout: int = 20,
) -> list[float]:
  """
  Henter strikes som faktisk finnes for én expiration/right hos IBKR.
  """
  query_contract = make_option_expiration_query_contract(
    symbol=symbol,
    expiration=iso_expiration_to_ibkr(expiration),
    right=right,
  )

  details = client.get_contract_details(
    query_contract,
    timeout=timeout,
  )

  return sorted(
    {item.contract.strike for item in details}
  )


def adjust_plan_to_common_strike(
  client,
  plan: CalendarSpreadPlan,
  underlying_price: float,
  timeout: int = 20,
) -> CalendarSpreadPlan:
  """
  Justerer plan.strike til nærmeste strike som finnes for begge legs.
  """
  short_strikes = get_available_strikes_for_expiration(
    client=client,
    symbol=plan.symbol,
    expiration=plan.short_expiration,
    right=plan.right,
    timeout=timeout,
  )

  long_strikes = get_available_strikes_for_expiration(
    client=client,
    symbol=plan.symbol,
    expiration=plan.long_expiration,
    right=plan.right,
    timeout=timeout,
  )

  common_strike = select_common_atm_strike(
    short_strikes=short_strikes,
    long_strikes=long_strikes,
    underlying_price=underlying_price,
  )

  return replace(
    plan,
    strike=common_strike,
  )