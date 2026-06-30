from datetime import date

from earnings_calendar_spreads.brokers.ibkr_calendar_plan import (
  build_calendar_spread_plan_from_ibkr_chain,
)
from earnings_calendar_spreads.brokers.ibkr_option_chain import (
  IBKROptionChainParameters,
)


def test_build_calendar_spread_plan_from_ibkr_chain():
  parameters = [
    IBKROptionChainParameters(
      exchange="CBOE",
      underlying_con_id=1,
      trading_class="AAPL",
      multiplier="100",
      expirations=[
        "20260703",
        "20260717",
        "20260821",
      ],
      strikes=[
        290.0,
        300.0,
        310.0,
      ],
    ),
    IBKROptionChainParameters(
      exchange="SMART",
      underlying_con_id=1,
      trading_class="AAPL",
      multiplier="100",
      expirations=[
        "20260703",
        "20260717",
        "20260821",
      ],
      strikes=[
        290.0,
        300.0,
        310.0,
      ],
    ),
  ]

  plan = build_calendar_spread_plan_from_ibkr_chain(
    symbol="aapl",
    parameters=parameters,
    entry_date=date(2026, 7, 1),
    earnings_date=date(2026, 7, 2),
    underlying_price=303.0,
    right="c",
    quantity=2,
  )

  assert plan.symbol == "AAPL"
  assert plan.short_expiration == "2026-07-03"
  assert plan.long_expiration == "2026-08-21"
  assert plan.strike == 300.0
  assert plan.right == "C"
  assert plan.quantity == 2
  assert plan.net_debit is None