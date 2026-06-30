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
  preferred_exchange: str = "SMART",
  multiplier: str = "100",
) -> IBKROptionChainParameters:
  """
  Velger én option chain parameter-sett fra IBKR-resultatene.

  Default:
  - SMART exchange
  - multiplier 100
  """
  if not parameters:
    raise ValueError("parameters cannot be empty.")

  preferred_exchange = preferred_exchange.strip().upper()

  for item in parameters:
    if item.exchange == preferred_exchange and item.multiplier == multiplier:
      return item

  raise ValueError(
    f"No option chain parameters found for exchange={preferred_exchange}, "
    f"multiplier={multiplier}."
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