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

def get_price_history(
  symbol: str,
  period: str = "3mo",
):
  """
  Henter historiske prisdata fra yfinance.
  """
  ticker = yf.Ticker(symbol)
  history = ticker.history(period=period)

  if history.empty:
    raise ValueError(f"No price history found for {symbol}.")

  return history

def get_option_chain(
  symbol: str,
  expiration_date: str,
) -> dict[str, list[dict]]:
  """
  Henter option chain for én expiration fra yfinance.

  Returnerer calls og puts som lister med dictionaries.
  """
  ticker = yf.Ticker(symbol)
  chain = ticker.option_chain(expiration_date)

  return {
    "calls": chain.calls.to_dict("records"),
    "puts": chain.puts.to_dict("records"),
  }

def get_option_chains(
  symbol: str,
  expiration_dates: list[str],
) -> dict[str, dict[str, list[dict]]]:
  """
  Henter option chains for flere expirations fra yfinance.
  """
  option_chains = {}

  for expiration_date in expiration_dates:
    option_chains[expiration_date] = get_option_chain(
      symbol=symbol,
      expiration_date=expiration_date,
    )

  return option_chains