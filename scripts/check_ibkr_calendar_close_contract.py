import os
import sys

from dotenv import load_dotenv

from earnings_calendar_spreads.brokers.ibkr_calendar_positions import (
  find_calendar_spread_positions,
)
from earnings_calendar_spreads.brokers.ibkr_calendar_spread import (
  build_calendar_spread_close_contract,
)
from earnings_calendar_spreads.brokers.ibkr_client import IBKRClient


def print_combo_contract(contract):
  print()
  print("Calendar close BAG contract")
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
      raise ValueError(f"No calendar spread positions found for {symbol}.")

    spread = spreads[0]

    short_contract = spread.short_position.contract
    long_contract = spread.long_position.contract

    close_contract = build_calendar_spread_close_contract(
      symbol=spread.symbol,
      short_option_contract=short_contract,
      long_option_contract=long_contract,
    )

    print(f"Close contract for {spread.symbol} calendar spread")
    print(f"quantity: {spread.quantity}")

    print()
    print("Current position")
    print(f"short/front: {spread.short_position.position} {short_contract.localSymbol}")
    print(f"long/back: {spread.long_position.position} {long_contract.localSymbol}")

    print_combo_contract(close_contract)

  finally:
    client.disconnect_and_wait()


if __name__ == "__main__":
  main()