from datetime import date, timedelta


def filter_actionable_earnings(
  earnings: list[dict],
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

  for item in earnings:
    symbol = item.get("symbol")
    earnings_date = item.get("date")
    hour = item.get("hour", "").lower()

    if not symbol:
      continue

    if earnings_date == today.isoformat() and hour == "amc":
      today_after_close.append(symbol)

    if earnings_date == tomorrow.isoformat() and hour == "bmo":
      tomorrow_before_open.append(symbol)

  return {
    "today_after_close": today_after_close,
    "tomorrow_before_open": tomorrow_before_open,
  }