import sys
from pprint import pprint

import yfinance as yf


def main():
  symbol = sys.argv[1] if len(sys.argv) > 1 else "AAPL"

  ticker = yf.Ticker(symbol)

  history = ticker.history(period="1d")
  options = list(ticker.options)

  print(f"Symbol: {symbol}")
  print(f"Price rows: {len(history)}")
  print(f"Options expirations: {len(options)}")

  if not history.empty:
    print(f"Last close: {history['Close'].iloc[-1]}")

  print("\nFirst expirations:")
  pprint(options[:5])

  if not options:
    return

  first_expiry = options[0]
  chain = ticker.option_chain(first_expiry)

  print(f"\nFirst expiry: {first_expiry}")
  print(f"Calls: {len(chain.calls)}")
  print(f"Puts: {len(chain.puts)}")

  print("\nFirst call row:")
  pprint(chain.calls.iloc[0].to_dict() if not chain.calls.empty else None)


if __name__ == "__main__":
  main()