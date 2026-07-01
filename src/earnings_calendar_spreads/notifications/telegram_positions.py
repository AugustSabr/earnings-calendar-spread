from decimal import Decimal

from earnings_calendar_spreads.brokers.ibkr_calendar_positions import (
  IBKRCalendarSpreadPosition,
)


def format_decimal(value) -> str:
  if isinstance(value, Decimal):
    return str(value.normalize())

  return str(value)


def format_calendar_spread_position(
  spread: IBKRCalendarSpreadPosition,
) -> str:
  short_contract = spread.short_position.contract
  long_contract = spread.long_position.contract

  return "\n".join(
    [
      f"{spread.symbol} calendar spread",
      f"Qty: {format_decimal(spread.quantity)}",
      "",
      "Short/front:",
      f"{short_contract.localSymbol}",
      f"Position: {format_decimal(spread.short_position.position)}",
      f"Avg cost: {spread.short_position.average_cost}",
      "",
      "Long/back:",
      f"{long_contract.localSymbol}",
      f"Position: {format_decimal(spread.long_position.position)}",
      f"Avg cost: {spread.long_position.average_cost}",
    ]
  )


def format_calendar_spread_positions(
  spreads: list[IBKRCalendarSpreadPosition],
) -> str:
  if not spreads:
    return "No open calendar spread positions."

  messages = [
    f"Open calendar spreads: {len(spreads)}",
  ]

  for spread in spreads:
    messages.append("")
    messages.append(format_calendar_spread_position(spread))

  return "\n".join(messages)