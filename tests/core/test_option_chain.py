import pytest

from earnings_calendar_spreads.core.option_chain import find_nearest_strike_option
from earnings_calendar_spreads.core.option_chain import calculate_atm_iv
from earnings_calendar_spreads.core.option_chain import calculate_atm_iv_by_expiration
from earnings_calendar_spreads.core.option_chain import calculate_expected_move
from earnings_calendar_spreads.core.option_chain import calculate_mid_price

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

def test_calculates_atm_iv_by_expiration():
  option_chains = {
    "2026-07-03": {
      "calls": [
        {"strike": 100.0, "impliedVolatility": 0.30},
      ],
      "puts": [
        {"strike": 100.0, "impliedVolatility": 0.50},
      ],
    },
    "2026-07-10": {
      "calls": [
        {"strike": 100.0, "impliedVolatility": 0.40},
      ],
      "puts": [
        {"strike": 100.0, "impliedVolatility": 0.60},
      ],
    },
  }

  result = calculate_atm_iv_by_expiration(
    option_chains=option_chains,
    underlying_price=101.0,
  )

  assert result == {
    "2026-07-03": 0.40,
    "2026-07-10": 0.50,
  }

def test_skips_expiration_when_calls_or_puts_are_missing():
  option_chains = {
    "2026-07-03": {
      "calls": [],
      "puts": [
        {"strike": 100.0, "impliedVolatility": 0.50},
      ],
    },
  }

  result = calculate_atm_iv_by_expiration(
    option_chains=option_chains,
    underlying_price=101.0,
  )

  assert result == {}

def test_calculates_mid_price():
  option = {
    "bid": 2.0,
    "ask": 3.0,
  }

  result = calculate_mid_price(option)

  assert result == 2.5

def test_mid_price_is_none_when_bid_or_ask_is_missing():
  assert calculate_mid_price({"bid": 2.0}) is None
  assert calculate_mid_price({"ask": 3.0}) is None
  assert calculate_mid_price({"bid": 0.0, "ask": 3.0}) is None

def test_calculates_expected_move_from_atm_straddle():
  calls = [
    {
      "strike": 100.0,
      "bid": 4.0,
      "ask": 6.0,
    },
  ]

  puts = [
    {
      "strike": 100.0,
      "bid": 3.0,
      "ask": 5.0,
    },
  ]

  result = calculate_expected_move(
    calls=calls,
    puts=puts,
    underlying_price=100.0,
  )

  assert result == "9.0%"

def test_expected_move_is_none_when_mid_price_is_missing():
  calls = [
    {
      "strike": 100.0,
      "bid": 0.0,
      "ask": 6.0,
    },
  ]

  puts = [
    {
      "strike": 100.0,
      "bid": 3.0,
      "ask": 5.0,
    },
  ]

  result = calculate_expected_move(
    calls=calls,
    puts=puts,
    underlying_price=100.0,
  )

  assert result is None