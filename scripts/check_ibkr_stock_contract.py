import os
import sys

from dotenv import load_dotenv

from earnings_calendar_spreads.brokers.ibkr_client import IBKRClient


def main():
  load_dotenv()

  symbol = sys.argv[1] if len(sys.argv) > 1 else "AAPL"

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

    details = client.get_stock_contract_details(
      symbol=symbol,
      primary_exchange="NASDAQ" if symbol.upper() == "AAPL" else None,
    )

    print(f"Found {len(details)} contract detail result(s) for {symbol}.")

    for item in details:
      contract = item.contract

      print()
      print(f"symbol: {contract.symbol}")
      print(f"secType: {contract.secType}")
      print(f"exchange: {contract.exchange}")
      print(f"primaryExchange: {contract.primaryExchange}")
      print(f"currency: {contract.currency}")
      print(f"conId: {contract.conId}")
      print(f"localSymbol: {contract.localSymbol}")
      print(f"tradingClass: {contract.tradingClass}")

  finally:
    client.disconnect_and_wait()


if __name__ == "__main__":
  main()