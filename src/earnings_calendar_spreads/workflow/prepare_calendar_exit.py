from dataclasses import dataclass

from ibapi.contract import Contract
from ibapi.order import Order
from ibapi.tag_value import TagValue

from earnings_calendar_spreads.brokers.ibkr_calendar_positions import (
  IBKRCalendarSpreadPosition,
  find_calendar_spread_positions,
)
from earnings_calendar_spreads.brokers.ibkr_calendar_spread import (
  build_calendar_spread_contract,
)
from earnings_calendar_spreads.brokers.ibkr_orders import (
  build_calendar_spread_close_order,
)
from earnings_calendar_spreads.core.calendar_spread import (
  calculate_calendar_close_credit,
)
from earnings_calendar_spreads.brokers.ibkr_positions import (
  get_positions_with_retry,
)


@dataclass(frozen=True)
class PreparedCalendarExit:
  """
  Ferdig forberedt calendar exit, men ikke sendt.
  """
  spread: IBKRCalendarSpreadPosition
  short_contract: Contract
  long_contract: Contract
  bag_contract: Contract
  order: Order
  short_bid: float
  short_ask: float
  long_bid: float
  long_ask: float
  close_credit: float


def prepare_calendar_exit(
  client,
  symbol: str,
  transmit: bool = False,
) -> PreparedCalendarExit | None:
  """
  Forbereder close order for første matching calendar spread.

  Sender ikke ordre.
  """
  positions = get_positions_with_retry(client)

  spreads = find_calendar_spread_positions(
    positions=positions,
    symbol=symbol,
  )

  if not spreads:
    return None

  spread = spreads[0]

  short_contract = spread.short_position.contract
  long_contract = spread.long_position.contract

  short_bid, short_ask = client.get_bid_ask(
    contract=short_contract,
    req_id=400,
    timeout=20,
  )

  long_bid, long_ask = client.get_bid_ask(
    contract=long_contract,
    req_id=401,
    timeout=20,
  )

  close_credit = calculate_calendar_close_credit(
    front_ask=short_ask,
    back_bid=long_bid,
  )

  bag_contract = build_calendar_spread_contract(
    symbol=spread.symbol,
    short_option_contract=short_contract,
    long_option_contract=long_contract,
  )

  order = build_calendar_spread_close_order(
    close_credit=close_credit,
    quantity=int(spread.quantity),
    transmit=transmit,
  )

  order.smartComboRoutingParams = [
    TagValue("NonGuaranteed", "1"),
  ]

  return PreparedCalendarExit(
    spread=spread,
    short_contract=short_contract,
    long_contract=long_contract,
    bag_contract=bag_contract,
    order=order,
    short_bid=short_bid,
    short_ask=short_ask,
    long_bid=long_bid,
    long_ask=long_ask,
    close_credit=close_credit,
  )