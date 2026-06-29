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