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
from earnings_calendar_spreads.notifications.telegram_trades import (
  format_open_trade_events,
)
from earnings_calendar_spreads.storage.trade_log import (
  get_open_trade_events,
  read_trade_log_events,
)


def get_required_env(name: str) -> str:
  value = os.getenv(name)

  if not value:
    raise ValueError(f"Missing {name} in .env")

  return value


def get_positions_message(client: IBKRClient) -> str:
  positions = client.get_positions()
  spreads = find_calendar_spread_positions(positions)

  return format_calendar_spread_positions(spreads)


def handle_command(
  text: str,
  client: IBKRClient,
) -> str | None:
  command = text.strip().lower()

  if command == "/positions":
    return get_positions_message(client)

  if command == "/trades":
    return get_trades_message()

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

def main():
  load_dotenv()

  telegram_config = TelegramConfig(
    bot_token=get_required_env("TELEGRAM_BOT_TOKEN"),
    chat_id=get_required_env("TELEGRAM_CHAT_ID"),
  )

  host = os.getenv("IBKR_HOST", "127.0.0.1")
  port = int(os.getenv("IBKR_PORT", "7497"))
  client_id = int(os.getenv("IBKR_CLIENT_ID", "180"))

  ibkr_client = IBKRClient()
  offset = None
  stop_event = threading.Event()

  ibkr_client.connect_and_start(
    host=host,
    port=port,
    client_id=client_id,
  )

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

        response = handle_command(
          text=text,
          client=ibkr_client,
        )

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
    ibkr_client.disconnect_and_wait()
    print("Stopped.")


if __name__ == "__main__":
  main()