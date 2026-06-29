import sys
from datetime import date
from pprint import pprint

from earnings_calendar_spreads.workflow.screen_symbol import screen_symbol


def main():
  symbol = sys.argv[1] if len(sys.argv) > 1 else "AAPL"

  result = screen_symbol(
    symbol=symbol,
    today=date.today(),
  )

  pprint(result)


if __name__ == "__main__":
  main()