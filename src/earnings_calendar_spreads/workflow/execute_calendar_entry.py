from dataclasses import dataclass
from datetime import date

from earnings_calendar_spreads.brokers.ibkr_order_execution import (
  IBKROrderExecutionResult,
  submit_and_manage_order,
)
from earnings_calendar_spreads.core.order_policy import EntryOrderPolicy
from earnings_calendar_spreads.workflow.prepare_calendar_entry import (
  PreparedCalendarEntry,
  prepare_calendar_entry,
)


@dataclass(frozen=True)
class CalendarEntryExecution:
  """
  Resultat fra forberedt og eventuelt sendt calendar entry.
  """
  prepared_entry: PreparedCalendarEntry
  execution_result: IBKROrderExecutionResult


def execute_calendar_entry(
  client,
  symbol: str,
  earnings_date: date,
  policy: EntryOrderPolicy,
  primary_exchange: str | None = None,
  right: str = "C",
  quantity: int = 1,
  transmit: bool = False,
  max_debit_per_symbol_usd: float | None = None,
) -> CalendarEntryExecution:
  """
  Forbereder og sender/stager en calendar entry.
  """
  prepared_entry = prepare_calendar_entry(
    client=client,
    symbol=symbol,
    earnings_date=earnings_date,
    primary_exchange=primary_exchange,
    right=right,
    quantity=quantity,
    transmit=transmit,
    max_debit_per_symbol_usd=max_debit_per_symbol_usd,
  )

  execution_result = submit_and_manage_order(
    client=client,
    contract=prepared_entry.bag_contract,
    order=prepared_entry.order,
    fill_timeout_seconds=policy.fill_timeout_seconds,
    cancel_if_not_filled=policy.cancel_if_not_filled,
  )

  return CalendarEntryExecution(
    prepared_entry=prepared_entry,
    execution_result=execution_result,
  )