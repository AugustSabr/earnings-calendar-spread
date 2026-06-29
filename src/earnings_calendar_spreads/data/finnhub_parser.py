from datetime import date

from earnings_calendar_spreads.core.models import EarningsEvent

def parse_finnhub_earnings_events(raw_events: list[dict]) -> list[EarningsEvent]:
  """
  Gjør rå earnings-data fra Finnhub om til EarningsEvent-objekter.

  Hopper over events som mangler symbol, dato eller report time.
  """
  earnings_events = []

  for raw_event in raw_events:
    symbol = raw_event.get("symbol")
    report_date_raw = raw_event.get("date")
    report_time = raw_event.get("hour")

    if not symbol or not report_date_raw or not report_time:
      continue

    earnings_events.append(
      EarningsEvent(
        symbol=symbol,
        report_date=date.fromisoformat(report_date_raw),
        report_time=report_time,
      )
    )

  return earnings_events