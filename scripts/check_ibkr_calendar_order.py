import os
import sys
from datetime import date

from dotenv import load_dotenv

from earnings_calendar_spreads.brokers.ibkr_client import IBKRClient
from earnings_calendar_spreads.core.order_policy import EntryOrderPolicy
from earnings_calendar_spreads.workflow.execute_calendar_entry import (
  execute_calendar_entry,
)
from earnings_calendar_spreads.storage.trade_log import (
  append_trade_log_event,
  make_calendar_trade_id,
  make_trade_log_event,
)
from earnings_calendar_spreads.workflow.calendar_position_reconciliation import (
  get_current_matching_calendar_spread,
)
from earnings_calendar_spreads.core.money import format_usd
from earnings_calendar_spreads.core.position_sizing import (
  calculate_calendar_spread_debit_usd,
)


def print_entry_preview(entry):
  plan = entry.plan
  order = entry.order
  bag_contract = entry.bag_contract

  print()
  print(f"Calendar pricing for {plan.symbol}")
  print(f"Underlying price: {entry.underlying_price}")
  print(f"Short expiration: {plan.short_expiration}")
  print(f"Long expiration: {plan.long_expiration}")
  print(f"Strike: {plan.strike}")
  print(f"Right: {plan.right}")
  print(f"Quantity: {plan.quantity}")

  print()
  print("Short/front option")
  print(f"localSymbol: {entry.short_contract.localSymbol}")
  print(f"bid: {entry.short_bid}")
  print(f"ask: {entry.short_ask}")

  print()
  print("Long/back option")
  print(f"localSymbol: {entry.long_contract.localSymbol}")
  print(f"bid: {entry.long_bid}")
  print(f"ask: {entry.long_ask}")

  print()
  print("Pricing")
  print(f"net_debit: {plan.net_debit}")

  total_debit = calculate_calendar_spread_debit_usd(
    quoted_debit=plan.net_debit,
    quantity=plan.quantity,
  )

  print(f"estimated_total_debit: {format_usd(total_debit)}")

  print()
  print("BAG contract")
  print(f"symbol: {bag_contract.symbol}")
  print(f"secType: {bag_contract.secType}")
  print(f"combo legs: {len(bag_contract.comboLegs)}")

  print()
  print("Order preview")
  print(f"action: {order.action}")
  print(f"orderType: {order.orderType}")
  print(f"totalQuantity: {order.totalQuantity}")
  print(f"lmtPrice: {order.lmtPrice}")
  print(f"transmit: {order.transmit}")


def print_execution_result(result):
  print()
  print("Submitted to TWS")
  print(f"order_id: {result.order_id}")
  print(f"transmit: {result.transmitted}")
  print(f"initial_status: {result.initial_status}")

  if result.final_status is not None:
    print()
    print("Final/latest status after wait")
    print(result.final_status)

  if result.cancel_status is not None:
    print()
    print("Status after cancel attempt")
    print(result.cancel_status)

def log_calendar_opened_if_confirmed(
  client,
  entry,
  execution_result,
) -> bool:
  if not execution_result.transmitted:
    return False

  final_status = execution_result.final_status

  order_status_confirms_fill = (
    final_status is not None
    and final_status.get("status") == "Filled"
  )

  matching_spread = get_current_matching_calendar_spread(
    client=client,
    short_contract=entry.short_contract,
    long_contract=entry.long_contract,
    symbol=entry.plan.symbol,
    wait_seconds=3,
  )

  position_confirms_fill = matching_spread is not None

  if not order_status_confirms_fill and not position_confirms_fill:
    return False

  plan = entry.plan

  trade_id = make_calendar_trade_id(
    symbol=plan.symbol,
    short_expiration=plan.short_expiration,
    long_expiration=plan.long_expiration,
    strike=plan.strike,
    right=plan.right,
  )

  confirmation_source = (
    "order_status"
    if order_status_confirms_fill
    else "positions_reconciliation"
  )

  event = make_trade_log_event(
    event_type="calendar_opened",
    trade_id=trade_id,
    symbol=plan.symbol,
    data={
      "confirmation_source": confirmation_source,
      "entry_order_id": execution_result.order_id,
      "entry_order_status": (
        final_status.get("status")
        if final_status is not None
        else None
      ),
      "entry_limit_debit": plan.net_debit,
      "entry_avg_fill_price": (
        final_status.get("avg_fill_price")
        if final_status is not None
        else None
      ),
      "matched_position_quantity": (
        str(matching_spread.quantity)
        if matching_spread is not None
        else None
      ),
      "quantity": plan.quantity,
      "short_expiration": plan.short_expiration,
      "long_expiration": plan.long_expiration,
      "strike": plan.strike,
      "right": plan.right,
      "short_local_symbol": entry.short_contract.localSymbol,
      "long_local_symbol": entry.long_contract.localSymbol,
      "short_con_id": entry.short_contract.conId,
      "long_con_id": entry.long_contract.conId,
    },
  )

  append_trade_log_event(event)

  return True

def parse_max_debit_per_symbol_usd(args: list[str]) -> float | None:
  for arg in args:
    if arg.startswith("--max-debit="):
      return float(arg.split("=", 1)[1])

  return None

def main():
  load_dotenv()

  symbol = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
  earnings_date = (
    date.fromisoformat(sys.argv[2])
    if len(sys.argv) > 2
    else date.today()
  )

  primary_exchange = None

  args_without_flags = [
    arg
    for arg in sys.argv[1:]
    if not arg.startswith("--")
  ]

  symbol = args_without_flags[0] if len(args_without_flags) > 0 else "AAPL"

  earnings_date = (
    date.fromisoformat(args_without_flags[1])
    if len(args_without_flags) > 1
    else date.today()
  )

  primary_exchange = (
    args_without_flags[2]
    if len(args_without_flags) > 2
    else None
  )

  should_transmit = "--transmit" in sys.argv

  max_debit_per_symbol_usd = parse_max_debit_per_symbol_usd(
    sys.argv[1:],
  )

  policy = EntryOrderPolicy()

  host = os.getenv("IBKR_HOST", "127.0.0.1")
  port = int(os.getenv("IBKR_PORT", "7497"))
  client_id = int(os.getenv("IBKR_CLIENT_ID", "180"))

  client = IBKRClient()

  try:
    client.connect_and_start(
      host=host,
      port=port,
      client_id=client_id,
    )

    try:
      execution = execute_calendar_entry(
        client=client,
        symbol=symbol,
        earnings_date=earnings_date,
        policy=policy,
        primary_exchange=primary_exchange,
        transmit=should_transmit,
        max_debit_per_symbol_usd=max_debit_per_symbol_usd,
      )

    except TimeoutError as error:
      print()
      print(f"Could not prepare calendar entry for {symbol}.")
      print("No order was sent.")
      print(f"Reason: {error}")
      return

    print_entry_preview(execution.prepared_entry)
    print_execution_result(execution.execution_result)

    was_logged = log_calendar_opened_if_confirmed(
      client=client,
      entry=execution.prepared_entry,
      execution_result=execution.execution_result,
    )

    if was_logged:
      print()
      print("Logged calendar_opened event.")

  finally:
    client.disconnect_and_wait()


if __name__ == "__main__":
  main()