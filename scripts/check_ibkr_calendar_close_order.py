import os
import sys

from dotenv import load_dotenv

from earnings_calendar_spreads.brokers.ibkr_client import IBKRClient
from earnings_calendar_spreads.core.order_policy import ExitOrderPolicy
from earnings_calendar_spreads.workflow.prepare_calendar_exit import (
  prepare_calendar_exit,
)


def print_exit_preview(exit):
  spread = exit.spread
  order = exit.order

  print()
  print(f"Calendar close order for {spread.symbol}")
  print(f"Quantity: {spread.quantity}")

  print()
  print("Short/front option")
  print(f"localSymbol: {exit.short_contract.localSymbol}")
  print(f"position: {spread.short_position.position}")
  print(f"bid: {exit.short_bid}")
  print(f"ask: {exit.short_ask}")

  print()
  print("Long/back option")
  print(f"localSymbol: {exit.long_contract.localSymbol}")
  print(f"position: {spread.long_position.position}")
  print(f"bid: {exit.long_bid}")
  print(f"ask: {exit.long_ask}")

  print()
  print("Close pricing")
  print(f"close_credit: {exit.close_credit}")

  print()
  print("Close order preview")
  print("Uses entry BAG direction, then SELL combo to close.")
  print(f"action: {order.action}")
  print(f"orderType: {order.orderType}")
  print(f"totalQuantity: {order.totalQuantity}")
  print(f"lmtPrice: {order.lmtPrice}")
  print(f"transmit: {order.transmit}")


def main():
  load_dotenv()

  symbol = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
  should_transmit = "--transmit" in sys.argv

  policy = ExitOrderPolicy()

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

    exit = prepare_calendar_exit(
      client=client,
      symbol=symbol,
      transmit=should_transmit,
    )

    if exit is None:
      print(f"No calendar spread positions found for {symbol}.")
      return

    print_exit_preview(exit)

    order_id = client.place_order(
      contract=exit.bag_contract,
      order=exit.order,
      wait_for_status=True,
      timeout=10,
    )

    print()
    print("Submitted to TWS")
    print(f"order_id: {order_id}")
    print(f"transmit: {exit.order.transmit}")
    print(f"latest_status: {client.order_status_by_id.get(order_id)}")

    if should_transmit:
      final_status = client.wait_for_order_status(
        order_id=order_id,
        target_statuses={
          "Filled",
          "Cancelled",
          "Inactive",
        },
        timeout=policy.fill_timeout_seconds,
      )

      print()
      print("Final/latest status after wait")
      print(final_status)

      if (
        policy.cancel_if_not_filled
        and (
          final_status is None
          or final_status["status"] != "Filled"
        )
      ):
        print()
        print(
          f"Order was not filled within {policy.fill_timeout_seconds} seconds. "
          "Cancelling order."
        )

        client.cancel_order(order_id)

        cancelled_status = client.wait_for_order_status(
          order_id=order_id,
          target_statuses={
            "Cancelled",
            "Inactive",
            "Filled",
          },
          timeout=10,
        )

        print()
        print("Status after cancel attempt")
        print(cancelled_status)

  finally:
    client.disconnect_and_wait()


if __name__ == "__main__":
  main()