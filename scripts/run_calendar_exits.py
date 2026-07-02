"""
Runner for closing open IBKR calendar spread positions.

Modes:
  default / list:
    Only lists detected open calendar spreads.
    Does not request option quotes.
    Does not stage or transmit orders.

  --prepare:
    Finds open calendar spreads and prices close orders using live IBKR quotes.
    Does not place orders.

  --stage:
    Finds open calendar spreads, prices close orders, and stages untransmitted
    close orders in TWS.
    Does not transmit orders.

  --transmit:
    Finds open calendar spreads, prices close orders, and transmits close orders
    to IBKR Paper/TWS.

Optional symbol filters:
  python scripts/run_calendar_exits.py AAPL MSFT --prepare

Notes:
  The close workflow assumes at most one open calendar spread per symbol.
  Use --prepare, --stage, or --transmit only when market data is available.
"""
import os
import sys

from dotenv import load_dotenv

from earnings_calendar_spreads.brokers.ibkr_calendar_positions import (
  find_calendar_spread_positions,
)
from earnings_calendar_spreads.brokers.ibkr_client import IBKRClient
from earnings_calendar_spreads.core.order_policy import ExitOrderPolicy
from earnings_calendar_spreads.workflow.execute_calendar_exit import (
  execute_calendar_exit,
)
from earnings_calendar_spreads.workflow.prepare_calendar_exit import (
  prepare_calendar_exit,
)
from earnings_calendar_spreads.brokers.ibkr_option_chain import (
  ibkr_expiration_to_iso,
)
from earnings_calendar_spreads.storage.trade_log import (
  append_trade_log_event,
  make_calendar_trade_id,
  make_trade_log_event,
)
from earnings_calendar_spreads.workflow.calendar_position_reconciliation import (
  get_current_matching_calendar_spread,
)

def print_spread_summary(spread):
  short_contract = spread.short_position.contract
  long_contract = spread.long_position.contract

  print()
  print(f"{spread.symbol}")
  print(f"Quantity: {spread.quantity}")
  print(f"Short/front: {short_contract.localSymbol} position={spread.short_position.position}")
  print(f"Long/back:   {long_contract.localSymbol} position={spread.long_position.position}")


def print_prepared_exit(prepared_exit):
  spread = prepared_exit.spread
  order = prepared_exit.order

  print()
  print(f"Prepared close for {spread.symbol}")
  print(f"Quantity: {spread.quantity}")
  print(f"Short bid/ask: {prepared_exit.short_bid} / {prepared_exit.short_ask}")
  print(f"Long bid/ask:  {prepared_exit.long_bid} / {prepared_exit.long_ask}")
  print(f"Close credit: {prepared_exit.close_credit}")

  print()
  print("Order")
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


def get_mode(args):
  modes = [
    flag
    for flag in ["--prepare", "--stage", "--transmit"]
    if flag in args
  ]

  if len(modes) > 1:
    raise ValueError("Use only one of --prepare, --stage, or --transmit.")

  if not modes:
    return "list"

  return modes[0].replace("--", "")

