import os
import sys
from datetime import date
from dotenv import load_dotenv

from ibapi.tag_value import TagValue
from earnings_calendar_spreads.brokers.ibkr_calendar_resolution import (
  adjust_plan_to_common_strike,
)
from earnings_calendar_spreads.brokers.ibkr_calendar_plan import (
  build_calendar_spread_plan_from_ibkr_chain,
)
from earnings_calendar_spreads.brokers.ibkr_calendar_spread import (
  build_calendar_spread_contract,
  make_calendar_option_contracts,
)
from earnings_calendar_spreads.brokers.ibkr_client import IBKRClient
from earnings_calendar_spreads.brokers.ibkr_orders import (
  build_calendar_spread_limit_order,
)
from earnings_calendar_spreads.core.calendar_spread import (
  price_calendar_spread_plan,
)
from earnings_calendar_spreads.data.yfinance_client import get_current_price
from earnings_calendar_spreads.core.order_policy import EntryOrderPolicy


def resolve_first_contract(
  client: IBKRClient,
  contract,
):
  details = client.get_contract_details(contract)

  if not details:
    raise ValueError("No contract details found.")

  return details[0].contract


def main():
  load_dotenv()

  symbol = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
  earnings_date = (
    date.fromisoformat(sys.argv[2])
    if len(sys.argv) > 2
    else date.today()
  )
  primary_exchange = sys.argv[3] if len(sys.argv) > 3 else "NASDAQ"

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
      right="C",
      quantity=1,
    )

    original_strike = plan.strike

    plan = adjust_plan_to_common_strike(
      client=client,
      plan=plan,
      underlying_price=underlying_price,
    )

    if plan.strike != original_strike:
      print(
        f"Adjusted strike from {original_strike} to {plan.strike} "
        "because both legs must use a listed common strike."
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
      transmit=False,
    )

    order.smartComboRoutingParams = [
      TagValue("NonGuaranteed", "1"),
    ]

    print()
    print(f"Calendar pricing for {priced_plan.symbol}")
    print(f"Underlying price: {underlying_price}")
    print(f"Short expiration: {priced_plan.short_expiration}")
    print(f"Long expiration: {priced_plan.long_expiration}")
    print(f"Strike: {priced_plan.strike}")
    print(f"Right: {priced_plan.right}")
    print(f"Quantity: {priced_plan.quantity}")

    print()
    print("Short/front option")
    print(f"localSymbol: {short_contract.localSymbol}")
    print(f"bid: {short_bid}")
    print(f"ask: {short_ask}")

    print()
    print("Long/back option")
    print(f"localSymbol: {long_contract.localSymbol}")
    print(f"bid: {long_bid}")
    print(f"ask: {long_ask}")

    print()
    print("Pricing")
    print(f"net_debit: {priced_plan.net_debit}")

    print()
    print("BAG contract")
    print(f"symbol: {bag_contract.symbol}")
    print(f"secType: {bag_contract.secType}")
    print(f"combo legs: {len(bag_contract.comboLegs)}")

    should_transmit = "--transmit" in sys.argv
    order.transmit = should_transmit

    policy = EntryOrderPolicy()

    print()
    print("Order preview")
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
        print(f"Order was not filled within {policy.fill_timeout_seconds} seconds. Cancelling order.")

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