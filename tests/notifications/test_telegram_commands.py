from earnings_calendar_spreads.notifications.telegram_commands import (
  handle_telegram_command,
  parse_telegram_command,
)


def test_parse_telegram_command():
  assert parse_telegram_command("/ping") == "/ping"


def test_parse_telegram_command_with_bot_name():
  assert parse_telegram_command("/ping@MyTradingBot") == "/ping"


def test_handle_ping_command():
  assert handle_telegram_command("/ping") == "pong"


def test_handle_ping_command_with_extra_text():
  assert handle_telegram_command("/ping please") == "pong"


def test_handle_positions_placeholder():
  assert (
    handle_telegram_command("/positions")
    == "Positions command is not connected to IBKR yet."
  )


def test_handle_unknown_command():
  assert handle_telegram_command("/help") == "Unknown command."