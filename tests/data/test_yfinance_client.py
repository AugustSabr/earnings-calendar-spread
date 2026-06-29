import pandas as pd
import pytest

from earnings_calendar_spreads.data import yfinance_client


class FakeTicker:
  def __init__(self, symbol: str):
    self.symbol = symbol
    self.options = [
      "2026-07-03",
      "2026-07-10",
    ]

  def history(self, period: str):
    return pd.DataFrame({
      "Close": [123.45],
    })

class FakeTickerWithoutData:
  def __init__(self, symbol: str):
    self.symbol = symbol
    self.options = []

  def history(self, period: str):
    return pd.DataFrame()

def test_get_current_price(monkeypatch):
  monkeypatch.setattr(yfinance_client.yf, "Ticker", FakeTicker)

  result = yfinance_client.get_current_price("AAPL")

  assert result == 123.45

def test_get_current_price_raises_error_when_missing(monkeypatch):
  monkeypatch.setattr(yfinance_client.yf, "Ticker", FakeTickerWithoutData)

  with pytest.raises(ValueError):
    yfinance_client.get_current_price("AAPL")

def test_get_option_expiration_dates(monkeypatch):
  monkeypatch.setattr(yfinance_client.yf, "Ticker", FakeTicker)

  result = yfinance_client.get_option_expiration_dates("AAPL")

  assert result == [
    "2026-07-03",
    "2026-07-10",
  ]

def test_get_option_expiration_dates_raises_error_when_missing(monkeypatch):
  monkeypatch.setattr(yfinance_client.yf, "Ticker", FakeTickerWithoutData)

  with pytest.raises(ValueError):
    yfinance_client.get_option_expiration_dates("AAPL")