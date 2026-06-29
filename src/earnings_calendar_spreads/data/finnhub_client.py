from datetime import date, timedelta

import finnhub

from earnings_calendar_spreads.config import get_finnhub_api_key


def get_earnings_calendar(
  start_date: date,
  days_ahead: int = 1,
) -> list[dict]:
  """
  Henter earnings calendar fra Finnhub.

  Returnerer rå dictionaries fra Finnhub API-et.
  """
  api_key = get_finnhub_api_key()
  client = finnhub.Client(api_key=api_key)

  end_date = start_date + timedelta(days=days_ahead)

  response = client.earnings_calendar(
    _from=start_date.isoformat(),
    to=end_date.isoformat(),
    symbol="",
    international=False,
  )

  return response.get("earningsCalendar", [])