from dotenv import load_dotenv
import os

from earnings_calendar_spreads.brokers.ibkr_connection import (
  check_ibkr_connection,
)


def main():
  load_dotenv()

  host = os.getenv("IBKR_HOST", "127.0.0.1")
  port = int(os.getenv("IBKR_PORT", "7497"))
  client_id = int(os.getenv("IBKR_CLIENT_ID", "180"))

  print(f"Connecting to IBKR at {host}:{port} with client_id={client_id}")

  next_order_id = check_ibkr_connection(
    host=host,
    port=port,
    client_id=client_id,
  )

  print("Connected successfully.")
  print(f"Next valid order id: {next_order_id}")


if __name__ == "__main__":
  main()