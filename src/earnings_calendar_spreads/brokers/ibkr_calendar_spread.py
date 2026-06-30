from ibapi.contract import ComboLeg, Contract


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