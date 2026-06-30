import os
from decimal import Decimal

from dotenv import load_dotenv

from earnings_calendar_spreads.brokers.ibkr_client import IBKRClient


def print_position(position):
  contract = position.contract

  print()
  print(f"{contract.symbol} {contract.secType}")
  print(f"account: {position.account}")
  print(f"position: {position.position}")
  print(f"average_cost: {position.average_cost}")
  print(f"conId: {contract.conId}")
  print(f"localSymbol: {contract.localSymbol}")
  print(f"exchange: {contract.exchange}")
  print(f"currency: {contract.currency}")

  if contract.secType == "OPT":
    print(f"expiration: {contract.lastTradeDateOrContractMonth}")
    print(f"strike: {contract.strike}")
    print(f"right: {contract.right}")
    print(f"multiplier: {contract.multiplier}")
    print(f"tradingClass: {contract.tradingClass}")


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

    open_positions = [
      position
      for position in positions
      if position.position != Decimal("0")
    ]

    print(f"Open positions: {len(open_positions)}")

    for position in open_positions:
      print_position(position)

  finally:
    client.disconnect_and_wait()


if __name__ == "__main__":
  main()