from ibapi.contract import Contract
from ibapi.order import Order

from earnings_calendar_spreads.brokers.ibkr_order_execution import (
  submit_and_manage_order,
)


class FakeClient:
  def __init__(self):
    self.order_status_by_id = {}
    self.cancelled_order_id = None

  def place_order(
    self,
    contract,
    order,
    wait_for_status=True,
    timeout=10,
  ):
    self.order_status_by_id[1] = {
      "status": "PreSubmitted",
      "filled": 0,
      "remaining": order.totalQuantity,
    }

    return 1

  def wait_for_order_status(
    self,
    order_id,
    target_statuses,
    timeout=30,
  ):
    return self.order_status_by_id.get(order_id)

  def cancel_order(self, order_id):
    self.cancelled_order_id = order_id
    self.order_status_by_id[order_id] = {
      "status": "Cancelled",
      "filled": 0,
      "remaining": 1,
    }


def make_order(transmit: bool) -> Order:
  order = Order()
  order.action = "BUY"
  order.orderType = "LMT"
  order.totalQuantity = 1
  order.lmtPrice = 1.0
  order.transmit = transmit
  return order


def test_submit_and_manage_order_does_not_wait_for_untransmitted_order():
  client = FakeClient()

  result = submit_and_manage_order(
    client=client,
    contract=Contract(),
    order=make_order(transmit=False),
    fill_timeout_seconds=30,
    cancel_if_not_filled=True,
  )

  assert result.order_id == 1
  assert result.transmitted is False
  assert result.initial_status["status"] == "PreSubmitted"
  assert result.final_status is None
  assert result.cancel_status is None
  assert client.cancelled_order_id is None


def test_submit_and_manage_order_cancels_unfilled_transmitted_order():
  client = FakeClient()

  result = submit_and_manage_order(
    client=client,
    contract=Contract(),
    order=make_order(transmit=True),
    fill_timeout_seconds=30,
    cancel_if_not_filled=True,
  )

  assert result.order_id == 1
  assert result.transmitted is True
  assert result.initial_status["status"] == "PreSubmitted"
  assert result.final_status["status"] == "PreSubmitted"
  assert result.cancel_status["status"] == "Cancelled"
  assert client.cancelled_order_id == 1