from dataclasses import dataclass

from earnings_calendar_spreads.brokers.ibkr_order_execution import (
  IBKROrderExecutionResult,
  submit_and_manage_order,
)
from earnings_calendar_spreads.core.order_policy import ExitOrderPolicy
from earnings_calendar_spreads.workflow.prepare_calendar_exit import (
  PreparedCalendarExit,
  prepare_calendar_exit,
)


@dataclass(frozen=True)
class CalendarExitExecution:
  """
  Resultat fra forberedt og eventuelt sendt calendar exit.
  """
  prepared_exit: PreparedCalendarExit | None
  execution_result: IBKROrderExecutionResult | None


def execute_calendar_exit(
  client,
  symbol: str,
  policy: ExitOrderPolicy,
  transmit: bool = False,
  limit_credit_override: float | None = None,
) -> CalendarExitExecution:
  """
  Forbereder og sender/stager en calendar exit.

  Returnerer None-felter hvis ingen matching calendar spread finnes.
  """
  prepared_exit = prepare_calendar_exit(
    client=client,
    symbol=symbol,
    transmit=transmit,
  )

  if prepared_exit is None:
    return CalendarExitExecution(
      prepared_exit=None,
      execution_result=None,
    )

  if limit_credit_override is not None:
    prepared_exit.order.lmtPrice = round(limit_credit_override, 2)

  execution_result = submit_and_manage_order(
    client=client,
    contract=prepared_exit.bag_contract,
    order=prepared_exit.order,
    fill_timeout_seconds=policy.fill_timeout_seconds,
    cancel_if_not_filled=policy.cancel_if_not_filled,
  )

  return CalendarExitExecution(
    prepared_exit=prepared_exit,
    execution_result=execution_result,
  )