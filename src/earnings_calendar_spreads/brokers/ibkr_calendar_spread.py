from ibapi.contract import ComboLeg, Contract

from earnings_calendar_spreads.brokers.ibkr_contracts import make_option_contract
from earnings_calendar_spreads.brokers.ibkr_option_chain import iso_expiration_to_ibkr
from earnings_calendar_spreads.core.models import CalendarSpreadPlan

def build_calendar_spread_contract(
  symbol: str,
  short_option_contract: Contract,
  long_option_contract: Contract,
  exchange: str = "SMART",
) -> Contract:
  """
  Bygger en IBKR BAG-kontrakt for long calendar spread.

  Calendar:
  - SELL short/front option
  - BUY long/back option
  """
  if not short_option_contract.conId:
    raise ValueError("short_option_contract must have a conId.")

  if not long_option_contract.conId:
    raise ValueError("long_option_contract must have a conId.")

  contract = Contract()
  contract.symbol = symbol.strip().upper()
  contract.secType = "BAG"
  contract.exchange = exchange
  contract.currency = "USD"

  short_leg = ComboLeg()
  short_leg.conId = short_option_contract.conId
  short_leg.ratio = 1
  short_leg.action = "SELL"
  short_leg.exchange = exchange

  long_leg = ComboLeg()
  long_leg.conId = long_option_contract.conId
  long_leg.ratio = 1
  long_leg.action = "BUY"
  long_leg.exchange = exchange

  contract.comboLegs = [
    short_leg,
    long_leg,
  ]

  return contract

def make_calendar_option_contracts(
  plan: CalendarSpreadPlan,
) -> tuple[Contract, Contract]:
  """
  Lager generic short/long option contracts fra en calendar spread plan.

  Returnerer:
  - short/front option contract
  - long/back option contract
  """
  short_contract = make_option_contract(
    symbol=plan.symbol,
    expiration=iso_expiration_to_ibkr(plan.short_expiration),
    strike=plan.strike,
    right=plan.right,
  )

  long_contract = make_option_contract(
    symbol=plan.symbol,
    expiration=iso_expiration_to_ibkr(plan.long_expiration),
    strike=plan.strike,
    right=plan.right,
  )

  return short_contract, long_contract

def build_calendar_spread_close_contract(
  symbol: str,
  short_option_contract: Contract,
  long_option_contract: Contract,
  exchange: str = "SMART",
) -> Contract:
  """
  Bygger en IBKR BAG-kontrakt for å lukke en long calendar spread.

  Close:
  - BUY short/front option tilbake
  - SELL long/back option
  """
  if not short_option_contract.conId:
    raise ValueError("short_option_contract must have a conId.")

  if not long_option_contract.conId:
    raise ValueError("long_option_contract must have a conId.")

  contract = Contract()
  contract.symbol = symbol.strip().upper()
  contract.secType = "BAG"
  contract.exchange = exchange
  contract.currency = "USD"

  short_leg = ComboLeg()
  short_leg.conId = short_option_contract.conId
  short_leg.ratio = 1
  short_leg.action = "BUY"
  short_leg.exchange = exchange

  long_leg = ComboLeg()
  long_leg.conId = long_option_contract.conId
  long_leg.ratio = 1
  long_leg.action = "SELL"
  long_leg.exchange = exchange

  contract.comboLegs = [
    short_leg,
    long_leg,
  ]

  return contract