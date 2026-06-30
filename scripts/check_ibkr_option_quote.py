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

    generic_contract = make_option_contract(
      symbol=symbol,
      expiration=expiration,
      strike=strike,
      right=right,
    )

    details = client.get_contract_details(generic_contract)

    if not details:
      raise ValueError("No contract details found.")

    resolved_contract = details[0].contract

    print(f"{resolved_contract.localSymbol}")

    try:
      bid, ask = client.get_bid_ask(
        contract=resolved_contract,
        req_id=100,
        timeout=10,
      )

      print(f"Bid: {bid}")
      print(f"Ask: {ask}")

    except TimeoutError as error:
      print("No valid bid/ask received.")
      print(f"Reason: {error}")

  finally:
    client.disconnect_and_wait()


if __name__ == "__main__":
  main()