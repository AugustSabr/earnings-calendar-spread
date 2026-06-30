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