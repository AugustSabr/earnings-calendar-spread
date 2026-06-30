import pytest

from ibapi.contract import Contract

from earnings_calendar_spreads.core.models import CalendarSpreadPlan
from earnings_calendar_spreads.brokers.ibkr_calendar_spread import (
  build_calendar_spread_contract,
  make_calendar_option_contracts,
)


def make_resolved_option_contract(con_id: int) -> Contract:
  contract = Contract()
  contract.symbol = "AAPL"
  contract.secType = "OPT"
  contract.conId = con_id
  return contract


def test_build_calendar_spread_contract():
  short_option = make_resolved_option_contract(111)
  long_option = make_resolved_option_contract(222)

  contract = build_calendar_spread_contract(
    symbol="aapl",
    short_option_contract=short_option,
    long_option_contract=long_option,
  )

  assert contract.symbol == "AAPL"
  assert contract.secType == "BAG"
  assert contract.exchange == "SMART"
  assert contract.currency == "USD"

  assert len(contract.comboLegs) == 2

  assert contract.comboLegs[0].conId == 111
  assert contract.comboLegs[0].ratio == 1
  assert contract.comboLegs[0].action == "SELL"
  assert contract.comboLegs[0].exchange == "SMART"

  assert contract.comboLegs[1].conId == 222
  assert contract.comboLegs[1].ratio == 1
  assert contract.comboLegs[1].action == "BUY"
  assert contract.comboLegs[1].exchange == "SMART"


def test_build_calendar_spread_contract_requires_short_con_id():
  short_option = make_resolved_option_contract(0)
  long_option = make_resolved_option_contract(222)

  with pytest.raises(ValueError, match="short_option_contract"):
    build_calendar_spread_contract(
      symbol="AAPL",
      short_option_contract=short_option,
      long_option_contract=long_option,
    )


def test_build_calendar_spread_contract_requires_long_con_id():
  short_option = make_resolved_option_contract(111)
  long_option = make_resolved_option_contract(0)

  with pytest.raises(ValueError, match="long_option_contract"):
    build_calendar_spread_contract(
      symbol="AAPL",
      short_option_contract=short_option,
      long_option_contract=long_option,
    )

def test_make_calendar_option_contracts():
  plan = CalendarSpreadPlan(
    symbol="AAPL",
    short_expiration="2026-07-01",
    long_expiration="2026-08-21",
    strike=282.5,
    right="C",
    quantity=1,
  )

  short_contract, long_contract = make_calendar_option_contracts(plan)

  assert short_contract.symbol == "AAPL"
  assert short_contract.secType == "OPT"
  assert short_contract.lastTradeDateOrContractMonth == "20260701"
  assert short_contract.strike == 282.5
  assert short_contract.right == "C"
  assert short_contract.multiplier == "100"

  assert long_contract.symbol == "AAPL"
  assert long_contract.secType == "OPT"
  assert long_contract.lastTradeDateOrContractMonth == "20260821"
  assert long_contract.strike == 282.5
  assert long_contract.right == "C"
  assert long_contract.multiplier == "100"