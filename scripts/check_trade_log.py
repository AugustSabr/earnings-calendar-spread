from collections import defaultdict

from earnings_calendar_spreads.storage.trade_log import (
  get_open_trade_events,
  read_trade_log_events,
)


def main():
  events = read_trade_log_events()

  if not events:
    print("No trade log events found.")
    return

  events_by_trade_id = defaultdict(list)

  for event in events:
    events_by_trade_id[event.trade_id].append(event)

  open_trade_events = get_open_trade_events(events)
  open_trade_ids = {
    event.trade_id
    for event in open_trade_events
  }

  print(f"Total events: {len(events)}")
  print(f"Total trades: {len(events_by_trade_id)}")
  print(f"Open trades: {len(open_trade_ids)}")
  print()

  for trade_id, trade_events in events_by_trade_id.items():
    opened_count = sum(
      1
      for event in trade_events
      if event.event_type == "calendar_opened"
    )
    closed_count = sum(
      1
      for event in trade_events
      if event.event_type == "calendar_closed"
    )

    latest_event = trade_events[-1]
    status = "OPEN" if trade_id in open_trade_ids else "CLOSED"

    warnings = []

    if opened_count == 0 and closed_count > 0:
      warnings.append("orphan close")

    if opened_count > 1 and closed_count == 0:
      warnings.append("duplicate open")

    if closed_count > opened_count:
      warnings.append("more closes than opens")

    print(f"{latest_event.symbol} {status}")
    print(f"  trade_id: {trade_id}")
    print(f"  opened_events: {opened_count}")
    print(f"  closed_events: {closed_count}")

    if warnings:
      print(f"  warnings: {', '.join(warnings)}")

    print()


if __name__ == "__main__":
  main()