from earnings_calendar_spreads.brokers.ibkr_client import (
  select_underlying_price_from_ticks,
)


def test_select_underlying_price_prefers_bid_ask_mid():
  price = select_underlying_price_from_ticks(
    {
      "bid": 100.0,
      "ask": 102.0,
      "last": 99.0,
    }
  )

  assert price == 101.0


def test_select_underlying_price_uses_last_when_bid_ask_missing():
  price = select_underlying_price_from_ticks(
    {
      "last": 293.58,
    }
  )

  assert price == 293.58


def test_select_underlying_price_uses_delayed_bid_ask():
  price = select_underlying_price_from_ticks(
    {
      "delayed_bid": 100.0,
      "delayed_ask": 101.0,
    }
  )

  assert price == 100.5


def test_select_underlying_price_returns_none_without_usable_ticks():
  price = select_underlying_price_from_ticks({})

  assert price is None