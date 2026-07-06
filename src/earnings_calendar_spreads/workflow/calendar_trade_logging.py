from pathlib import Path

from earnings_calendar_spreads.storage.trade_log import (
  DEFAULT_TRADE_LOG_PATH,
  append_trade_log_event,
  make_calendar_trade_id,
  make_trade_log_event,
)
from earnings_calendar_spreads.workflow.calendar_position_reconciliation import (
  get_current_matching_calendar_spread,
)


def log_calendar_opened_if_confirmed(
  client,
  entry,
  execution_result,
  wait_seconds: int = 3,
  path: Path = DEFAULT_TRADE_LOG_PATH,
) -> bool:
  if not execution_result.transmitted:
    return False

  final_status = execution_result.final_status

  order_status_confirms_fill = (
    final_status is not None
    and final_status.get("status") == "Filled"
  )

  matching_spread = get_current_matching_calendar_spread(
    client=client,
    short_contract=entry.short_contract,
    long_contract=entry.long_contract,
    symbol=entry.plan.symbol,
    wait_seconds=wait_seconds,
  )

  position_confirms_fill = matching_spread is not None

  if not order_status_confirms_fill and not position_confirms_fill:
    return False

  plan = entry.plan

  trade_id = make_calendar_trade_id(
    symbol=plan.symbol,
    short_expiration=plan.short_expiration,
    long_expiration=plan.long_expiration,
    strike=plan.strike,
    right=plan.right,
  )

  confirmation_source = (
    "order_status"
    if order_status_confirms_fill
    else "positions_reconciliation"
  )

  event = make_trade_log_event(
    event_type="calendar_opened",
    trade_id=trade_id,
    symbol=plan.symbol,
    data={
      "confirmation_source": confirmation_source,
      "entry_order_id": execution_result.order_id,
      "entry_order_status": (
        final_status.get("status")
        if final_status is not None
        else None
      ),
      "entry_limit_debit": plan.net_debit,
      "entry_avg_fill_price": (
        final_status.get("avg_fill_price")
        if final_status is not None
        else None
      ),
      "matched_position_quantity": (
        str(matching_spread.quantity)
        if matching_spread is not None
        else None
      ),
      "quantity": plan.quantity,
      "short_expiration": plan.short_expiration,
      "long_expiration": plan.long_expiration,
      "strike": plan.strike,
      "right": plan.right,
      "short_local_symbol": entry.short_contract.localSymbol,
      "long_local_symbol": entry.long_contract.localSymbol,
      "short_con_id": entry.short_contract.conId,
      "long_con_id": entry.long_contract.conId,
    },
  )

  append_trade_log_event(
    event=event,
    path=path,
  )

  return True