import os

from dotenv import load_dotenv

from earnings_calendar_spreads.brokers.ibkr_calendar_positions import (
  find_calendar_spread_positions,
)
from earnings_calendar_spreads.brokers.ibkr_client import IBKRClient


def print_calendar_spread(spread):
  short_contract = spread.short_position.contract
  long_contract = spread.long_position.contract

  print()
  print(f"{spread.symbol} calendar spread")
  print(f"quantity: {spread.quantity}")

  print()
  print("Short/front leg")
  print(f"position: {spread.short_position.position}")
  print(f"localSymbol: {short_contract.localSymbol}")
  print(f"conId: {short_contract.conId}")
  print(f"expiration: {short_contract.lastTradeDateOrContractMonth}")
  print(f"strike: {short_contract.strike}")
  print(f"right: {short_contract.right}")

  print()
  print("Long/back leg")
  print(f"position: {spread.long_position.position}")
  print(f"localSymbol: {long_contract.localSymbol}")
  print(f"conId: {long_contract.conId}")
  print(f"expiration: {long_contract.lastTradeDateOrContractMonth}")
  print(f"strike: {long_contract.strike}")
  print(f"right: {long_contract.right}")


def main():
  load_dotenv()

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
    )

    print(f"Calendar spreads found: {len(spreads)}")

    for spread in spreads:
      print_calendar_spread(spread)

  finally:
    client.disconnect_and_wait()


if __name__ == "__main__":
  main()