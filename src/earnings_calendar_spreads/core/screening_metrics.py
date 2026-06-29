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