from dataclasses import dataclass
from decimal import Decimal

from ibapi.contract import Contract


@dataclass(frozen=True)
class IBKRPosition:
  """
  Én posisjon fra IBKR.
  """
  account: str
  contract: Contract
  position: Decimal
  average_cost: float