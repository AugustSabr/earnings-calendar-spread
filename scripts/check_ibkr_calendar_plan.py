import os
import sys
from datetime import date

from dotenv import load_dotenv

from earnings_calendar_spreads.brokers.ibkr_calendar_plan import (
  build_calendar_spread_plan_from_ibkr_chain,
)
from earnings_calendar_spreads.brokers.ibkr_client import IBKRClient
from earnings_calendar_spreads.data.yfinance_client import get_current_price


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

    print(f"Calendar spread plan for {plan.symbol}")
    print(f"Underlying price: {underlying_price}")
    print(f"Short expiration: {plan.short_expiration}")
    print(f"Long expiration: {plan.long_expiration}")
    print(f"Strike: {plan.strike}")
    print(f"Right: {plan.right}")
    print(f"Quantity: {plan.quantity}")
    print(f"Net debit: {plan.net_debit}")

  finally:
    client.disconnect_and_wait()


if __name__ == "__main__":
  main()