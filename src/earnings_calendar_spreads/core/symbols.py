def is_standard_us_symbol(symbol: str) -> bool:
  """
  Returnerer True hvis symbolet ser ut som et vanlig US aksjesymbol.
  """
  cleaned = symbol.strip().upper()

  if not cleaned:
    return False

  if len(cleaned) > 5:
    return False

  if any(char in cleaned for char in [".", "-", "/"]):
    return False

  return True