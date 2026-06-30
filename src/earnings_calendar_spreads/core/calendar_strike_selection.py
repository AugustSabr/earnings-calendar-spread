def select_atm_strike(
  strikes: list[float],
  underlying_price: float,
) -> float:
  """
  Velger strike nærmest underliggende pris.
  """
  if not strikes:
    raise ValueError("strikes cannot be empty.")

  if underlying_price <= 0:
    raise ValueError("underlying_price must be greater than zero.")

  return float(
    min(
      strikes,
      key=lambda strike: abs(float(strike) - underlying_price),
    )
  )

def select_common_atm_strike(
  short_strikes: list[float],
  long_strikes: list[float],
  underlying_price: float,
) -> float:
  """
  Velger ATM strike som finnes for både short og long expiration.
  """
  common_strikes = sorted(
    set(float(strike) for strike in short_strikes)
    & set(float(strike) for strike in long_strikes)
  )

  if not common_strikes:
    raise ValueError("No common strikes found.")

  return select_atm_strike(
    strikes=common_strikes,
    underlying_price=underlying_price,
  )