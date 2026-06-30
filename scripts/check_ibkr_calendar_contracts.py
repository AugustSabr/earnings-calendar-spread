import os
import sys
from datetime import date
from dotenv import load_dotenv

from earnings_calendar_spreads.brokers.ibkr_option_chain import (
  select_option_chain_parameters,
)
from earnings_calendar_spreads.brokers.ibkr_calendar_plan import (
  build_calendar_spread_plan_from_ibkr_chain,
)
from earnings_calendar_spreads.brokers.ibkr_calendar_spread import (
  make_calendar_option_contracts,
  build_calendar_spread_contract,
)
from earnings_calendar_spreads.brokers.ibkr_client import IBKRClient
from earnings_calendar_spreads.data.yfinance_client import get_current_price
from earnings_calendar_spreads.brokers.ibkr_calendar_resolution import (
  adjust_plan_to_common_strike,
)

def print_contract(label, contract):
  print()
  print(label)
  print(f"symbol: {contract.symbol}")
  print(f"secType: {contract.secType}")
  print(f"exchange: {contract.exchange}")
  print(f"currency: {contract.currency}")
  print(f"lastTradeDateOrContractMonth: {contract.lastTradeDateOrContractMonth}")
  print(f"strike: {contract.strike}")
  print(f"right: {contract.right}")
  print(f"multiplier: {contract.multiplier}")
  print(f"conId: {contract.conId}")
  print(f"localSymbol: {contract.localSymbol}")
  print(f"tradingClass: {contract.tradingClass}")

def print_combo_contract(contract):
  print()
  print("Calendar BAG contract")
  print(f"symbol: {contract.symbol}")
  print(f"secType: {contract.secType}")
  print(f"exchange: {contract.exchange}")
  print(f"currency: {contract.currency}")

  for index, leg in enumerate(contract.comboLegs, start=1):
    print()
    print(f"Leg {index}")
    print(f"conId: {leg.conId}")
    print(f"ratio: {leg.ratio}")
    print(f"action: {leg.action}")
    print(f"exchange: {leg.exchange}")

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

    selected_parameters = select_option_chain_parameters(parameters)

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

    short_details = client.get_contract_details(short_generic_contract)
    long_details = client.get_contract_details(long_generic_contract)

    if not short_details:
      raise ValueError("No short option contract details found.")

    if not long_details:
      raise ValueError("No long option contract details found.")

    short_contract = short_details[0].contract
    long_contract = long_details[0].contract

    print(f"Calendar contracts for {plan.symbol}")
    print(f"Underlying price: {underlying_price}")
    print(f"Short expiration: {plan.short_expiration}")
    print(f"Long expiration: {plan.long_expiration}")
    print(f"Strike: {plan.strike}")
    print(f"Right: {plan.right}")
    print(f"Quantity: {plan.quantity}")

    print_contract("Short/front option", short_contract)
    print_contract("Long/back option", long_contract)

    bag_contract = build_calendar_spread_contract(
      symbol=plan.symbol,
      short_option_contract=short_contract,
      long_option_contract=long_contract,
    )

    print_combo_contract(bag_contract)

  finally:
    client.disconnect_and_wait()


if __name__ == "__main__":
  main()