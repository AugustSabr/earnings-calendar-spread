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

  finally:
    client.disconnect_and_wait()


if __name__ == "__main__":
  main()