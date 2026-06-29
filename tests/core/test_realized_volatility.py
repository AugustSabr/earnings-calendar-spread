import pandas as pd
import pytest

from earnings_calendar_spreads.core.realized_volatility import (
  calculate_yang_zhang_volatility,
)


def test_yang_zhang_returns_zero_for_flat_prices():
  price_data = pd.DataFrame({
    "Open": [100.0] * 35,
    "High": [100.0] * 35,
    "Low": [100.0] * 35,
    "Close": [100.0] * 35,
  })

  result = calculate_yang_zhang_volatility(price_data)

  assert result == pytest.approx(0.0)


def test_yang_zhang_returns_last_value_by_default():
  price_data = pd.DataFrame({
    "Open": [100 + i for i in range(35)],
    "High": [101 + i for i in range(35)],
    "Low": [99 + i for i in range(35)],
    "Close": [100.5 + i for i in range(35)],
  })

  full_series = calculate_yang_zhang_volatility(
    price_data,
    return_last_only=False,
  )

  last_value = calculate_yang_zhang_volatility(price_data)

  assert last_value == full_series.iloc[-1]
  assert last_value > 0