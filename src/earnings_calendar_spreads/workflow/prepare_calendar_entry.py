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
from earnings_calendar_spreads.brokers.ibkr_contracts import make_stock_contract


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

def resolve_standard_option_contract(
  client,
  contract,
  symbol: str,
):
  normalized_symbol = symbol.strip().upper()
  contract_details = client.get_contract_details(contract)

  standard_contracts = [
    details.contract
    for details in contract_details
    if details.contract.tradingClass == normalized_symbol
    and str(details.contract.multiplier) == "100"
  ]

  smart_standard_contracts = [
    contract
    for contract in standard_contracts
    if contract.exchange == "SMART"
  ]

  if smart_standard_contracts:
    selected_contract = smart_standard_contracts[0]
    selected_contract.exchange = "SMART"
    return selected_contract

  if standard_contracts:
    selected_contract = standard_contracts[0]
    selected_contract.exchange = "SMART"
    return selected_contract

  summaries = [
    (
      details.contract.localSymbol,
      details.contract.conId,
      details.contract.exchange,
      details.contract.tradingClass,
      details.contract.multiplier,
      details.contract.lastTradeDateOrContractMonth,
      details.contract.strike,
      details.contract.right,
    )
    for details in contract_details
  ]

  raise ValueError(
    f"No standard option contract found for {symbol}. "
    f"Available contracts: {summaries}"
  )

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
  Forbereder en calendar entry fra IBKR-data.

  Sender ikke ordre.
  """
  stock_contract_details = client.get_stock_contract_details(
    symbol=symbol,
    primary_exchange=primary_exchange,
  )

  if not stock_contract_details:
    raise ValueError(f"No stock contract details found for {symbol}")

  resolved_stock_contract = stock_contract_details[0].contract

  quote_stock_contract = make_stock_contract(
    symbol=symbol,
    primary_exchange=primary_exchange,
  )

  try:
    underlying_price = client.get_underlying_price(
      contract=quote_stock_contract,
      req_id=client.get_next_request_id(),
      timeout=30,
    )

  except TimeoutError as error:
    raise TimeoutError(
      f"Timed out waiting for IBKR underlying price for {symbol}. {error}"
    ) from error

  parameters = client.get_option_chain_parameters(
    symbol,
    resolved_stock_contract.conId,
    timeout=20,
  )

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

  short_contract = resolve_standard_option_contract(
    client=client,
    contract=short_generic_contract,
    symbol=symbol,
  )

  long_contract = resolve_standard_option_contract(
    client=client,
    contract=long_generic_contract,
    symbol=symbol,
  )

  try:
    short_bid, short_ask = client.get_bid_ask(
      contract=short_contract,
      req_id=client.get_next_request_id(),
      timeout=30,
    )

  except TimeoutError as error:
    raise TimeoutError(
      f"Timed out waiting for short/front option quote "
      f"{short_contract.localSymbol} "
      f"conId={short_contract.conId} "
      f"exchange={short_contract.exchange} "
      f"tradingClass={short_contract.tradingClass}. "
      f"{error}"
    ) from error

  try:
    long_bid, long_ask = client.get_bid_ask(
      contract=long_contract,
      req_id=client.get_next_request_id(),
      timeout=30,
    )

  except TimeoutError as error:
    raise TimeoutError(
      f"Timed out waiting for long/back option quote "
      f"{long_contract.localSymbol} "
      f"conId={long_contract.conId} "
      f"exchange={long_contract.exchange} "
      f"tradingClass={long_contract.tradingClass}. "
      f"{error}"
    ) from error

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