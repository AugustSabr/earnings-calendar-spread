import numpy as np
from scipy.interpolate import interp1d


def build_term_structure(
  days: list[int],
  ivs: list[float],
):
  """
  Lager en term structure-funksjon for implied volatility.
  - bruker scipy.interp1d med lineær interpolering
  - bruker første IV for DTE under laveste kjente DTE
  - bruker siste IV for DTE over høyeste kjente DTE
  """
  if len(days) != len(ivs):
    raise ValueError("days and ivs must have the same length.")

  if not days:
    raise ValueError("At least one expiration is required.")

  days_array = np.array(days)
  ivs_array = np.array(ivs)

  sort_index = days_array.argsort()
  days_array = days_array[sort_index]
  ivs_array = ivs_array[sort_index]

  spline = interp1d(
    days_array,
    ivs_array,
    kind="linear",
    fill_value="extrapolate",
  )

  def estimate_iv(dte: int) -> float:
    if dte < days_array[0]:
      return ivs_array[0]

    if dte > days_array[-1]:
      return ivs_array[-1]

    return float(spline(dte))

  return estimate_iv