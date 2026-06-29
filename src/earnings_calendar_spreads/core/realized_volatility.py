import numpy as np


def calculate_yang_zhang_volatility(
  price_data,
  window: int = 30,
  trading_periods: int = 252,
  return_last_only: bool = True,
):
  """
  Beregner Yang-Zhang realized volatility.

  Forventer price_data med kolonnene:
  Open, High, Low, Close.
  """
  log_ho = np.log(price_data["High"] / price_data["Open"])
  log_lo = np.log(price_data["Low"] / price_data["Open"])
  log_co = np.log(price_data["Close"] / price_data["Open"])

  log_oc = np.log(price_data["Open"] / price_data["Close"].shift(1))
  log_oc_sq = log_oc**2

  log_cc = np.log(price_data["Close"] / price_data["Close"].shift(1))
  log_cc_sq = log_cc**2

  rs = (
    log_ho * (log_ho - log_co)
    + log_lo * (log_lo - log_co)
  )

  close_vol = (
    log_cc_sq
    .rolling(window=window, center=False)
    .sum()
    * (1.0 / (window - 1.0))
  )

  open_vol = (
    log_oc_sq
    .rolling(window=window, center=False)
    .sum()
    * (1.0 / (window - 1.0))
  )

  window_rs = (
    rs
    .rolling(window=window, center=False)
    .sum()
    * (1.0 / (window - 1.0))
  )

  k = 0.34 / (
    1.34
    + ((window + 1) / (window - 1))
  )

  result = (
    open_vol
    + k * close_vol
    + (1 - k) * window_rs
  ).apply(np.sqrt) * np.sqrt(trading_periods)

  if return_last_only:
    return result.iloc[-1]

  return result.dropna()