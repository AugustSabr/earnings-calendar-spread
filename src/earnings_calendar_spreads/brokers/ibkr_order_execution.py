from dataclasses import dataclass
from typing import Any

from ibapi.contract import Contract
from ibapi.order import Order


@dataclass(frozen=True)
class IBKROrderExecutionResult:
  """
  Resultat fra IBKR order submission.
  """
  order_id: int
  transmitted: bool
  initial_status: dict[str, Any] | None
  final_status: dict[str, Any] | None = None
  cancel_status: dict[str, Any] | None = None


def submit_and_manage_order(
  client,
  contract: Contract,
  order: Order,
  fill_timeout_seconds: int,
  cancel_if_not_filled: bool,
  status_timeout_seconds: int = 10,
) -> IBKROrderExecutionResult:
  """
  Sender ordre til TWS og håndterer wait/cancel.

  Hvis order.transmit=False:
    - sender staged/untransmitted order
    - venter ikke på fill

  Hvis order.transmit=True:
    - venter på Filled/Cancelled/Inactive
    - canceller hvis ikke fylt og cancel_if_not_filled=True
  """
  order_id = client.place_order(
    contract=contract,
    order=order,
    wait_for_status=True,
    timeout=status_timeout_seconds,
  )

  initial_status = client.order_status_by_id.get(order_id)

  if not order.transmit:
    return IBKROrderExecutionResult(
      order_id=order_id,
      transmitted=False,
      initial_status=initial_status,
    )

  final_status = client.wait_for_order_status(
    order_id=order_id,
    target_statuses={
      "Filled",
      "Cancelled",
      "Inactive",
    },
    timeout=fill_timeout_seconds,
  )

  cancel_status = None

  if (
    cancel_if_not_filled
    and (
      final_status is None
      or final_status["status"] != "Filled"
    )
  ):
    client.cancel_order(order_id)

    cancel_status = client.wait_for_order_status(
      order_id=order_id,
      target_statuses={
        "Cancelled",
        "Inactive",
        "Filled",
      },
      timeout=status_timeout_seconds,
    )

  return IBKROrderExecutionResult(
    order_id=order_id,
    transmitted=True,
    initial_status=initial_status,
    final_status=final_status,
    cancel_status=cancel_status,
  )