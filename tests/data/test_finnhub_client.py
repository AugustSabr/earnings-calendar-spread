from datetime import date

from earnings_calendar_spreads.data import finnhub_client


class FakeFinnhubClient:
  def __init__(self, api_key: str):
    self.api_key = api_key

  def earnings_calendar(self, _from, to, symbol, international):
    return {
      "earningsCalendar": [
        {
          "symbol": "AAPL",
          "date": _from,
          "hour": "amc",
        }
      ]
    }


def test_get_earnings_calendar(monkeypatch):
  monkeypatch.setenv("FINNHUB_API_KEY", "test-key")
  monkeypatch.setattr(finnhub_client.finnhub, "Client", FakeFinnhubClient)

  result = finnhub_client.get_earnings_calendar(
    start_date=date(2026, 6, 29),
    days_ahead=1,
  )

  assert result == [
    {
      "symbol": "AAPL",
      "date": "2026-06-29",
      "hour": "amc",
    }
  ]