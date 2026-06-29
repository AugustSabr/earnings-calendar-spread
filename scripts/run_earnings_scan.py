from datetime import date

from earnings_calendar_spreads.workflows.earnings_scan import scan_earnings_candidates


def main():
  today = date.today()

  candidates = scan_earnings_candidates(today=today)

  print(f"Earnings candidates for {today}:")
  if not candidates:
    print("No candidates found.")
    return

  for symbol in candidates:
    print(f"- {symbol}")


if __name__ == "__main__":
  main()