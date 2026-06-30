import os
import sys

from dotenv import load_dotenv
from ibapi.tag_value import TagValue

from earnings_calendar_spreads.brokers.ibkr_calendar_positions import (
  find_calendar_spread_positions,
)
from earnings_calendar_spreads.brokers.ibkr_calendar_spread import (
  build_calendar_spread_contract,
)
from earnings_calendar_spreads.brokers.ibkr_client import IBKRClient
from earnings_calendar_spreads.brokers.ibkr_orders import (
  build_calendar_spread_close_order,
)
from earnings_calendar_spreads.core.calendar_spread import (
  calculate_calendar_close_credit,
)
from earnings_calendar_spreads.core.order_policy import ExitOrderPolicy

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

    positions = client.get_positions()

    spreads = find_calendar_spread_positions(
      positions=positions,
      symbol=symbol,
    )

    if not spreads:
      print(f"No calendar spread positions found for {symbol}.")
      return

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
      transmit=should_transmit,
    )

    order.smartComboRoutingParams = [
      TagValue("NonGuaranteed", "1"),
    ]

    print()
    print(f"Calendar close order for {spread.symbol}")
    print(f"Quantity: {spread.quantity}")

    print()
    print("Short/front option")
    print(f"localSymbol: {short_contract.localSymbol}")
    print(f"position: {spread.short_position.position}")
    print(f"bid: {short_bid}")
    print(f"ask: {short_ask}")

    print()
    print("Long/back option")
    print(f"localSymbol: {long_contract.localSymbol}")
    print(f"position: {spread.long_position.position}")
    print(f"bid: {long_bid}")
    print(f"ask: {long_ask}")

    print()
    print("Close pricing")
    print(f"close_credit: {close_credit}")

    print()
    print("Close order preview")
    print("Uses entry BAG direction, then SELL combo to close.")
    print(f"action: {order.action}")
    print(f"orderType: {order.orderType}")
    print(f"totalQuantity: {order.totalQuantity}")
    print(f"lmtPrice: {order.lmtPrice}")
    print(f"transmit: {order.transmit}")

    order_id = client.place_order(
      contract=bag_contract,
      order=order,
      wait_for_status=True,
      timeout=10,
    )

    print()
    print("Submitted to TWS")
    print(f"order_id: {order_id}")
    print(f"transmit: {order.transmit}")
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

      if final_status is None or final_status["status"] != "Filled":
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