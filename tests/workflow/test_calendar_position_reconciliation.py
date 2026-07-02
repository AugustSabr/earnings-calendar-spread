from decimal import Decimal

from ibapi.contract import Contract

from earnings_calendar_spreads.brokers.ibkr_positions import IBKRPosition
from earnings_calendar_spreads.workflow.calendar_position_reconciliation import (
  find_matching_calendar_spread,
  get_current_matching_calendar_spread,
)
from earnings_calendar_spreads.brokers.ibkr_calendar_positions import (
  find_calendar_spread_positions,
)


class FakeClient:
  def __init__(self, positions):
    self.positions = positions

  def get_positions(self):
    return self.positions


def make_option_contract(
  con_id: int,
  expiration: str,
  strike: float = 295.0,
  symbol: str = "AAPL",
) -> Contract:
  contract = Contract()
  contract.conId = con_id
  contract.symbol = symbol
  contract.secType = "OPT"
  contract.lastTradeDateOrContractMonth = expiration
  contract.strike = strike
  contract.right = "C"
  contract.multiplier = "100"
  contract.tradingClass = symbol
  return contract


def make_position(
  contract: Contract,
  position,
) -> IBKRPosition:
  return IBKRPosition(
    account="DU123",
    contract=contract,
    position=Decimal(str(position)),
    average_cost=0.0,
  )


def test_find_matching_calendar_spread_by_contract_ids():
  short_contract = make_option_contract(
    con_id=1,
    expiration="20260702",
  )
  long_contract = make_option_contract(
    con_id=2,
    expiration="20260821",
  )

  positions = [
    make_position(short_contract, -1),
    make_position(long_contract, 1),
  ]

  spreads = find_calendar_spread_positions(positions)

  match = find_matching_calendar_spread(
    spreads=spreads,
    short_contract=short_contract,
    long_contract=long_contract,
  )

  assert match is not None
  assert match.symbol == "AAPL"
  assert match.quantity == Decimal("1")


def test_find_matching_calendar_spread_returns_none_for_wrong_contracts():
  short_contract = make_option_contract(
    con_id=1,
    expiration="20260702",
  )
  long_contract = make_option_contract(
    con_id=2,
    expiration="20260821",
  )
  other_contract = make_option_contract(
    con_id=3,
    expiration="20260821",
  )

  positions = [
    make_position(short_contract, -1),
    make_position(long_contract, 1),
  ]

  spreads = find_calendar_spread_positions(positions)

  match = find_matching_calendar_spread(
    spreads=spreads,
    short_contract=short_contract,
    long_contract=other_contract,
  )

  assert match is None


def test_get_current_matching_calendar_spread_reads_positions_from_client():
  short_contract = make_option_contract(
    con_id=1,
    expiration="20260702",
  )
  long_contract = make_option_contract(
    con_id=2,
    expiration="20260821",
  )

  client = FakeClient(
    positions=[
      make_position(short_contract, -1),
      make_position(long_contract, 1),
    ]
  )

  match = get_current_matching_calendar_spread(
    client=client,
    short_contract=short_contract,
    long_contract=long_contract,
    symbol="AAPL",
  )

  assert match is not None
  assert match.quantity == Decimal("1")