from dataclasses import dataclass
from datetime import date

from ibapi.contract import Contract
from ibapi.order import Order
from ibapi.tag_value import TagValue

from earnings_calendar_spreads.brokers.ibkr_calendar_plan import (
  build_calendar_spread_plan_from_ibkr_chain,
)
from earnings_calendar_spreads.brokers.ibkr_calendar_resolution import (
  adjust_plan_to_common_strike,
)
from earnings_calendar_spreads.brokers.ibkr_calendar_spread import (
  build_calendar_spread_contract,
  make_calendar_option_contracts,
)
from earnings_calendar_spreads.brokers.ibkr_orders import (
  build_calendar_spread_limit_order,
)
from earnings_calendar_spreads.core.calendar_spread import (
  price_calendar_spread_plan,
)
from earnings_calendar_spreads.core.models import CalendarSpreadPlan
from earnings_calendar_spreads.data.yfinance_client import get_current_price


@dataclass(frozen=True)
class PreparedCalendarEntry:
  """
  Ferdig forberedt calendar entry, men ikke sendt.
  """
  plan: CalendarSpreadPlan
  underlying_price: float
  short_contract: Contract
  long_contract: Contract
  bag_contract: Contract
  order: Order
  short_bid: float
  short_ask: float
  long_bid: float
  long_ask: float


def resolve_first_contract(
  client,
  contract: Contract,
) -> Contract:
  """
  Resolver en generic IBKR contract og returnerer første match.
  """
  details = client.get_contract_details(contract)

  if not details:
    raise ValueError("No contract details found.")

  return details[0].contract


def prepare_calendar_entry(
  client,
  symbol: str,
  earnings_date: date,
  primary_exchange: str | None = None,
  right: str = "C",
  quantity: int = 1,
  transmit: bool = False,
) -> PreparedCalendarEntry:
  """
  Forbereder en calendar entry fra IBKR/yfinance-data.

  Sender ikke ordre.
  """
  stock_details = client.get_stock_contract_details(
    symbol=symbol,
    primary_exchange=primary_exchange,
  )

  if not stock_details:
    raise ValueError("No stock contract details found.")

  stock_contract = stock_details[0].contract

  parameters = client.get_option_chain_parameters(
    underlying_symbol=symbol,
    underlying_con_id=stock_contract.conId,
  )

  underlying_price = get_current_price(symbol)

  plan = build_calendar_spread_plan_from_ibkr_chain(
    symbol=symbol,
    parameters=parameters,
    entry_date=date.today(),
    earnings_date=earnings_date,
    underlying_price=underlying_price,
    right=right,
    quantity=quantity,
  )

  plan = adjust_plan_to_common_strike(
    client=client,
    plan=plan,
    underlying_price=underlying_price,
  )

  short_generic_contract, long_generic_contract = make_calendar_option_contracts(
    plan,
  )

  short_contract = resolve_first_contract(
    client=client,
    contract=short_generic_contract,
  )
  long_contract = resolve_first_contract(
    client=client,
    contract=long_generic_contract,
  )

  short_bid, short_ask = client.get_bid_ask(
    contract=short_contract,
    req_id=300,
    timeout=20,
  )
  long_bid, long_ask = client.get_bid_ask(
    contract=long_contract,
    req_id=301,
    timeout=20,
  )

  priced_plan = price_calendar_spread_plan(
    plan=plan,
    front_bid=short_bid,
    back_ask=long_ask,
  )

  bag_contract = build_calendar_spread_contract(
    symbol=priced_plan.symbol,
    short_option_contract=short_contract,
    long_option_contract=long_contract,
  )

  order = build_calendar_spread_limit_order(
    net_debit=priced_plan.net_debit,
    quantity=priced_plan.quantity,
    transmit=transmit,
  )

  order.smartComboRoutingParams = [
    TagValue("NonGuaranteed", "1"),
  ]

  return PreparedCalendarEntry(
    plan=priced_plan,
    underlying_price=underlying_price,
    short_contract=short_contract,
    long_contract=long_contract,
    bag_contract=bag_contract,
    order=order,
    short_bid=short_bid,
    short_ask=short_ask,
    long_bid=long_bid,
    long_ask=long_ask,
  )