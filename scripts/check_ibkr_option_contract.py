import os
import sys

from dotenv import load_dotenv

from earnings_calendar_spreads.brokers.ibkr_client import IBKRClient
from earnings_calendar_spreads.brokers.ibkr_contracts import make_option_contract


def main():
  load_dotenv()

  symbol = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
  expiration = sys.argv[2] if len(sys.argv) > 2 else "20260717"
  strike = float(sys.argv[3]) if len(sys.argv) > 3 else 300.0
  right = sys.argv[4] if len(sys.argv) > 4 else "C"

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

    contract = make_option_contract(
      symbol=symbol,
      expiration=expiration,
      strike=strike,
      right=right,
    )

    details = client.get_contract_details(contract)

    print(
      f"Found {len(details)} option contract detail result(s) "
      f"for {symbol} {expiration} {strike} {right.upper()}."
    )

    for item in details:
      resolved = item.contract

      print()
      print(f"symbol: {resolved.symbol}")
      print(f"secType: {resolved.secType}")
      print(f"exchange: {resolved.exchange}")
      print(f"currency: {resolved.currency}")
      print(f"lastTradeDateOrContractMonth: {resolved.lastTradeDateOrContractMonth}")
      print(f"strike: {resolved.strike}")
      print(f"right: {resolved.right}")
      print(f"multiplier: {resolved.multiplier}")
      print(f"conId: {resolved.conId}")
      print(f"localSymbol: {resolved.localSymbol}")
      print(f"tradingClass: {resolved.tradingClass}")

  finally:
    client.disconnect_and_wait()


if __name__ == "__main__":
  main()