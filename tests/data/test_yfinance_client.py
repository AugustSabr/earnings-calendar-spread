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

  def option_chain(self, expiration_date: str):
    return FakeOptionChain()

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

def test_get_price_history(monkeypatch):
  monkeypatch.setattr(yfinance_client.yf, "Ticker", FakeTicker)

  result = yfinance_client.get_price_history("AAPL")

  assert not result.empty
  assert result["Close"].iloc[-1] == 123.45

def test_get_price_history_raises_error_when_missing(monkeypatch):
  monkeypatch.setattr(yfinance_client.yf, "Ticker", FakeTickerWithoutData)

  with pytest.raises(ValueError):
    yfinance_client.get_price_history("AAPL")

class FakeOptionChain:
  def __init__(self):
    self.calls = pd.DataFrame([
      {
        "strike": 100.0,
        "bid": 4.0,
        "ask": 6.0,
        "impliedVolatility": 0.30,
      }
    ])

    self.puts = pd.DataFrame([
      {
        "strike": 100.0,
        "bid": 3.0,
        "ask": 5.0,
        "impliedVolatility": 0.50,
      }
    ])

def test_get_option_chain(monkeypatch):
  monkeypatch.setattr(yfinance_client.yf, "Ticker", FakeTicker)

  result = yfinance_client.get_option_chain(
    symbol="AAPL",
    expiration_date="2026-07-03",
  )

  assert result == {
    "calls": [
      {
        "strike": 100.0,
        "bid": 4.0,
        "ask": 6.0,
        "impliedVolatility": 0.30,
      }
    ],
    "puts": [
      {
        "strike": 100.0,
        "bid": 3.0,
        "ask": 5.0,
        "impliedVolatility": 0.50,
      }
    ],
  }

def test_get_option_chains(monkeypatch):
  monkeypatch.setattr(yfinance_client.yf, "Ticker", FakeTicker)

  result = yfinance_client.get_option_chains(
    symbol="AAPL",
    expiration_dates=[
      "2026-07-03",
      "2026-07-10",
    ],
  )

  assert list(result.keys()) == [
    "2026-07-03",
    "2026-07-10",
  ]