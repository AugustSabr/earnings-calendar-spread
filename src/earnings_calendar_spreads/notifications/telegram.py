import json
import urllib.error
import urllib.request
from dataclasses import dataclass

@dataclass(frozen=True)
class TelegramConfig:
  bot_token: str
  chat_id: str

class TelegramError(RuntimeError):
  pass

def build_telegram_send_message_url(bot_token: str) -> str:
  return f"https://api.telegram.org/bot{bot_token}/sendMessage"

def build_telegram_send_message_payload(
  chat_id: str,
  text: str,
) -> dict[str, str]:
  return {
    "chat_id": chat_id,
    "text": text,
  }

def send_telegram_message(
  config: TelegramConfig,
  text: str,
  timeout_seconds: int = 10,
) -> dict:
  url = build_telegram_send_message_url(config.bot_token)

  payload = build_telegram_send_message_payload(
    chat_id=config.chat_id,
    text=text,
  )

  request = urllib.request.Request(
    url=url,
    data=json.dumps(payload).encode("utf-8"),
    headers={
      "Content-Type": "application/json",
    },
    method="POST",
  )

  try:
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
      response_body = response.read().decode("utf-8")

  except urllib.error.HTTPError as error:
    body = error.read().decode("utf-8")
    raise TelegramError(f"Telegram HTTP error: {body}") from error

  except urllib.error.URLError as error:
    raise TelegramError(f"Telegram connection error: {error}") from error

  data = json.loads(response_body)

  if not data.get("ok"):
    raise TelegramError(f"Telegram API error: {data}")

  return data

def build_telegram_get_updates_url(bot_token: str) -> str:
  return f"https://api.telegram.org/bot{bot_token}/getUpdates"


def get_telegram_updates(
  config: TelegramConfig,
  offset: int | None = None,
  timeout_seconds: int = 30,
) -> list[dict]:
  url = build_telegram_get_updates_url(config.bot_token)

  payload = {
    "timeout": timeout_seconds,
  }

  if offset is not None:
    payload["offset"] = offset

  request = urllib.request.Request(
    url=url,
    data=json.dumps(payload).encode("utf-8"),
    headers={
      "Content-Type": "application/json",
    },
    method="POST",
  )

  try:
    with urllib.request.urlopen(
      request,
      timeout=timeout_seconds + 5,
    ) as response:
      response_body = response.read().decode("utf-8")

  except urllib.error.HTTPError as error:
    body = error.read().decode("utf-8")
    raise TelegramError(f"Telegram HTTP error: {body}") from error

  except urllib.error.URLError as error:
    raise TelegramError(f"Telegram connection error: {error}") from error

  data = json.loads(response_body)

  if not data.get("ok"):
    raise TelegramError(f"Telegram API error: {data}")

  return data["result"]