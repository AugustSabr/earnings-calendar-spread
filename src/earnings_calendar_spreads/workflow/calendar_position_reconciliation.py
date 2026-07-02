import time

from ibapi.contract import Contract

from earnings_calendar_spreads.brokers.ibkr_calendar_positions import (
  IBKRCalendarSpreadPosition,
  find_calendar_spread_positions,
)


def find_matching_calendar_spread(
  spreads: list[IBKRCalendarSpreadPosition],
  short_contract: Contract,
  long_contract: Contract,
) -> IBKRCalendarSpreadPosition | None:
  for spread in spreads:
    if (
      spread.short_position.contract.conId == short_contract.conId
      and spread.long_position.contract.conId == long_contract.conId
    ):
      return spread

  return None


def get_current_matching_calendar_spread(
  client,
  short_contract: Contract,
  long_contract: Contract,
  symbol: str | None = None,
  wait_seconds: int = 0,
) -> IBKRCalendarSpreadPosition | None:
  if wait_seconds > 0:
    time.sleep(wait_seconds)

  positions = client.get_positions()

  spreads = find_calendar_spread_positions(
    positions=positions,
    symbol=symbol,
  )

  return find_matching_calendar_spread(
    spreads=spreads,
    short_contract=short_contract,
    long_contract=long_contract,
  )