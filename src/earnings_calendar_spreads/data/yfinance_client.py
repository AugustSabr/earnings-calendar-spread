import yfinance as yf

def get_current_price(symbol: str) -> float:
  """
  Henter siste close-pris for et symbol fra yfinance.
  """
  ticker = yf.Ticker(symbol)
  history = ticker.history(period="1d")

  if history.empty:
    raise ValueError(f"No price data found for {symbol}.")

  return float(history["Close"].iloc[-1])

def get_option_expiration_dates(symbol: str) -> list[str]:
  """
  Henter tilgjengelige option expiration-datoer fra yfinance.
  """
  ticker = yf.Ticker(symbol)
  expirations = list(ticker.options)

  if not expirations:
    raise ValueError(f"No option expirations found for {symbol}.")

  return expirations