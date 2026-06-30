import os
import sys
from datetime import date

from dotenv import load_dotenv

from earnings_calendar_spreads.brokers.ibkr_client import IBKRClient
from earnings_calendar_spreads.core.order_policy import EntryOrderPolicy
from earnings_calendar_spreads.workflow.prepare_calendar_entry import (
  prepare_calendar_entry,
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


def main():
  load_dotenv()

  symbol = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
  earnings_date = (
    date.fromisoformat(sys.argv[2])
    if len(sys.argv) > 2
    else date.today()
  )
  primary_exchange = sys.argv[3] if len(sys.argv) > 3 else "NASDAQ"
  should_transmit = "--transmit" in sys.argv

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

    entry = prepare_calendar_entry(
      client=client,
      symbol=symbol,
      earnings_date=earnings_date,
      primary_exchange=primary_exchange,
      transmit=should_transmit,
    )

    print_entry_preview(entry)

    order_id = client.place_order(
      contract=entry.bag_contract,
      order=entry.order,
      wait_for_status=True,
      timeout=10,
    )

    print()
    print("Submitted to TWS")
    print(f"order_id: {order_id}")
    print(f"transmit: {entry.order.transmit}")
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