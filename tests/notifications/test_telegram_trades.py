from earnings_calendar_spreads.notifications.telegram_trades import (
  format_open_trade_events,
)
from earnings_calendar_spreads.storage.trade_log import make_trade_log_event


def test_format_open_trade_events_empty():
  assert format_open_trade_events([]) == "No open trades in trade log."


def test_format_open_trade_events():
  event = make_trade_log_event(
    event_type="calendar_opened",
    trade_id="AAPL|2026-07-02|2026-08-21|295.0|C",
    symbol="AAPL",
    data={
      "quantity": 2,
      "entry_limit_debit": 10.5,
      "short_local_symbol": "AAPL  260702C00295000",
      "long_local_symbol": "AAPL  260821C00295000",
    },
  )

  message = format_open_trade_events([event])

  assert "AAPL calendar spread" in message
  assert "Qty: 2" in message
  assert "Entry debit quote: $10.50" in message
  assert "Estimated total debit: $2,100.00" in message
  assert "Short/front: AAPL  260702C00295000" in message
  assert "Long/back: AAPL  260821C00295000" in message