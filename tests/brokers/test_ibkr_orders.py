import pytest

from earnings_calendar_spreads.brokers.ibkr_orders import (
  build_calendar_spread_limit_order,
)


def test_build_calendar_spread_limit_order():
  order = build_calendar_spread_limit_order(
    net_debit=1.23,
    quantity=2,
    transmit=False,
  )

  assert order.action == "BUY"
  assert order.orderType == "LMT"
  assert order.totalQuantity == 2
  assert order.lmtPrice == 1.23
  assert order.transmit is False


def test_build_calendar_spread_limit_order_can_transmit():
  order = build_calendar_spread_limit_order(
    net_debit=1.23,
    quantity=1,
    transmit=True,
  )

  assert order.transmit is True


def test_build_calendar_spread_limit_order_requires_positive_quantity():
  with pytest.raises(ValueError, match="quantity"):
    build_calendar_spread_limit_order(
      net_debit=1.23,
      quantity=0,
    )


def test_build_calendar_spread_limit_order_requires_positive_net_debit():
  with pytest.raises(ValueError, match="net_debit"):
    build_calendar_spread_limit_order(
      net_debit=0,
      quantity=1,
    )