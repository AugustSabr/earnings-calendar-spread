def calculate_iv30_rv30(
  term_structure,
  realized_volatility_30: float,
) -> float:
  """
  Beregner forholdet mellom 30-dagers implied volatility og 30-dagers realized volatility.
  """
  if realized_volatility_30 <= 0:
    raise ValueError("realized_volatility_30 must be greater than zero.")

  return term_structure(30) / realized_volatility_30

def calculate_average_volume(
  price_history,
  window: int = 30,
) -> float:
  """
  Beregner gjennomsnittlig volum over siste window-perioder.
  """
  average_volume = (
    price_history["Volume"]
    .rolling(window)
    .mean()
    .dropna()
  )

  if average_volume.empty:
    raise ValueError("Not enough volume data.")

  return average_volume.iloc[-1]

def passes_average_volume_filter(
  average_volume: float,
  minimum_volume: int = 1_500_000,
) -> bool:
  """
  Returnerer True hvis gjennomsnittlig volum er høyt nok.
  """
  return average_volume >= minimum_volume