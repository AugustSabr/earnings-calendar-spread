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