from datetime import date
from pprint import pprint

from earnings_calendar_spreads.workflow.screen_candidates import (
  screen_earnings_candidates,
)


def main():
  today = date.today()

  results = screen_earnings_candidates(today=today)

  qualified = [
    result
    for result in results
    if result.qualifies
  ]

  print(f"Screening results for {today}")
  print(f"Screened: {len(results)}")
  print(f"Qualified: {len(qualified)}")

  print("\nAll results:")
  for result in results:
    pprint(result)

  print("\nQualified symbols:")
  if not qualified:
    print("No qualified symbols found.")
    return

  for result in qualified:
    print(f"- {result.symbol}")


if __name__ == "__main__":
  main()