from collections import Counter
from datetime import date
from pprint import pprint

from earnings_calendar_spreads.data.finnhub_client import get_earnings_calendar
from earnings_calendar_spreads.data.finnhub_parser import parse_finnhub_earnings_events


def main():
  raw_events = get_earnings_calendar(
    start_date=date.today(),
    days_ahead=1,
  )

  hour_counts = Counter(
    event.get("hour", "<missing>") or "<empty>"
    for event in raw_events
  )

  print(f"Raw events: {len(raw_events)}")
  print(f"Hour counts: {dict(hour_counts)}")

  print("\nFirst raw event:")
  pprint(raw_events[0] if raw_events else None)

  parsed_events = parse_finnhub_earnings_events(raw_events)

  print(f"\nParsed events: {len(parsed_events)}")
  print("\nFirst parsed event:")
  pprint(parsed_events[0] if parsed_events else None)


if __name__ == "__main__":
  main()