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

def calculate_atm_iv_by_expiration(
  option_chains: dict[str, dict[str, list[dict]]],
  underlying_price: float,
) -> dict[str, float]:
  """
  Beregner ATM implied volatility for hver expiration.

  Forventer option_chains på formatet:
  {
    "2026-07-03": {
      "calls": [...],
      "puts": [...]
    }
  }
  """
  atm_iv_by_expiration = {}

  for expiration_date, chain in option_chains.items():
    calls = chain.get("calls", [])
    puts = chain.get("puts", [])

    if not calls or not puts:
      continue

    atm_iv_by_expiration[expiration_date] = calculate_atm_iv(
      calls=calls,
      puts=puts,
      underlying_price=underlying_price,
    )

  return atm_iv_by_expiration

def calculate_mid_price(option: dict) -> float | None:
  """
  Beregner mid price fra bid og ask.
  - hvis bid eller ask mangler/er 0, returneres None.
  """
  bid = option.get("bid")
  ask = option.get("ask")

  if not bid or not ask:
    return None

  return (bid + ask) / 2.0

def calculate_expected_move(
  calls: list[dict],
  puts: list[dict],
  underlying_price: float,
) -> str | None:
  """
  Beregner expected move fra ATM straddle som prosent av underliggende pris.
  """
  nearest_call = find_nearest_strike_option(
    options=calls,
    underlying_price=underlying_price,
  )

  nearest_put = find_nearest_strike_option(
    options=puts,
    underlying_price=underlying_price,
  )

  call_mid = calculate_mid_price(nearest_call)
  put_mid = calculate_mid_price(nearest_put)

  if not call_mid or not put_mid:
    return None

  straddle_price = call_mid + put_mid
  expected_move = round(straddle_price / underlying_price * 100, 2)

  return f"{expected_move}%"