import os
import threading

from dotenv import load_dotenv

from earnings_calendar_spreads.brokers.ibkr_calendar_positions import (
  find_calendar_spread_positions,
)
from earnings_calendar_spreads.brokers.ibkr_client import IBKRClient
from earnings_calendar_spreads.notifications.telegram import (
  TelegramConfig,
  get_telegram_updates,
  send_telegram_message,
)
from earnings_calendar_spreads.notifications.telegram_positions import (
  format_calendar_spread_positions,
)
from earnings_calendar_spreads.storage.trade_log import (
  get_open_trade_events,
  read_trade_log_events,
)
from earnings_calendar_spreads.notifications.telegram_trades import (
  filter_trade_events_since,
  format_trade_log_events,
)

def get_required_env(name: str) -> str:
  value = os.getenv(name)

  if not value:
    raise ValueError(f"Missing {name} in .env")

  return value

def get_positions_message() -> str:
  host = os.getenv("IBKR_HOST", "127.0.0.1")
  port = int(os.getenv("IBKR_PORT", "7497"))
  client_id = int(os.getenv("IBKR_CLIENT_ID", "180"))

  client = IBKRClient()

  try:
    client.connect_and_start(
      host=host,
      port=port,
      client_id=client_id,
    )

    positions = client.get_positions()
    spreads = find_calendar_spread_positions(positions)

    return format_calendar_spread_positions(spreads)

  finally:
    client.disconnect_and_wait()

def handle_command(text: str) -> str | None:
  command = text.strip().lower()

  if command == "/positions":
    return get_positions_message()

  if command.startswith("/log"):
    return get_log_message(command)

  return None


def wait_for_exit(stop_event: threading.Event):
  while not stop_event.is_set():
    command = input().strip().lower()

    if command in {"q", "quit", "exit"}:
      stop_event.set()
      return

def get_trades_message() -> str:
  try:
    events = read_trade_log_events()
  except FileNotFoundError:
    events = []

  open_trade_events = get_open_trade_events(events)

  return format_open_trade_events(open_trade_events)

def parse_log_days(command: str) -> int:
  parts = command.split()

  if len(parts) == 1:
    return 1

  if len(parts) != 2:
    raise ValueError("Usage: /log [days]")

  days = int(parts[1])

  if days <= 0:
    raise ValueError("days must be positive.")

  return days

def get_log_message(command: str) -> str:
  try:
    days = parse_log_days(command)
  except ValueError:
    return "Usage: /log [days]"

  try:
    events = read_trade_log_events()
  except FileNotFoundError:
    events = []

  recent_events = filter_trade_events_since(
    events=events,
    days=days,
  )

  return format_trade_log_events(
    events=recent_events,
    days=days,
  )

def main():
  load_dotenv()

  telegram_config = TelegramConfig(
    bot_token=get_required_env("TELEGRAM_BOT_TOKEN"),
    chat_id=get_required_env("TELEGRAM_CHAT_ID"),
  )

  offset = None
  stop_event = threading.Event()

  threading.Thread(
    target=wait_for_exit,
    args=(stop_event,),
    daemon=True,
  ).start()

  print("Telegram bot is running.")
  print("Type q, quit, or exit and press Enter to stop.")

  try:
    while not stop_event.is_set():
      updates = get_telegram_updates(
        config=telegram_config,
        offset=offset,
        timeout_seconds=2,
      )

      for update in updates:
        offset = update["update_id"] + 1

        message = update.get("message", {})
        chat = message.get("chat", {})
        chat_id = str(chat.get("id"))
        text = message.get("text", "")

        if chat_id != telegram_config.chat_id:
          continue

        response = handle_command(text=text)

        if response is None:
          continue

        send_telegram_message(
          config=telegram_config,
          text=response,
        )

  except KeyboardInterrupt:
    stop_event.set()

  finally:
    print("Stopping Telegram bot...")
    print("Stopped.")


if __name__ == "__main__":
  main()