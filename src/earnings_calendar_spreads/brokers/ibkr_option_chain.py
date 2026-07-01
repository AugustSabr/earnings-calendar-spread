from dataclasses import dataclass


@dataclass(frozen=True)
class IBKROptionChainParameters:
  """
  Option chain metadata fra IBKR.

  Inneholder mulige expirations og strikes for en underliggende aksje.
  """
  exchange: str
  underlying_con_id: int
  trading_class: str
  multiplier: str
  expirations: list[str]
  strikes: list[float]

def select_option_chain_parameters(
  parameters: list[IBKROptionChainParameters],
  underlying_symbol: str | None = None,
  preferred_exchange: str = "SMART",
  multiplier: str = "100",
) -> IBKROptionChainParameters:
  """
  Velger standard SMART option chain.

  Krever:
    exchange == SMART
    multiplier == 100

  Hvis underlying_symbol er gitt, krever vi også:
    trading_class == underlying_symbol

  Dette unngår adjusted chains som f.eks. 2MSFT.
  """
  smart_matches = [
    parameter
    for parameter in parameters
    if parameter.exchange == preferred_exchange
    and str(parameter.multiplier) == multiplier
  ]

  if not smart_matches:
    raise ValueError(
      f"No IBKR option chain parameters found for "
      f"exchange={preferred_exchange} multiplier={multiplier}."
    )

  if underlying_symbol is None:
    return smart_matches[0]

  normalized_symbol = underlying_symbol.strip().upper()

  standard_matches = [
    parameter
    for parameter in smart_matches
    if parameter.trading_class == normalized_symbol
  ]

  if standard_matches:
    return standard_matches[0]

  available_trading_classes = sorted(
    {
      parameter.trading_class
      for parameter in smart_matches
    }
  )

  raise ValueError(
    f"No standard SMART option chain found for {normalized_symbol}. "
    f"Available trading classes: {available_trading_classes}"
  )

def ibkr_expiration_to_iso(expiration: str) -> str:
  """
  Konverterer IBKR expiration YYYYMMDD til ISO YYYY-MM-DD.
  """
  if len(expiration) != 8:
    raise ValueError("expiration must use YYYYMMDD format.")

  return f"{expiration[:4]}-{expiration[4:6]}-{expiration[6:]}"


def iso_expiration_to_ibkr(expiration: str) -> str:
  """
  Konverterer ISO expiration YYYY-MM-DD til IBKR YYYYMMDD.
  """
  if len(expiration) != 10:
    raise ValueError("expiration must use YYYY-MM-DD format.")

  return expiration.replace("-", "")