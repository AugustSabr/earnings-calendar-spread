from dataclasses import dataclass
from decimal import Decimal
import time

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

def get_positions_with_retry(
  client,
  attempts: int = 3,
  delay_seconds: float = 1.0,
):
  if attempts <= 0:
    raise ValueError("attempts must be positive.")

  if delay_seconds < 0:
    raise ValueError("delay_seconds must be >= 0.")

  last_error = None

  for attempt_index in range(attempts):
    try:
      return client.get_positions()
    except TimeoutError as error:
      last_error = error

      if attempt_index == attempts - 1:
        raise

      if delay_seconds > 0:
        time.sleep(delay_seconds)

  raise last_error