def log_calendar_closed_if_confirmed(
  client,
  prepared_exit,
  execution_result,
) -> bool:
  if not execution_result.transmitted:
    return False

  final_status = execution_result.final_status

  order_status_confirms_close = (
    final_status is not None
    and final_status.get("status") == "Filled"
  )

  matching_spread = get_current_matching_calendar_spread(
    client=client,
    short_contract=prepared_exit.short_contract,
    long_contract=prepared_exit.long_contract,
    symbol=prepared_exit.spread.symbol,
    wait_seconds=3,
  )

  position_confirms_close = matching_spread is None

  if not order_status_confirms_close and not position_confirms_close:
    return False

  spread = prepared_exit.spread
  short_contract = prepared_exit.short_contract
  long_contract = prepared_exit.long_contract

  short_expiration = ibkr_expiration_to_iso(
    short_contract.lastTradeDateOrContractMonth,
  )
  long_expiration = ibkr_expiration_to_iso(
    long_contract.lastTradeDateOrContractMonth,
  )

  trade_id = make_calendar_trade_id(
    symbol=spread.symbol,
    short_expiration=short_expiration,
    long_expiration=long_expiration,
    strike=short_contract.strike,
    right=short_contract.right,
  )

  confirmation_source = (
    "order_status"
    if order_status_confirms_close
    else "positions_reconciliation"
  )

  event = make_trade_log_event(
    event_type="calendar_closed",
    trade_id=trade_id,
    symbol=spread.symbol,
    data={
      "confirmation_source": confirmation_source,
      "exit_order_id": execution_result.order_id,
      "exit_order_status": (
        final_status.get("status")
        if final_status is not None
        else None
      ),
      "exit_limit_credit": prepared_exit.close_credit,
      "exit_avg_fill_price": (
        final_status.get("avg_fill_price")
        if final_status is not None
        else None
      ),
      "quantity": int(spread.quantity),
      "short_expiration": short_expiration,
      "long_expiration": long_expiration,
      "strike": short_contract.strike,
      "right": short_contract.right,
      "short_local_symbol": short_contract.localSymbol,
      "long_local_symbol": long_contract.localSymbol,
      "short_con_id": short_contract.conId,
      "long_con_id": long_contract.conId,
    },
  )

  append_trade_log_event(event)

  return True

def main():
  load_dotenv()

  args = sys.argv[1:]
  mode = get_mode(args)

  requested_symbols = {
    arg.upper()
    for arg in args
    if not arg.startswith("--")
  }

  print("Calendar exit runner")
  print(f"Mode: {mode}")

  if requested_symbols:
    print(f"Symbols: {', '.join(sorted(requested_symbols))}")
  else:
    print("Symbols: all open calendar spreads")

  host = os.getenv("IBKR_HOST", "127.0.0.1")
  port = int(os.getenv("IBKR_PORT", "7497"))
  client_id = int(os.getenv("IBKR_CLIENT_ID", "180"))

  client = IBKRClient()
  policy = ExitOrderPolicy()

  try:
    client.connect_and_start(
      host=host,
      port=port,
      client_id=client_id,
    )

    positions = client.get_positions()
    spreads = find_calendar_spread_positions(positions)

    if requested_symbols:
      spreads = [
        spread
        for spread in spreads
        if spread.symbol.upper() in requested_symbols
      ]

    print()
    print(f"Calendar spreads found: {len(spreads)}")

    if not spreads:
      return

    symbols_seen = set()

    for spread in spreads:
      print_spread_summary(spread)

      if spread.symbol in symbols_seen:
        print()
        print("Skipping duplicate symbol. Current exit workflow assumes one open calendar spread per symbol.")
        continue

      symbols_seen.add(spread.symbol)

      if mode == "list":
        continue

      if mode == "prepare":
        prepared_exit = prepare_calendar_exit(
          client=client,
          symbol=spread.symbol,
          transmit=False,
        )

        if prepared_exit is None:
          print(f"No closeable spread found for {spread.symbol}.")
          continue

        print_prepared_exit(prepared_exit)
        continue

      execution = execute_calendar_exit(
        client=client,
        symbol=spread.symbol,
        policy=policy,
        transmit=mode == "transmit",
      )

      if execution.prepared_exit is None:
        print(f"No closeable spread found for {spread.symbol}.")
        continue

      print_prepared_exit(execution.prepared_exit)
      print_execution_result(execution.execution_result)

      was_logged = log_calendar_closed_if_confirmed(
        client=client,
        prepared_exit=execution.prepared_exit,
        execution_result=execution.execution_result,
      )

      if was_logged:
        print()
        print("Logged calendar_closed event.")

  finally:
    client.disconnect_and_wait()


if __name__ == "__main__":
  main()