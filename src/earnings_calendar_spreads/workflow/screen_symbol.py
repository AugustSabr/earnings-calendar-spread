from datetime import date, datetime

from earnings_calendar_spreads.core.option_chain import (
  calculate_atm_iv_by_expiration,
  calculate_expected_move,
)
from earnings_calendar_spreads.core.option_expirations import filter_expiration_dates
from earnings_calendar_spreads.core.realized_volatility import (
  calculate_yang_zhang_volatility,
)
from earnings_calendar_spreads.core.screening import create_screening_result
from earnings_calendar_spreads.core.screening_metrics import (
  calculate_average_volume,
  calculate_iv30_rv30,
)
from earnings_calendar_spreads.core.term_structure import (
  build_term_structure,
  calculate_term_structure_slope,
)
from earnings_calendar_spreads.data.yfinance_client import (
  get_current_price,
  get_option_chains,
  get_option_expiration_dates,
  get_price_history,
)


def screen_symbol(symbol: str, today: date):
  """
  Screener ett symbol

  Returnerer ScreeningResult hvis symbol kan vurderes.
  Kaster ValueError hvis nødvendig data mangler.
  """
  symbol = symbol.strip().upper()

  expiration_dates = get_option_expiration_dates(symbol)
  filtered_expirations = filter_expiration_dates(
    expiration_dates=expiration_dates,
    today=today,
  )

  option_chains = get_option_chains(
    symbol=symbol,
    expiration_dates=filtered_expirations,
  )

  underlying_price = get_current_price(symbol)

  atm_iv_by_expiration = calculate_atm_iv_by_expiration(
    option_chains=option_chains,
    underlying_price=underlying_price,
  )

  if not atm_iv_by_expiration:
    raise ValueError(f"Could not determine ATM IV for {symbol}.")

  dtes = []
  ivs = []

  for expiration_date, atm_iv in atm_iv_by_expiration.items():
    expiration = datetime.strptime(expiration_date, "%Y-%m-%d").date()
    dtes.append((expiration - today).days)
    ivs.append(atm_iv)

  term_structure = build_term_structure(
    days=dtes,
    ivs=ivs,
  )

  term_structure_slope = calculate_term_structure_slope(
    term_structure=term_structure,
    first_dte=dtes[0],
    target_dte=45,
  )

  price_history = get_price_history(symbol, period="3mo")

  realized_volatility_30 = calculate_yang_zhang_volatility(price_history)

  iv30_rv30 = calculate_iv30_rv30(
    term_structure=term_structure,
    realized_volatility_30=realized_volatility_30,
  )

  average_volume = calculate_average_volume(price_history)

  first_expiration = next(iter(atm_iv_by_expiration.keys()))
  first_chain = option_chains[first_expiration]

  expected_move = calculate_expected_move(
    calls=first_chain["calls"],
    puts=first_chain["puts"],
    underlying_price=underlying_price,
  )

  return create_screening_result(
    symbol=symbol,
    average_volume=average_volume,
    iv30_rv30=iv30_rv30,
    term_structure_slope=term_structure_slope,
    expected_move=expected_move,
  )