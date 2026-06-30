from dataclasses import dataclass
from decimal import Decimal

from earnings_calendar_spreads.brokers.ibkr_positions import IBKRPosition


@dataclass(frozen=True)
class IBKRCalendarSpreadPosition:
  """
  Matching short/long option positions som ser ut som en calendar spread.
  """
  symbol: str
  short_position: IBKRPosition
  long_position: IBKRPosition
  quantity: Decimal


def is_option_position(position: IBKRPosition) -> bool:
  return position.contract.secType == "OPT"


def get_calendar_position_key(position: IBKRPosition) -> tuple:
  contract = position.contract

  return (
    contract.symbol,
    contract.strike,
    contract.right,
    contract.multiplier,
    contract.tradingClass,
  )


def find_calendar_spread_positions(
  positions: list[IBKRPosition],
  symbol: str | None = None,
) -> list[IBKRCalendarSpreadPosition]:
  """
  Finner matching calendar spread-posisjoner.

  Matcher:
  - samme symbol
  - samme strike
  - samme right
  - samme multiplier
  - short/front position < 0
  - long/back position > 0
  - short expiration før long expiration
  """
  cleaned_symbol = symbol.strip().upper() if symbol else None

  option_positions = [
    position
    for position in positions
    if is_option_position(position)
    and position.position != Decimal("0")
    and (
      cleaned_symbol is None
      or position.contract.symbol == cleaned_symbol
    )
  ]

  short_positions = [
    position
    for position in option_positions
    if position.position < Decimal("0")
  ]

  long_positions = [
    position
    for position in option_positions
    if position.position > Decimal("0")
  ]

  spreads = []

  for short_position in short_positions:
    for long_position in long_positions:
      if get_calendar_position_key(short_position) != get_calendar_position_key(long_position):
        continue

      if (
        short_position.contract.lastTradeDateOrContractMonth
        >= long_position.contract.lastTradeDateOrContractMonth
      ):
        continue

      quantity = min(
        abs(short_position.position),
        long_position.position,
      )

      spreads.append(
        IBKRCalendarSpreadPosition(
          symbol=short_position.contract.symbol,
          short_position=short_position,
          long_position=long_position,
          quantity=quantity,
        )
      )

  return spreads