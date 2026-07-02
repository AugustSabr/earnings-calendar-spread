from earnings_calendar_spreads.core.money import format_usd
from earnings_calendar_spreads.core.position_sizing import (
  calculate_calendar_spread_debit_usd,
)
from earnings_calendar_spreads.storage.trade_log import TradeLogEvent


def parse_float(value) -> float | None:
  if value is None:
    return None

  try:
    return float(value)
  except (TypeError, ValueError):
    return None


def parse_int(value) -> int | None:
  if value is None:
    return None

  try:
    return int(value)
  except (TypeError, ValueError):
    return None


def format_open_trade_event(event: TradeLogEvent) -> str:
  data = event.data

  quantity = parse_int(data.get("quantity"))
  entry_limit_debit = parse_float(data.get("entry_limit_debit"))

  lines = [
    f"{event.symbol} calendar spread",
    f"Qty: {quantity if quantity is not None else 'unknown'}",
  ]

  if entry_limit_debit is not None:
    lines.append(f"Entry debit quote: {format_usd(entry_limit_debit)}")

  if entry_limit_debit is not None and quantity is not None:
    estimated_total_debit = calculate_calendar_spread_debit_usd(
      quoted_debit=entry_limit_debit,
      quantity=quantity,
    )

    lines.append(
      f"Estimated total debit: {format_usd(estimated_total_debit)}"
    )

  short_local_symbol = data.get("short_local_symbol")
  long_local_symbol = data.get("long_local_symbol")

  if short_local_symbol is not None:
    lines.append(f"Short/front: {short_local_symbol}")

  if long_local_symbol is not None:
    lines.append(f"Long/back: {long_local_symbol}")

  lines.append(f"Trade ID: {event.trade_id}")

  return "\n".join(lines)


def format_open_trade_events(events: list[TradeLogEvent]) -> str:
  if not events:
    return "No open trades in trade log."

  formatted_events = [
    format_open_trade_event(event)
    for event in events
  ]

  return "\n\n".join(formatted_events)