import os
import sys
from datetime import date

from dotenv import load_dotenv

from earnings_calendar_spreads.brokers.ibkr_client import IBKRClient
from earnings_calendar_spreads.core.order_policy import EntryOrderPolicy
from earnings_calendar_spreads.workflow.prepare_calendar_entry import (
  prepare_calendar_entry,
)
from earnings_calendar_spreads.workflow.execute_calendar_entry import (
  execute_calendar_entry,
)
from earnings_calendar_spreads.workflow.screen_candidates import (
  screen_earnings_candidate_events,
)
from earnings_calendar_spreads.workflow.trading_pause import (
  is_trading_paused,
)


def print_prepared_entry(entry):
  plan = entry.plan
  order = entry.order

  print()
  print(f"Prepared calendar entry for {plan.symbol}")
  print(f"Underlying price: {entry.underlying_price}")
  print(f"Short expiration: {plan.short_expiration}")
  print(f"Long expiration: {plan.long_expiration}")
  print(f"Strike: {plan.strike}")
  print(f"Right: {plan.right}")
  print(f"Quantity: {plan.quantity}")
  print(f"Net debit: {plan.net_debit}")

  print()
  print("Order")
  print(f"action: {order.action}")
  print(f"orderType: {order.orderType}")
  print(f"totalQuantity: {order.totalQuantity}")
  print(f"lmtPrice: {order.lmtPrice}")
  print(f"transmit: {order.transmit}")


def print_execution_result(result):
  print()
  print("Submitted to TWS")
  print(f"order_id: {result.order_id}")
  print(f"transmit: {result.transmitted}")
  print(f"initial_status: {result.initial_status}")

  if result.final_status is not None:
    print()
    print("Final/latest status after wait")
    print(result.final_status)

  if result.cancel_status is not None:
    print()
    print("Status after cancel attempt")
    print(result.cancel_status)


def main():
  load_dotenv()

  today = date.today()
  should_stage = "--stage" in sys.argv
  should_transmit = "--transmit" in sys.argv

  if should_stage and should_transmit:
    raise ValueError("Use either --stage or --transmit, not both.")

  mode = "prepare-only"

  if should_stage:
    mode = "stage"

  if should_transmit:
    mode = "transmit"

  print(f"Qualified calendar entry runner for {today}")
  print(f"Mode: {mode}")
  print()

  if is_trading_paused():
    print("Trading is paused. Skipping new calendar entries.")
    return

  candidates = screen_earnings_candidate_events(
    today=today,
  )

  qualified = [
    candidate
    for candidate in candidates
    if candidate.screening_result.qualifies
  ]

  print(f"Screened: {len(candidates)}")
  print(f"Qualified: {len(qualified)}")

  if not qualified:
    print("No qualified candidates found.")
    return

  host = os.getenv("IBKR_HOST", "127.0.0.1")
  port = int(os.getenv("IBKR_PORT", "7497"))
  client_id = int(os.getenv("IBKR_CLIENT_ID", "180"))

  policy = EntryOrderPolicy()
  client = IBKRClient()

  try:
    client.connect_and_start(
      host=host,
      port=port,
      client_id=client_id,
    )

    for candidate in qualified:
      event = candidate.earnings_event
      result = candidate.screening_result

      print()
      print("=" * 72)
      print(f"{result.symbol} qualifies")
      print(f"earnings_date: {event.report_date}")
      print(f"expected_move: {result.expected_move}")
      print("=" * 72)

      if mode == "prepare-only":
        entry = prepare_calendar_entry(
          client=client,
          symbol=result.symbol,
          earnings_date=event.report_date,
          primary_exchange=None,
          transmit=False,
        )

        print_prepared_entry(entry)
        continue

      execution = execute_calendar_entry(
        client=client,
        symbol=result.symbol,
        earnings_date=event.report_date,
        policy=policy,
        primary_exchange=None,
        transmit=should_transmit,
      )

      print_prepared_entry(execution.prepared_entry)
      print_execution_result(execution.execution_result)

  finally:
    client.disconnect_and_wait()


if __name__ == "__main__":
  main()