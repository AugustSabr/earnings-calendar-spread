import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_TRADE_LOG_PATH = Path("runtime/trade_log.jsonl")


@dataclass(frozen=True)
class TradeLogEvent:
  timestamp: str
  event_type: str
  trade_id: str
  symbol: str
  data: dict[str, Any]


def utc_now_iso() -> str:
  return datetime.now(timezone.utc).isoformat()


def make_calendar_trade_id(
  symbol: str,
  short_expiration: str,
  long_expiration: str,
  strike: float,
  right: str,
) -> str:
  return "|".join(
    [
      symbol.strip().upper(),
      short_expiration,
      long_expiration,
      str(float(strike)),
      right.strip().upper(),
    ]
  )


def make_trade_log_event(
  event_type: str,
  trade_id: str,
  symbol: str,
  data: dict[str, Any],
  timestamp: str | None = None,
) -> TradeLogEvent:
  return TradeLogEvent(
    timestamp=timestamp or utc_now_iso(),
    event_type=event_type,
    trade_id=trade_id,
    symbol=symbol.strip().upper(),
    data=data,
  )


def append_trade_log_event(
  event: TradeLogEvent,
  path: Path = DEFAULT_TRADE_LOG_PATH,
) -> None:
  path.parent.mkdir(
    parents=True,
    exist_ok=True,
  )

  with path.open("a", encoding="utf-8") as file:
    file.write(json.dumps(asdict(event), sort_keys=True))
    file.write("\n")


def read_trade_log_events(
  path: Path = DEFAULT_TRADE_LOG_PATH,
) -> list[TradeLogEvent]:
  if not path.exists():
    return []

  events = []

  with path.open("r", encoding="utf-8") as file:
    for line in file:
      line = line.strip()

      if not line:
        continue

      raw_event = json.loads(line)

      events.append(
        TradeLogEvent(
          timestamp=raw_event["timestamp"],
          event_type=raw_event["event_type"],
          trade_id=raw_event["trade_id"],
          symbol=raw_event["symbol"],
          data=raw_event["data"],
        )
      )

  return events


def get_open_trade_ids(
  events: list[TradeLogEvent],
) -> set[str]:
  open_trade_ids = set()

  for event in events:
    if event.event_type == "calendar_opened":
      open_trade_ids.add(event.trade_id)

    if event.event_type == "calendar_closed":
      open_trade_ids.discard(event.trade_id)

  return open_trade_ids


def get_open_trade_events(
  events: list[TradeLogEvent],
) -> list[TradeLogEvent]:
  open_trade_ids = get_open_trade_ids(events)

  return [
    event
    for event in events
    if event.event_type == "calendar_opened"
    and event.trade_id in open_trade_ids
  ]