from earnings_calendar_spreads.core.symbols import is_standard_us_symbol

def filter_standard_symbols(symbols: list[str]) -> list[str]:
  """
  Returnerer en liste med gyldige symboler, normalisert til store bokstaver.
  """
  valid_symbols = []

  for symbol in symbols:
    if is_standard_us_symbol(symbol):
      valid_symbols.append(symbol.strip().upper())

  return valid_symbols