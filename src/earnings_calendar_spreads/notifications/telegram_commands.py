def parse_telegram_command(text: str) -> str:
  """
  Extracts the command part from a Telegram message.

  Supports:
    /ping
    /positions
  """
  first_word = text.strip().split()[0].lower()

  return first_word.split("@")[0]


def handle_telegram_command(text: str) -> str:
  command = parse_telegram_command(text)

  if command == "/ping":
    return "pong"

  if command == "/positions":
    return "Positions command is not connected to IBKR yet."

  return "Unknown command."