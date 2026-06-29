import pytest

from earnings_calendar_spreads.core.option_chain import find_nearest_strike_option
from earnings_calendar_spreads.core.option_chain import calculate_atm_iv

def test_finds_option_with_strike_nearest_underlying_price():
  options = [
    {"strike": 95.0, "impliedVolatility": 0.40},
    {"strike": 100.0, "impliedVolatility": 0.35},
    {"strike": 105.0, "impliedVolatility": 0.38},
  ]

  result = find_nearest_strike_option(
    options=options,
    underlying_price=101.0,
  )

  assert result == {"strike": 100.0, "impliedVolatility": 0.35}

def test_raises_error_when_no_options_are_provided():
  with pytest.raises(ValueError):
    find_nearest_strike_option(
      options=[],
      underlying_price=100.0,
    )

def test_calculates_atm_iv_from_nearest_call_and_put():
  calls = [
    {"strike": 95.0, "impliedVolatility": 0.40},
    {"strike": 100.0, "impliedVolatility": 0.30},
  ]

  puts = [
    {"strike": 100.0, "impliedVolatility": 0.50},
    {"strike": 105.0, "impliedVolatility": 0.60},
  ]

  result = calculate_atm_iv(
    calls=calls,
    puts=puts,
    underlying_price=101.0,
  )

  assert result == 0.40