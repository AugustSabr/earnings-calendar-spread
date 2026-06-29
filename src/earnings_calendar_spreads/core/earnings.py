from datetime import date, timedelta

from earnings_calendar_spreads.core.models import EarningsEvent


def filter_actionable_earnings(
  earnings: list[EarningsEvent],
  today: date,
) -> dict[str, list[str]]:
  """
  Finner earnings som er relevante for neste mulige earnings-trade.

  Tar med:
  - selskaper som rapporterer i dag etter close
  - selskaper som rapporterer i morgen før open
  """

  tomorrow = today + timedelta(days=1)

  today_after_close = []
  tomorrow_before_open = []

  for event in earnings:
    report_time = event.report_time.lower()

    if event.report_date == today and report_time == "amc":
      today_after_close.append(event.symbol)

    if event.report_date == tomorrow and report_time == "bmo":
      tomorrow_before_open.append(event.symbol)

  return {
    "today_after_close": today_after_close,
    "tomorrow_before_open": tomorrow_before_open,
  }