from datetime import date

from earnings_calendar_spreads.workflow import earnings_scan


def test_scan_earnings_candidates(monkeypatch):
  def fake_get_earnings_calendar(start_date, days_ahead):
    return [
      {"symbol": "aapl", "date": "2026-06-29", "hour": "amc"},
      {"symbol": "MSFT", "date": "2026-06-30", "hour": "bmo"},
      {"symbol": "BRK.B", "date": "2026-06-29", "hour": "amc"},
      {"symbol": "NVDA", "date": "2026-06-29", "hour": ""},
    ]

  monkeypatch.setattr(
    earnings_scan,
    "get_earnings_calendar",
    fake_get_earnings_calendar,
  )

  result = earnings_scan.scan_earnings_candidates(
    today=date(2026, 6, 29),
  )

  assert result == ["AAPL", "MSFT"]