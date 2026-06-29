from datetime import date

import pandas as pd

from earnings_calendar_spreads.workflow import screen_symbol


def test_screen_symbol(monkeypatch):
  def fake_get_option_expiration_dates(symbol):
    return [
      "2026-07-03",
      "2026-08-14",
    ]

  def fake_get_option_chains(symbol, expiration_dates):
    return {
      "2026-07-03": {
        "calls": [
          {
            "strike": 100.0,
            "bid": 4.0,
            "ask": 6.0,
            "impliedVolatility": 0.70,
          }
        ],
        "puts": [
          {
            "strike": 100.0,
            "bid": 3.0,
            "ask": 5.0,
            "impliedVolatility": 0.70,
          }
        ],
      },
      "2026-08-14": {
        "calls": [
          {
            "strike": 100.0,
            "bid": 4.0,
            "ask": 6.0,
            "impliedVolatility": 0.45,
          }
        ],
        "puts": [
          {
            "strike": 100.0,
            "bid": 3.0,
            "ask": 5.0,
            "impliedVolatility": 0.45,
          }
        ],
      },
    }

  def fake_get_current_price(symbol):
    return 100.0

  def fake_get_price_history(symbol, period):
    return pd.DataFrame({
      "Open": [100.0] * 35,
      "High": [101.0] * 35,
      "Low": [99.0] * 35,
      "Close": [100.0] * 35,
      "Volume": [2_000_000] * 35,
    })

  def fake_calculate_yang_zhang_volatility(price_history):
    return 0.25

  monkeypatch.setattr(
    screen_symbol,
    "get_option_expiration_dates",
    fake_get_option_expiration_dates,
  )
  monkeypatch.setattr(
    screen_symbol,
    "get_option_chains",
    fake_get_option_chains,
  )
  monkeypatch.setattr(
    screen_symbol,
    "get_current_price",
    fake_get_current_price,
  )
  monkeypatch.setattr(
    screen_symbol,
    "get_price_history",
    fake_get_price_history,
  )
  monkeypatch.setattr(
    screen_symbol,
    "calculate_yang_zhang_volatility",
    fake_calculate_yang_zhang_volatility,
  )

  result = screen_symbol.screen_symbol(
    symbol="aapl",
    today=date(2026, 6, 29),
  )

  assert result.symbol == "AAPL"
  assert result.average_volume == 2_000_000
  assert result.iv30_rv30 > 1.25
  assert result.term_structure_slope <= -0.00406
  assert result.expected_move == "9.0%"
  assert result.qualifies