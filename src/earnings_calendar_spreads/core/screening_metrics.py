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

def passes_iv30_rv30_filter(
  iv30_rv30: float,
  minimum_ratio: float = 1.25,
) -> bool:
  """
  Returnerer True hvis IV/RV-forholdet er høyt nok.
  """
  return iv30_rv30 >= minimum_ratio

def passes_term_structure_slope_filter(
  term_structure_slope: float,
  maximum_slope: float = -0.00406,
) -> bool:
  """
  Returnerer True hvis term structure slope er lav nok.

  Bevarer gammel calculator_new.py-logikk:
  ts_slope_0_45 <= -0.00406
  """
  return term_structure_slope <= maximum_slope

def passes_all_screening_filters(
  average_volume: float,
  iv30_rv30: float,
  term_structure_slope: float,
) -> bool:
  """
  Returnerer True hvis alle gamle screening-regler passerer.
  """
  return (
    passes_average_volume_filter(average_volume)
    and passes_iv30_rv30_filter(iv30_rv30)
    and passes_term_structure_slope_filter(term_structure_slope)
  )