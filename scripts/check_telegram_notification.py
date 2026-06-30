import os
from datetime import datetime

from dotenv import load_dotenv

from earnings_calendar_spreads.notifications.telegram import (
  TelegramConfig,
  send_telegram_message,
)

def main():
  load_dotenv()

  bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
  chat_id = os.getenv("TELEGRAM_CHAT_ID")

  if not bot_token or not chat_id:
    print("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID in .env")
    return

  config = TelegramConfig(
    bot_token=bot_token,
    chat_id=chat_id,
  )

  send_telegram_message(
    config=config,
    text=f"Earnings calendar spread bot test: {datetime.now()}",
  )

  print("Telegram test message sent.")


if __name__ == "__main__":
  main()