from decimal import Decimal

from ibapi.contract import Contract

from earnings_calendar_spreads.brokers.ibkr_calendar_positions import (
  find_calendar_spread_positions,
)
from earnings_calendar_spreads.brokers.ibkr_positions import IBKRPosition


def make_option_position(
  symbol: str,
  expiration: str,
  strike: float,
  right: str,
  quantity: str,
) -> IBKRPosition:
  contract = Contract()
  contract.symbol = symbol
  contract.secType = "OPT"
  contract.lastTradeDateOrContractMonth = expiration
  contract.strike = strike
  contract.right = right
  contract.multiplier = "100"
  contract.tradingClass = symbol

  return IBKRPosition(
    account="TEST",
    contract=contract,
    position=Decimal(quantity),
    average_cost=0.0,
  )


def test_find_calendar_spread_positions():
  short_position = make_option_position(
    symbol="AAPL",
    expiration="20260701",
    strike=285.0,
    right="C",
    quantity="-7",
  )
  long_position = make_option_position(
    symbol="AAPL",
    expiration="20260821",
    strike=285.0,
    right="C",
    quantity="7",
  )

  spreads = find_calendar_spread_positions([
    short_position,
    long_position,
  ])

  assert len(spreads) == 1
  assert spreads[0].symbol == "AAPL"
  assert spreads[0].short_position == short_position
  assert spreads[0].long_position == long_position
  assert spreads[0].quantity == Decimal("7")


def test_find_calendar_spread_positions_filters_by_symbol():
  aapl_short = make_option_position(
    symbol="AAPL",
    expiration="20260701",
    strike=285.0,
    right="C",
    quantity="-1",
  )
  aapl_long = make_option_position(
    symbol="AAPL",
    expiration="20260821",
    strike=285.0,
    right="C",
    quantity="1",
  )
  msft_long = make_option_position(
    symbol="MSFT",
    expiration="20260821",
    strike=500.0,
    right="C",
    quantity="1",
  )

  spreads = find_calendar_spread_positions(
    positions=[
      aapl_short,
      aapl_long,
      msft_long,
    ],
    symbol="AAPL",
  )

  assert len(spreads) == 1
  assert spreads[0].symbol == "AAPL"


def test_find_calendar_spread_positions_requires_matching_strike():
  short_position = make_option_position(
    symbol="AAPL",
    expiration="20260701",
    strike=285.0,
    right="C",
    quantity="-1",
  )
  long_position = make_option_position(
    symbol="AAPL",
    expiration="20260821",
    strike=290.0,
    right="C",
    quantity="1",
  )

  spreads = find_calendar_spread_positions([
    short_position,
    long_position,
  ])

  assert spreads == []


def test_find_calendar_spread_positions_requires_later_long_expiration():
  short_position = make_option_position(
    symbol="AAPL",
    expiration="20260821",
    strike=285.0,
    right="C",
    quantity="-1",
  )
  long_position = make_option_position(
    symbol="AAPL",
    expiration="20260701",
    strike=285.0,
    right="C",
    quantity="1",
  )

  spreads = find_calendar_spread_positions([
    short_position,
    long_position,
  ])

  assert spreads == []