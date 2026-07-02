from datetime import datetime, timedelta, timezone

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

def parse_event_timestamp(timestamp) -> datetime | None:
  if isinstance(timestamp, datetime):
    return timestamp

  if not isinstance(timestamp, str):
    return None

  normalized_timestamp = timestamp.replace("Z", "+00:00")

  try:
    parsed_timestamp = datetime.fromisoformat(normalized_timestamp)
  except ValueError:
    return None

  if parsed_timestamp.tzinfo is None:
    return parsed_timestamp.replace(tzinfo=timezone.utc)

  return parsed_timestamp


def filter_trade_events_since(
  events: list[TradeLogEvent],
  days: int,
  now: datetime | None = None,
) -> list[TradeLogEvent]:
  if days <= 0:
    raise ValueError("days must be positive.")

  current_time = now or datetime.now(timezone.utc)
  cutoff = current_time - timedelta(days=days)

  filtered_events = []

  for event in events:
    timestamp = parse_event_timestamp(event.timestamp)

    if timestamp is None:
      continue

    if timestamp >= cutoff:
      filtered_events.append(event)

  return filtered_events


def format_trade_log_event(event: TradeLogEvent) -> str:
  lines = [
    f"{event.symbol} {event.event_type}",
    f"Trade ID: {event.trade_id}",
  ]

  quantity = parse_int(event.data.get("quantity"))

  if quantity is not None:
    lines.append(f"Qty: {quantity}")

  entry_limit_debit = parse_float(event.data.get("entry_limit_debit"))

  if entry_limit_debit is not None:
    lines.append(f"Entry debit quote: {format_usd(entry_limit_debit)}")

  exit_limit_credit = parse_float(event.data.get("exit_limit_credit"))

  if exit_limit_credit is not None:
    lines.append(f"Exit credit quote: {format_usd(exit_limit_credit)}")

  confirmation_source = event.data.get("confirmation_source")

  if confirmation_source is not None:
    lines.append(f"Confirmed by: {confirmation_source}")

  return "\n".join(lines)


def format_trade_log_events(
  events: list[TradeLogEvent],
  days: int,
) -> str:
  if not events:
    return f"No trade log events in the last {days} day(s)."

  formatted_events = [
    format_trade_log_event(event)
    for event in events
  ]

  return "\n\n".join(formatted_events)