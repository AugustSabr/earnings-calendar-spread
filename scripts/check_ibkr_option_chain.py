import os
import sys

from dotenv import load_dotenv

from earnings_calendar_spreads.brokers.ibkr_client import IBKRClient


def main():
  load_dotenv()

  symbol = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
  primary_exchange = sys.argv[2] if len(sys.argv) > 2 else "NASDAQ"

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

    print(f"Found {len(parameters)} option chain parameter result(s) for {symbol}.")
    print(f"Underlying conId: {stock_contract.conId}")

    for item in parameters:
      print()
      print(f"exchange: {item.exchange}")
      print(f"trading_class: {item.trading_class}")
      print(f"multiplier: {item.multiplier}")
      print(f"expirations count: {len(item.expirations)}")
      print(f"first expirations: {item.expirations[:5]}")
      print(f"strikes count: {len(item.strikes)}")
      print(f"first strikes: {item.strikes[:10]}")
      print(f"last strikes: {item.strikes[-10:]}")

  finally:
    client.disconnect_and_wait()


if __name__ == "__main__":
  main()