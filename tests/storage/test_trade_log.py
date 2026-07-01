from earnings_calendar_spreads.storage.trade_log import (
  append_trade_log_event,
  get_open_trade_events,
  get_open_trade_ids,
  make_calendar_trade_id,
  make_trade_log_event,
  read_trade_log_events,
)


def test_append_and_read_trade_log_event(tmp_path):
  path = tmp_path / "trade_log.jsonl"

  trade_id = make_calendar_trade_id(
    symbol="aapl",
    short_expiration="2026-07-02",
    long_expiration="2026-08-21",
    strike=295,
    right="c",
  )

  event = make_trade_log_event(
    event_type="calendar_opened",
    trade_id=trade_id,
    symbol="aapl",
    data={
      "net_debit": 11.07,
      "quantity": 1,
    },
    timestamp="2026-07-01T19:45:00+00:00",
    event_id="event-1",
  )

  append_trade_log_event(
    event=event,
    path=path,
  )

  events = read_trade_log_events(path)

  assert events == [event]


def test_get_open_trade_ids_removes_closed_trades():
  trade_id = make_calendar_trade_id(
    symbol="AAPL",
    short_expiration="2026-07-02",
    long_expiration="2026-08-21",
    strike=295,
    right="C",
  )

  opened = make_trade_log_event(
    event_type="calendar_opened",
    trade_id=trade_id,
    symbol="AAPL",
    data={},
    event_id="open-event",
  )

  closed = make_trade_log_event(
    event_type="calendar_closed",
    trade_id=trade_id,
    symbol="AAPL",
    data={},
    event_id="close-event",
  )

  assert get_open_trade_ids([opened]) == {trade_id}
  assert get_open_trade_ids([opened, closed]) == set()


def test_get_open_trade_events_returns_open_events():
  open_trade_id = make_calendar_trade_id(
    symbol="AAPL",
    short_expiration="2026-07-02",
    long_expiration="2026-08-21",
    strike=295,
    right="C",
  )

  closed_trade_id = make_calendar_trade_id(
    symbol="MSFT",
    short_expiration="2026-07-02",
    long_expiration="2026-08-21",
    strike=390,
    right="C",
  )

  open_event = make_trade_log_event(
    event_type="calendar_opened",
    trade_id=open_trade_id,
    symbol="AAPL",
    data={},
    event_id="aapl-open",
  )

  closed_open_event = make_trade_log_event(
    event_type="calendar_opened",
    trade_id=closed_trade_id,
    symbol="MSFT",
    data={},
    event_id="msft-open",
  )

  closed_event = make_trade_log_event(
    event_type="calendar_closed",
    trade_id=closed_trade_id,
    symbol="MSFT",
    data={},
    event_id="msft-close",
  )

  assert get_open_trade_events(
    [
      open_event,
      closed_open_event,
      closed_event,
    ]
  ) == [open_event]