def find_nearest_strike_option(
  options: list[dict],
  underlying_price: float,
) -> dict:
  """
  Finner option-kontrakten med strike nærmest underliggende aksjepris.
  """
  if not options:
    raise ValueError("No options provided.")

  return min(
    options,
    key=lambda option: abs(option["strike"] - underlying_price),
  )

def calculate_atm_iv(
  calls: list[dict],
  puts: list[dict],
  underlying_price: float,
) -> float:
  """
  Beregner ATM implied volatility som snittet av nærmeste call-IV og put-IV.
  """
  nearest_call = find_nearest_strike_option(
    options=calls,
    underlying_price=underlying_price,
  )

  nearest_put = find_nearest_strike_option(
    options=puts,
    underlying_price=underlying_price,
  )

  return (
    nearest_call["impliedVolatility"]
    + nearest_put["impliedVolatility"]
  ) / 2.0